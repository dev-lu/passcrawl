import argparse
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import re
from functools import lru_cache
from concurrent.futures import ThreadPoolExecutor
from tabulate import tabulate
import time
import urllib3
import os
import random

# Disable insecure request warnings globally
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

number_of_urls = 0
numer_of_crawling_errors = 0
word_counts = 0
saved_word_count = 0
proxies = []
current_proxy_index = 0
user_agents = None


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


def read_blacklist(filepath):
    if not filepath:
        return set()
    with open(filepath, 'r') as file:
        return set(line.strip().lower() for line in file.readlines())


def print_centered(text, width=80, char='='):
    padded_text = text + ' '
    print(padded_text.center(width, char))


def load_proxies(proxy_file):
    global proxies
    with open(proxy_file, 'r') as file:
        proxies = [line.strip() for line in file.readlines() if line.strip()]


def get_next_proxy():
    global current_proxy_index
    if not proxies:
        return None
    proxy = proxies[current_proxy_index]
    current_proxy_index = (current_proxy_index + 1) % len(proxies)
    return {
        "http": f"http://{proxy}"
    }


@lru_cache(maxsize=512)  # Store 512 requests in cache
def fetch_url_content(url):
    global number_of_urls
    global numer_of_crawling_errors
    retry_count = len(proxies) if proxies else 1

    while retry_count > 0:
        proxy = get_next_proxy()
        if user_agents:
            if isinstance(user_agents, list):
                user_agent = random.choice(user_agents)
            else:
                user_agent = user_agents
        else:
            user_agent = requests.utils.default_user_agent()

        headers = {
            "User-Agent": user_agent
        }

        try:
            if proxy:
                response = requests.get(
                    url, verify=False, proxies=proxy, headers=headers)
            else:
                response = requests.get(url, verify=False)
            response.raise_for_status()
            number_of_urls += 1
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"Error accessing URL {url} using proxy {proxy}: {e}")
            numer_of_crawling_errors += 1
            retry_count -= 1

    return None


def get_words_from_url(url, depth, max_threads, visited_urls=None, word_counts=None):
    if visited_urls is None:
        visited_urls = set()
    if word_counts is None:
        word_counts = {}

    if depth == 0 or url in visited_urls:
        return word_counts

    visited_urls.add(url)

    content = fetch_url_content(url)
    if content is None:
        return word_counts

    print(f"Crawl {url}")

    soup = BeautifulSoup(content, 'html.parser')

    # Extract text and tokenize words
    text = soup.get_text()
    for word in re.findall(r'\b\w+\b', text.lower()):
        word_counts[word] = word_counts.get(word, 0) + 1

    # Find links on page and crawl recursively
    parsed_url = urlparse(url)
    base_url = f"{parsed_url.scheme}://{parsed_url.netloc}"
    next_urls = []

    for link in soup.find_all('a'):
        href = link.get('href')
        if href and not href.startswith('#') and not href.startswith('javascript:'):
            next_url = urlparse(href)
            if not next_url.netloc:
                next_url = urlparse(base_url + href)
            if next_url.netloc == parsed_url.netloc:
                next_urls.append(next_url.geturl())

    # Use concurrency to crawl multiple URLs
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(get_words_from_url, next_url, depth - 1,
                                   max_threads, visited_urls, word_counts) for next_url in next_urls]

        for future in futures:
            word_counts.update(future.result())
    return word_counts


def main():
    global saved_word_count
    global word_counts
    global user_agents

    start_time = time.perf_counter()
    display_ascii()
    parser = argparse.ArgumentParser(
        description="PassCrawl is generates custom password lists from crawled URLs. Perfect for ethical hackers, penetration testers, and cybersecurity enthusiasts, PassCrawl will help you create specific and targeted password lists by utilizing web content.")
    parser.add_argument("url", help="URL to start crawling from")
    parser.add_argument("-d", "--depth", type=int, default=1,
                        help="Crawling depth (default: 1)")
    parser.add_argument("-m", "--min-occurrences", type=int, default=1,
                        help="Minimum occurrences of a word to include in the list (default: 1)")
    parser.add_argument("-l", "--length", type=int, default=1,
                        help="Minimum length of a word to include in the list (default: 1)")
    parser.add_argument("-b", "--blacklist", default=None,
                        help="Path to a blacklist file containing words that should not be added to the final list.")
    parser.add_argument("-p", "--proxy-file", default=None,
                        help="File containing a list of proxies for proxy rotation.")
    parser.add_argument("-u", "--user-agent", default=None,
                        help="User-Agent string or path to a file with a list of User-Agents. If a file path is provided, a User-Agent will be randomly selected from the file. If not provided, the default User-Agent will be used.")
    parser.add_argument("-o", "--output", default="password_list.txt",
                        help="Output file name (default: password_list.txt)")
    parser.add_argument("-t", "--threads", type=int, default=1,
                        help="Number of threads for concurrent crawling (default: 1)")
    args = parser.parse_args()

    if args.proxy_file:
        load_proxies(args.proxy_file)

    if args.user_agent:
        if os.path.isfile(args.user_agent):
            with open(args.user_agent, 'r') as file:
                user_agents = [line.strip() for line in file if line.strip()]
        else:
            user_agents = args.user_agent

    try:
        word_counts = get_words_from_url(args.url, args.depth, args.threads)
        saved_word_count = 0

        blacklisted_words = read_blacklist(args.blacklist)
        with open(args.output, "w") as file:
            for word, count in sorted(word_counts.items(), key=lambda x: x[0]):
                if word not in blacklisted_words and count >= args.min_occurrences and len(word) >= args.length:
                    file.write(f"{word}\n")
                    saved_word_count += 1

    except KeyboardInterrupt:
        print("\nCrawling aborted by user.")
    except Exception as e:
        print(f"An error occurred: {e}")

    cache_info = fetch_url_content.cache_info()
    duration = time.perf_counter() - start_time

    stats = [
        ["Words found", len(word_counts.items())],
        [f"Words saved to {args.output}", saved_word_count],
        ["Number of URLs crawled", number_of_urls],
        ["Number of crawling errors", numer_of_crawling_errors],
        ["Duration (seconds)", duration],
        ["Cache Info",
            f"hits: {cache_info.hits}, misses: {cache_info.misses}, maxsize: {cache_info.maxsize}, currsize: {cache_info.currsize}"],
    ]

    print("\n")
    print_centered(" STATISTICS ")
    table_str = tabulate(stats, tablefmt="plain")
    print(table_str)


if __name__ == "__main__":
    main()
