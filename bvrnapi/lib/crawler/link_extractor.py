# original from x4nth055 https://github.com/x4nth055
# https://github.com/x4nth055/pythoncode-tutorials/blob/master/web-scraping/link-extractor/link_extractor_js.py
# License: https://github.com/x4nth055/pythoncode-tutorials/blob/master/web-scraping/link-extractor/link_extractor_js.py
from typing import List
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup
from pydantic import AnyUrl
from requests_html import HTMLSession

# initialize the set of links (unique links)
internal_urls = []
external_urls = []

total_urls_visited = 0


def _is_valid(url: str):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


def _get_all_website_links(url: str):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    and add it to external or internal urls.
    """
    # all URLs of `url`
    urls = set()
    # domain name of the URL without the protocol
    domain_name = urlparse(url).netloc
    # initialize an HTTP session
    session = HTMLSession()
    # make HTTP request & retrieve response
    response = session.get(url)
    # execute Javascript
    try:
        response.html.render()
    except Exception:
        pass
    try:
        soup = BeautifulSoup(response.html.html, "html.parser")
    except Exception:
        return urls
    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue
        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path
        if not _is_valid(href):
            # not a valid URL
            continue
        if href in internal_urls:
            # already in the set
            continue
        if domain_name not in href:
            # external link
            if href not in external_urls:
                external_urls.append(href)
            continue
        urls.add(href)
        internal_urls.append(href)
    return urls


def _crawl(url, max_urls=30):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    params:
        max_urls (int): number of max urls to crawl, default is 30.
    """
    global total_urls_visited
    total_urls_visited += 1
    links = _get_all_website_links(url)
    for link in links:
        if total_urls_visited > max_urls:
            break
        _crawl(link, max_urls=max_urls)


def link_by_name(url: AnyUrl, keywords: List[str], max_urls: int = 5):
    """
    Tries to find an url matching a keyword.
    :param url: Any (http) url to look for links by the keywords list.
    :param keywords: List of words to find a link by name, ordered by priority (highest first).
    :param max_urls: Number of (internal) urls to crawl recursively.
    :return: First matching url found or None if nothing found.
    """
    global total_urls_visited, internal_urls, external_urls
    total_urls_visited = 0
    internal_urls = []
    external_urls = []

    _crawl(url, max_urls)
    for kw in keywords:
        found = list(
            filter(lambda internal_url: kw in internal_url.lower(), internal_urls)
        )
        if found:
            return found[0]
        found = list(
            filter(lambda external_url: kw in external_url.lower(), external_urls)
        )
        if found:
            return found[0]
    return None
