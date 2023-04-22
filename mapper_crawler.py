
import os
from bs4 import BeautifulSoup
import colorama
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque
import re



# init the colorama module
colorama.init()

GREEN = colorama.Fore.GREEN
GRAY = colorama.Fore.LIGHTBLACK_EX
RESET = colorama.Fore.RESET
YELLOW = colorama.Fore.YELLOW
PURPLE = colorama.Fore.MAGENTA
RED = colorama.Fore.RED
BLUE = colorama.Fore.BLUE
CREAM = colorama.Fore.LIGHTYELLOW_EX
ORANGE = colorama.Fore.LIGHTRED_EX
MEROON = colorama.Fore.LIGHTMAGENTA_EX

url = "https://www.msu.ru"
max_visits = 1000  # ... max number of pages to visit

# a queue of urls to be crawled
new_urls = deque([url])

# a set of urls that we have already been processed
processed_urls = set()
# a set of domains inside the target website
local_urls = set()
# a set of subdomains inside the target website
subdomain_urls = set()
# a set of documnent urls (pdf,doc,docx) inside the target website
document_urls = set()
# a set of domains outside the target website
foreign_urls = set()
# a set of broken urls
broken_urls = set()
# a set of all urls found on the target website
total_urls_visited = 0



# process urls one by one until we exhaust the queue
while len(new_urls) and total_urls_visited < max_visits:
    # move next url from the queue to the set of processed urls
    url = new_urls.popleft()
    processed_urls.add(url)
    total_urls_visited += 1
    # get url's content
    # print("Processing %s" % url)
    print(f"{YELLOW}[*] Crawling: {url}{RESET}")
    try:
        response = requests.get(url)
    except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, requests.exceptions.InvalidURL, requests.exceptions.InvalidSchema):
        # add broken urls to it's own set, then continue
        print(f"{RED}[*] Broken link: {url}{RESET}")
        broken_urls.add(url)
        continue

    # extract base url to resolve relative links
    parts = urlsplit(url) 
    base = "{0.netloc}".format(parts) 
    strip_base = base.replace("www.", "")
    base_url = "{0.scheme}://{0.netloc}".format(parts) 
    path = url[:url.rfind('/')+1] if '/' in parts.path else url

    # Define headers with user agent string
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
    }

    # create a beutiful soup for the html document
    soup = BeautifulSoup(requests.get(url, headers=headers).content, "lxml")

    for link in soup.find_all('a'):
        # extract link url from the anchor
        anchor = link.attrs["href"] if "href" in link.attrs else ''

        # skip email links, tel links, and image/video links
        if anchor.startswith('mailto:') or anchor.startswith('tel:') or anchor.endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.mp4', '.avi', '.mov')):
            continue
        # extract document links
        elif anchor.endswith(('.doc', '.docx', '.pdf', '.pptx', '.ppt', '.xls', '.xlsx', '.csv', '.txt', '.rtf', '.zip', '.rar')):
            print(f"{YELLOW}[*] Document link: {anchor}{RESET}")
            document_urls.add(anchor)
            continue
        elif anchor.startswith('/'):
            local_link = base_url + anchor
            print(f"{GREEN}[*] Local link: {local_link}{RESET}")
            local_urls.add(local_link)
        # elif strip_base in anchor:
        #     local_urls.add(anchor)
        # elif not anchor.startswith('http'):
        #     local_link = path + anchor
        #     local_urls.add(local_link)
        elif strip_base in anchor:
            subdomain = anchor.split('.')[0]
            if subdomain != strip_base.split('.')[0]:
                subdomain_urls.add(anchor)
                print(f"{BLUE}[*] Subdomain link: {anchor}{RESET}")
        else:
            print(f"{GRAY}[*] Foreign link: {anchor}{RESET}")
            foreign_urls.add(anchor)
        

    # Add internal links to the queue
    for i in local_urls.union(subdomain_urls):
        if i not in new_urls and i not in processed_urls:
            print(f"{PURPLE}[*] Adding to queue: {i}{RESET}")
            new_urls.append(i)


# add all urls to the total count minus the processed urls

total_urls_visited += len(local_urls)
total_urls_visited += len(subdomain_urls)
total_urls_visited += len(foreign_urls)
total_urls_visited += len(document_urls)
total_urls_visited += len(broken_urls)
total_urls_visited -= len(processed_urls)

# create a report of all urls
print("[+] Total Internal links:", len(local_urls))
print("[+] Total Subdomain links:", len(subdomain_urls))
print("[+] Total Foreign links:", len(foreign_urls))
print("[+] Total Document links:", len(document_urls))
print("[+] Total Broken links:", len(broken_urls))
print("[+] Total URLs:", total_urls_visited)
print("[+] Total Processed URLs:", len(processed_urls))

# save the report to a files in the directory named after the target website. one file for each type of url and one file for all urls.

# Create a folder with the domain name to save the files
if not os.path.exists(strip_base):
    os.makedirs(strip_base)
    
# save all urls to a file
with open(strip_base + "/" + strip_base + "_all_urls.txt", "w", encoding='utf-8') as f:
    for all_urls in local_urls | subdomain_urls | foreign_urls | document_urls | broken_urls:
        print(all_urls.strip(), file=f)
        
# save internal urls to a file
with open(strip_base + "/" + strip_base + "_internal_urls.txt", "w", encoding='utf-8') as f:
    for internal in local_urls:
        print(internal.strip(), file=f)
        
# save subdomain urls to a file
with open(strip_base + "/" + strip_base + "_subdomain_urls.txt", "w", encoding='utf-8') as f:
    for subdomain in subdomain_urls:
        print(subdomain.strip(), file=f)

# save foreign urls to a file
with open(strip_base + "/" + strip_base + "_foreign_urls.txt", "w", encoding='utf-8') as f:
    for foreign in foreign_urls:
        print(foreign.strip(), file=f)
        
# save document urls to a file
with open(strip_base + "/" + strip_base + "_document_urls.txt", "w", encoding='utf-8') as f:
    for document in document_urls:
        print(document.strip(), file=f)
        
# save broken urls to a file
with open(strip_base + "/" + strip_base + "_broken_urls.txt", "w", encoding='utf-8') as f:
    for broken in broken_urls:
        print(broken.strip(), file=f)
        
# save processed urls to a file
with open(strip_base + "/" + strip_base + "_processed_urls.txt", "w", encoding='utf-8') as f:
    for processed in processed_urls:
        print(processed.strip(), file=f)
