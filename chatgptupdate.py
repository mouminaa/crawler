import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import colorama
import os

# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW


# initialize the set of links (unique links)
internal_urls = set()
external_urls = set()
subdomains = set()
broken_urls = set()
document_urls = set()

total_urls_visited = 0

# Define headers with user agent string
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

# function to check if a URL is valid


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)  # add headers to avoid 403 error
    return bool(parsed.netloc) and bool(parsed.scheme)


# function to extract all links from a web page
def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """
    # all URLs of `url`
    urls = set()
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "lxml")
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # skip tel and mailto links
        if href.startswith("tel:") or href.startswith("mailto:"):
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls:
                print(f"{GRAY}[!] External link: {href}{RESET}")
                external_urls.add(href)
            continue
        print(f"{GREEN}[*] Internal link: {href}{RESET}")
        urls.add(href)
        internal_urls.add(href)
        # check if the link is from a subdomain
        subdomain = parsed_href.netloc.split('.')[0]
        if subdomain != domain_name.split('.')[0]:
            subdomains.add(subdomain)
        # check if the link is a document link
        extension = os.path.splitext(parsed_href.path)[1]
        if extension in ['.doc', '.docx', '.pdf', '.pptx']:
            document_urls.add(href)
    return urls


# function to crawl a web page and extract all links
def crawl(url, max_urls=50000):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    try:
        links = get_all_website_links(url)
        for link in links:
            if total_urls_visited > max_urls:
                break
            crawl(link, max_urls=max_urls)
    except Exception as e:
        print(f"{GRAY}[!] Error: {e}{RESET}")
        broken_urls.add(url)  # save error link
        

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Link Extractor Tool with Python")
    parser.add_argument("url", help="The URL to extract links from.")
    parser.add_argument(
        "-m", "--max-urls", help="Number of max URLs to crawl, default is 30.", default=50000, type=int)

    args = parser.parse_args()
    url = args.url
    max_urls = args.max_urls
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    crawl(url, max_urls=max_urls)

    print("[+] Total Internal links:", len(internal_urls))
    print("[+] Total External links:", len(external_urls))
    print("[+] Total Subdomains:", len(subdomains))
    print("[+] Total Documents:", len(document_urls))
    print("[+] Total Broken links:", len(broken_urls))
    print("[+] Total URLs:", len(external_urls) + len(internal_urls) + len(subdomains) + len(document_urls))
    print("[+] Total crawled URLs:", max_urls)

    # save the internal links to a file
    with open(f"{domain_name}/{domain_name}_internal_links.txt", "w") as f:
        for internal_link in internal_urls:
            print(internal_link.strip(), file=f)

    # save the external links to a file
    with open(f"{domain_name}/{domain_name}_external_links.txt", "w") as f:
        for external_link in external_urls:
            print(external_link.strip(), file=f)
            
    # save the subdomains to a file
    with open(f"{domain_name}/{domain_name}_subdomains.txt", "w") as f:
        for subdomain in subdomains:
            print(subdomain.strip(), file=f)
    
    # save the document links to a file
    with open(f"{domain_name}/{domain_name}_document_links.txt", "w") as f:
        for document_link in document_urls:
            print(document_link.strip(), file=f)
    
    # save the broken links to a file
    with open(f"{domain_name}/{domain_name}_broken_links.txt", "w") as f:
        for broken_link in broken_urls:
            print(broken_link.strip(), file=f)
            
    # save the total links to a file
    with open(f"{domain_name}/{domain_name}_total_links.txt", "w") as f:
        for total_link in external_urls | internal_urls | subdomains | document_urls:
            print(total_link.strip(), file=f)
    
    # save the total crawled links to a file
    with open(f"{domain_name}/{domain_name}_total_crawled_links.txt", "w") as f:
        for total_crawled_link in max_urls:
            print(total_crawled_link.strip(), file=f)        
