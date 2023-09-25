import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
import urllib3

# Disable insecure request warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def display_ascii():
    ascii_text = """
  _____               _____                    _ 
 |  __ \             / ____|                  | |
 | |__) |_ _ ___ ___| |     _ __ __ ___      _| |
 |  ___/ _` / __/ __| |    | '__/ _` \ \ /\ / / |
 | |  | (_| \__ \__ \ |____| | | (_| |\ V  V /| |
 |_|   \__,_|___/___/\_____|_|  \__,_| \_/\_/ |_|
   by dev-lu                                              
                                                 
    """
    print(ascii_text)


def get_words_from_url(url, depth, visited_urls=None):
    if visited_urls is None:
        visited_urls = set()

    if depth == 0 or url in visited_urls:
        return set()

    visited_urls.add(url)

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing URL {url}: {e}")
        return set()

    soup = BeautifulSoup(response.text, 'html.parser')
    words = set()

    # Extract text and tokenize words
    text = soup.get_text()
    words.update(re.findall(r'\b\w+\b', text.lower()))

    # Find links on page and crawl recursively
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and not href.startswith('#') and not href.startswith('javascript:'):
            next_url = urlparse(href)
            if not next_url.netloc:
                next_url = urlparse(base_url + href)

            if next_url.netloc == parsed_url.netloc:
                words.update(get_words_from_url(
                    next_url.geturl(), depth - 1, visited_urls))

    return words


def main():
    display_ascii()
    parser = argparse.ArgumentParser(
        description="PassCrawl is generates custom password lists from crawled URLs. Perfect for ethical hackers, penetration testers, and cybersecurity enthusiasts, PassCrawl will help you create specific and targeted password lists by utilizing web content.")
    parser.add_argument("url", help="URL to start crawling from")
    parser.add_argument("-d", "--depth", type=int, default=1,
                        help="Crawling depth (default: 1)")
    parser.add_argument("-o", "--output", default="password_list.txt",
                        help="Output file name (default: password_list.txt)")
    args = parser.parse_args()

    try:
        unique_words = get_words_from_url(args.url, args.depth)

        with open(args.output, "w") as file:
            for word in sorted(unique_words):
                file.write(f"{word}\n")

        print(f"Unique words saved to {args.output}")
    except KeyboardInterrupt:
        print("\nCrawling aborted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
