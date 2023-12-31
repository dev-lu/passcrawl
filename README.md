# PassCrawl 🛡️

## Password List Generator

PassCrawl is a tool that generates custom password lists from crawled URLs. Perfect for ethical hackers, penetration testers, and cybersecurity enthusiasts, this tool will help you create specific and targeted password lists by utilizing web content.

### Features

- Deep crawling based on specified depth.
- Export generated password lists to a file.
- Efficient and fast URL processing.

### Prerequisites

Ensure you have `Python 3.11` installed on your machine. You can download and install Python [here](https://www.python.org/downloads/).

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/dev-lu/passcrawl.git
   ```
2. Navigate to the project directory:
   ```bash
   cd passcrawl
   ```
3. (Optional) Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```

### Usage

To use PassCrawl, provide the target URL, desired link depth (`-d`), and an output filename (`-o`).

Parameters:

- `-d <link depth>`: Specify the depth of links to crawl. For example, `-d 2` will crawl the main page and one level deep into the linked pages.
- `-o <output filename>`: Name of the file to store the generated password list.
- `-m <minimum occurrences>`: Set the minimum amount of occurrences to include a word to the list.
- `-l <minimum word length>`: Set the minimum length of a word to append to the list.
- `-b <blacklist>`: Path to a blacklist file containing words that should not be added to the final list.
- `-u <user agent>`: User-Agent string or path to a file with a list of User-Agents. If a file path is provided, a User-Agent will be randomly selected from the file. If not provided, the default User-Agent will be used.
- `-t <specify number of threads>`: Set the number of threads used to crawl URLs.

Example:

```bash
python passcrawl.py https://example.com -d 2 -o passwordlist.txt
```

### Contributing

If you find a bug or have a feature request, please open an issue. If you'd like to contribute to the codebase, please open a pull request.

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

### Credits

Developed by dev-lu.
