import argparse

from core.config import Config
from core.generate import Generator
from core.trans import TranslationManager

def parse_args():
    """Parses the command line arguments."""
    parser = argparse.ArgumentParser(description="QuickDot configuration")

    parser.add_argument("--use-threads", action='store_true', 
                        help="Whether to use threads for processing")
    parser.add_argument("--thread-count", type=int, default=None, 
                        help="The number of threads to use if --use-threads is specified")
    parser.add_argument("--gather-texts", action='store_true', 
                        help="Whether to gather texts for translation")
    parser.add_argument("--run-watcher", action='store_true', 
                        help="Whether to run a file watcher for live updates")
    parser.add_argument("--site-output-path", type=str, default=None, 
                        help="The path where the generated site will be output")
    parser.add_argument("--site-languages", type=str, nargs='+', default=None, 
                        help="The languages used on the site for internationalization")

    args = parser.parse_args()
    return args

def main():
    """Main entry point of the application."""
    config = Config(parse_args())
    trans = TranslationManager(config)

    if config.gather_texts:
        trans.gather_texts()
    else:
        gen = Generator(config, trans)


if __name__ == "__main__":
    main()
