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


def get_words_from_url(url, depth, visited_urls=None, word_counts=None):
    if visited_urls is None:
        visited_urls = set()
    if word_counts is None:
        word_counts = {}

    if depth == 0 or url in visited_urls:
        return word_counts

    visited_urls.add(url)

    try:
        response = requests.get(url, verify=False)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing URL {url}: {e}")
        return word_counts

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract text and tokenize words
    text = soup.get_text()
    for word in re.findall(r'\b\w+\b', text.lower()):
        word_counts[word] = word_counts.get(word, 0) + 1

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
                word_counts.update(get_words_from_url(
                    next_url.geturl(), depth - 1, visited_urls, word_counts))

    return word_counts


def main():
    display_ascii()
    parser = argparse.ArgumentParser(
        description="PassCrawl is generates custom password lists from crawled URLs. Perfect for ethical hackers, penetration testers, and cybersecurity enthusiasts, PassCrawl will help you create specific and targeted password lists by utilizing web content.")
    parser.add_argument("url", help="URL to start crawling from")
    parser.add_argument("-d", "--depth", type=int, default=1,
                        help="Crawling depth (default: 1)")
    parser.add_argument("-m", "--min-occurrences", type=int, default=1,
                        help="Minimum occurrences of a word to include in the list (default: 1)")
    parser.add_argument("-o", "--output", default="password_list.txt",
                        help="Output file name (default: password_list.txt)")
    args = parser.parse_args()

    try:
        word_counts = get_words_from_url(args.url, args.depth)
        saved_word_count = 0

        with open(args.output, "w") as file:
            for word, count in sorted(word_counts.items(), key=lambda x: x[0]):
                if count >= args.min_occurrences:
                    file.write(f"{word}\n")
                    saved_word_count += 1

        print(f"{len(word_counts.items())} words found")
        print(f"{saved_word_count} words saved to {args.output}")
    except KeyboardInterrupt:
        print("\nCrawling aborted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
