# QuickDot

QuickDot is a lightweight, fast, and user-friendly static site generator with internationalization support. It's designed to make website creation simple and enjoyable, without sacrificing flexibility and customization.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Command Line Options](#command-line-options)
- [Project Structure](#project-structure)
  - [Pages](#pages)
  - [Posts](#posts)
  - [Static Files](#static-files)
  - [Configuration Files](#configuration-files)
- [Contexts](#contexts)
- [Internationalization](#internationalization)
- [Text Gathering](#text-gathering)
- [Contributing](#contributing)
- [License](#license)

## Features

- **Multithreaded Generation**: Utilize the power of multithreading for efficient site generation.
- **Internationalization Support**: Extend your reach with multiple language support.
- **Jinja2 Templating**: Enjoy the flexibility of Jinja2 for your HTML templates.
- **Flexible Configuration**: Command line or config file - you choose how to configure QuickDot.
- **Automatic Static Files Handling**: Hassle-free management of static files like images, stylesheets, and scripts.

## Installation

Install QuickDot with a single command:

```bash
pip install quickdot
```

## Usage

### Command Line Options

After installation, run QuickDot from the command line:

```bash
quickdot
```

Or, customize QuickDot's behavior with command line flags:

```bash
quickdot --use-threads --thread-count 4
```

Run `quickdot --help` to explore all available options.

## Project Structure

### Pages

Located in the `pages` directory, each page should have:

- `page.html`: HTML template.
- `context.json`: Context for the template.

### Posts

Located in the `posts` directory, each post should contain:

- `post.html`: HTML template.
- `context.json`: Context for the template.

### Static Files

The `static` directory contains static files such as images, stylesheets, and scripts. QuickDot will automatically copy these files to the build directory.

### Configuration Files

- `config.json`: Customizes QuickDot's behavior.
- `site.config.json`: Defines site-wide properties.

## Contexts

Contexts are JSON files that define variables accessible in templates. For example:

```json
{
    "title": "My Page",
    "description": "This is my page."
}
```

These variables can be used within the corresponding template.

## Internationalization

Define supported languages in `site.config.json` and QuickDot will look for corresponding .po files in `site_translation_path`.

Example:

```json
"site_languages": ["en", "es"]
```

QuickDot will search for `texts_en.po` and `texts_es.po`.

## Text Gathering

QuickDot can automatically gather text for translation from your `string_table.json` files. These files should be located in the same directory as the corresponding `.html` file. They contain key-value pairs of text to be translated. For example:

```json
[
    {
        "KEY": "greeting",
        "VALUE": "Hello, world!"
    },
    {
        "KEY": "farewell",
        "VALUE": "Goodbye, world!"
    }
]
```

Use the `--gather-texts` flag when running QuickDot to update your `.po` files with text from your `string_table.json` files.

## Contributing

We welcome contributions! Please see our contributing guidelines.

## License

MIT License. See LICENSE file for details.
