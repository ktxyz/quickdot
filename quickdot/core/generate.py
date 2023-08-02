import os
import json
import shutil
import logging
import traceback
from enum import Enum
from pathlib import Path
from datetime import date as datetime_date
from concurrent.futures import ThreadPoolExecutor

from jinja2 import Environment, FileSystemLoader
from babel import Locale
from babel.dates import format_date


class ElementType(Enum):
    PAGE = 0
    POST = 1

class Element:
    def __init__(self, type, name):
        self.type = type
        self.name = name
        self.is_active = False
    
    def toggle_active(self):
        self.is_active = not self.is_active
    
    def get_url(self, lang):
        return f'/{lang}/{"posts" if self.type == ElementType.POST else "pages"}/{self.name}.html'

    def __str__(self):
        return f'<Element type={self.type} name={self.name} is_active={self.is_active}>'

class PageElement(Element):
    def __init__(self, name):
        super().__init__(ElementType.PAGE, name)

class PostElement(Element):
    def __init__(self, name, date):
        super().__init__(ElementType.POST, name)
        self.date = date

class SiteMap:
    def __init__(self):
        self.elements = {}
    
    def add_element(self, element):
        self.elements[element.name] = element

class Generator:
    def __init__(self, config, trans):
        self.logger = self._setup_logger()
        self.config = config
        self.trans = trans
        self.jinja_env = self._setup_jinja_env()

        self.site_map = SiteMap()
        self.context = {'_SITE_MAP': self.site_map, '_CONFIG': self.config}

        self._copy_static_files()

        self._gather_data()
        self._generate_site()

    def _setup_logger(self):
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        return logging.getLogger(__name__)

    def _setup_jinja_env(self):
        jinja_env = Environment(loader=FileSystemLoader(self.config.ROOT_PATH / 'templates'))

        def get_url_filter(element):
            return element.get_url(self.context['_LANG'])
        
        def get_element_filter(name):
            return self.site_map.elements[name]
        
        def get_element_lang_url(data):
            return self.site_map.elements[data['element'].name].get_url(data['lang'])
        
        def get_element_name(element):
            return self.trans.get_text(element.name, self.context['_LANG'])

        jinja_env.filters['get_url'] = get_url_filter
        jinja_env.filters['get_element'] = get_element_filter
        jinja_env.filters['get_element_name'] = get_element_name
        jinja_env.filters['get_element_lang_url'] = get_element_lang_url

        return jinja_env

    def _copy_static_files(self):
        shutil.copytree(self.config.site_static_path, self.config.site_output_path / "static", dirs_exist_ok=True)

    def _gather_data(self):
        self._gather_elements(ElementType.PAGE, self.config.site_pages)
        self._gather_elements(ElementType.POST, self.config.site_posts)

    def _gather_elements(self, type, elements):
        for name in elements:
            if type == ElementType.POST:
                site_map_element = self._create_post_element(name)
                print('added post element')
            else:
                site_map_element = PageElement(name)
            self.site_map.add_element(site_map_element)

    def _create_post_element(self, name):
        postinfo_path = self.config.ROOT_PATH / 'posts' / name / '.postinfo.json'
        if postinfo_path.exists():
            with open(postinfo_path, 'r+', encoding='utf-8') as f:
                postinfo = json.load(f)
            date = str(postinfo.get('date', datetime_date.today()))
        else:
            date = datetime_date.today()
            postinfo = {'date': str(date)}
        with open(postinfo_path, 'w+', encoding='utf-8') as f:
            json.dump(postinfo, f, indent=4)
        return PostElement(name, date)

    def _generate_site(self):
        os.makedirs(self.config.site_output_path, exist_ok=True)
        self._generate_pages()
        self._generate_posts()

    def _generate_pages(self):
        self._generate_elements(self.config.site_pages, self._generate_page)

    def _generate_posts(self):
        self._generate_elements(self.config.site_posts, self._generate_post)

    def _generate_elements(self, elements, generate_element_func):
        for lang in self.config.site_languages:
            self.context['_LANG'] = lang
            with ThreadPoolExecutor(max_workers=self.config.thread_count) as executor:
                for key, value in self.trans.locale[lang].items():
                    self.context[key] = value
                context = self.context.copy()
                context['_LANG'] = lang
                context['_DATE'] = format_date(datetime_date.today(), format='long', locale=Locale.parse(lang))
                for element in elements:
                    executor.submit(self._run_with_exception_logging, generate_element_func, context, element, lang)

    def _run_with_exception_logging(self, func, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except Exception as e:
            self.logger.error(f"Exception occurred during execution: {e}")
            self.logger.debug(traceback.format_exc())
            # If the exception needs to be propagated, re-raise it
            # raise

    def _generate_page(self, context, page, lang):
        self._generate_element(context, page, lang, 'pages')

    def _generate_post(self, context, post, lang):
        site_map_element = self.site_map.elements[post]
        date = datetime_date.fromisoformat(site_map_element.date)
        context['_DATE_CREATED'] = format_date(date, format='long', locale=Locale.parse(lang))
        self._generate_element(context, post, lang, 'posts')

    def _generate_element(self, context, element, lang, element_type):
        self.logger.info(f'Generating {element_type[:-1]} {element} for language {lang}.')
        element_file_path = Path(element_type) / element / f'{element_type[:-1]}.html'
        with open(element_file_path, 'r+', encoding='utf-8') as f:
            element_content = f.read()
        element_context_path = Path(element_type) / element / 'context.json'
        if element_context_path.exists() is False:
            element_context = {}
        else:
            with open(element_context_path, 'r+', encoding='utf-8') as f:
                element_context = json.load(f)
        context.update(element_context)

        site_map_element = self.site_map.elements[element]
        site_map_element.toggle_active()
        context['_ELEMENT'] = site_map_element
        template = self.jinja_env.from_string(element_content, context)
        rendered = template.render(context)
        site_map_element.toggle_active()

        element_url = self.config.site_output_path / lang / element_type / f'{element}.html'
        os.makedirs(element_url.parent, exist_ok=True)
        with open(element_url, '+w', encoding='utf-8') as f:
            f.write(rendered)
        if element == self.config.site_index_page and lang == self.config.site_languages[0]:
            self.logger.info(f'Generating index page...')
            index_url = self.config.site_output_path / 'index.html'
            with open(index_url, '+w', encoding='utf-8') as f:
                f.write(rendered)

        self.logger.info(f'Writing {element_type[:-1]} {element} for language {lang} to {element_url}.')
        self.logger.info(f'Generated {element_type[:-1]} {element} for language {lang}.')
