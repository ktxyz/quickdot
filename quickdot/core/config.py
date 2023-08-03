import os
import json
from pathlib import Path


class Config:
    # The root path of the project
    ROOT_PATH = Path(os.getcwd())

    """Class responsible for both generator config handling
    as well as sites config handling."""
    def __init__(self, args):
        self._load_config()
        self._load_site_config()

        self._handle_args(args)
        self._handle_build_number()

        if self.use_threads is False:
            self.thread_count = 1
        
    def _load_config(self):
        """"Loads the generator config file."""
        try:
            with open(self.ROOT_PATH / "config.json", "r") as f:
                config_data = json.load(f)

                # used for site generation
                self.use_threads = config_data["use_threads"]
                self.thread_count = config_data["thread_count"]

                self.gather_texts = False

                self.live_server_port = config_data["live_server_port"]
        except FileNotFoundError:
            print("No config file found.")
        except json.JSONDecodeError or KeyError:
            print("Invalid config file.")
        except Exception as e:
            print(e)
    
    def _load_site_config(self):
        """Loads the site config file."""
        try:
            with open(self.ROOT_PATH / "site.config.json", "r") as f:
                config_data = json.load(f)

                # used for site generation
                self.site_name = config_data["site_name"]
                self.site_url = config_data["site_url"]
                self.version = config_data["version"]
                self.site_description = config_data["site_description"]
                self.site_author = config_data["site_author"]
                self.site_keywords = config_data["site_keywords"]
                self.site_author_email = config_data["site_author_email"]

                self.site_index_page = config_data["site_index_page"]
                self.site_blog_page = config_data["site_blog_page"]
                self.site_pages = config_data["site_pages"]
                self.site_posts = config_data["site_posts"]
                self.site_static_path = config_data["site_static_path"]

                # relative to the site root
                self.site_output_path = self.ROOT_PATH / Path(config_data["site_output_path"])

                self.site_languages = config_data["site_languages"]
                self.site_translation_path = self.ROOT_PATH / Path(config_data["site_translation_path"])
        except FileNotFoundError:
            print("No config file found.")
        except json.JSONDecodeError or KeyError:
            print("Invalid config file.")
    
    def _handle_args(self, args):
        """Handles the command line arguments."""
        if args.use_threads is not None:
            self.use_threads = args.use_threads
        if args.thread_count is not None:
            self.thread_count = args.thread_count
        if args.gather_texts is not None:
            self.gather_texts = args.gather_texts
        if args.run_watcher is not None:
            self.run_watcher = args.run_watcher
        if args.site_output_path is not None:
            self.site_output_path = args.site_output_path
        if args.site_languages is not None:
            self.site_languages = args.site_languages
    
    def _handle_build_number(self):
        """Handles the build number."""
        try:
            with open(self.ROOT_PATH / ".buildinfo", "r+") as f:
                self.build_number, self.prev_version = map(int, f.read().strip().split(' '))
                f.write(f'{self.build_number + 1} {self.version}')
        except FileNotFoundError:
            self.build_number = 0
            self.prev_version = self.version
        except ValueError as e:
            self.build_number = 0
            self.prev_version = self.version
        finally:
            if self.version != self.prev_version:
                self.build_number = 0
            with open(self.ROOT_PATH / ".buildinfo", "w+") as f:
                f.write(f'{self.build_number + 1} {self.version}')
