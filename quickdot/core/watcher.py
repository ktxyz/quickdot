import time
import logging
import threading
import http.server
import socketserver
from pathlib import Path

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, PatternMatchingEventHandler

from quickdot.core.generate import Generator


def create_custom_handle(config):
    class QuickdotHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
        def translate_path(self, path):
            path = path.lstrip('/')
            return str(config.site_output_path / path)
    return QuickdotHTTPRequestHandler


class QuickdotHandler(PatternMatchingEventHandler):
    def __init__(self, config, generator):
        # Ignore everything that is in the .git directory or in the output directory
        ignore_patterns = [str(config.ROOT_PATH / '.git/**'), str(config.site_output_path / '**'), '*.buildinfo', '*.postinfo.json']
        ignore_patterns = [p.replace('\\\\', '/') for p in ignore_patterns]
        super().__init__(ignore_patterns=ignore_patterns)
        self.config = config
        self.generator = generator

    def on_modified(self, event):
        logging.info('File changed: %s', event.src_path)
        logging.info('Rebuilding site...')
        self.generator.regenerate()


class Watcher:
    def __init__(self, config, trans) -> None:
        self.config = config
        self.generator = Generator(self.config, trans)

        self.event_handler = QuickdotHandler(self.config, self.generator)

        self.observer = Observer()
        self.observer.schedule(self.event_handler, path=self.config.ROOT_PATH, recursive=True)

        Handler = create_custom_handle(self.config)
        self.httpd = socketserver.TCPServer(("localhost", self.config.live_server_port), Handler)

    def watch(self):
        # Run the HTTP server in a separate daemon thread
        httpd_thread = threading.Thread(target=self.httpd.serve_forever)
        httpd_thread.setDaemon(True)
        httpd_thread.start()
        logging.info(f'Started HTTP server at http://localhost:{self.config.live_server_port}')

        self.observer.start()
        logging.info('Started observer')

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

