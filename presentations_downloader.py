import json
import re
import time
import logging
import requests
from googlesearch import search
from fake_headers import Headers
from typing import List

from requests import Response

from util import ensure_path_correctness, load_cleaned_up_cache


# For cache to work correctly, it assumes a few things
# 1 - the url of the pptx file is not changing
# 2 - The relative path of the file will not change
# 3 - Cache file and downloads are within the same directory as python files or below

# TODO scrape from slideshare
# TODO scrape from Bing
# TODO scrape from Searx (local instance for unlimited rate)
# TODO Check if keywords are not empty
def scrape_presentations_to_dir(search_keywords,
                                download_dir_path="",
                                cache_file_path="cache.json") -> List[str]:
    if download_dir_path is None or len(download_dir_path) == 0:
        download_dir_path = '_'.join(search_keywords)
    if cache_file_path is None:
        cache_file_path = "cache.json"
    logging.info(f"Will start scraping with following params: search_keywords = {search_keywords}, "
                 f"download_dir_path = {download_dir_path}, cache_file_path = {cache_file_path}")
    cache = load_cleaned_up_cache(cache_file_path)
    raw_pptx_urls = __scrape_presentation_urls__(search_keywords)
    # Filter pptx that are already downloaded
    cache_hits = [cache for cache in cache if cache["url"] in raw_pptx_urls]
    cache_misses_urls = list(set(raw_pptx_urls) - set([cache["url"] for cache in cache_hits]))
    logging.info(
        f"{len(cache_hits)}/{len(raw_pptx_urls)} is already cached. Will attempt to download those that aren't cached")
    paths_to_presentations = [cache["path"] for cache in cache_hits]
    for url in cache_misses_urls:
        try:
            # TODO download files concurrently
            response = requests.get(url, timeout=10, headers=Headers(headers=True).generate())
        except Exception as e:
            logging.warning(e)
            logging.info(f"Due to an error downloading the file, we will skip downloading {url}")
        presentation_file_name = __get_file_name_from_response__(response)
        presentation_file_path = f"{download_dir_path}/{presentation_file_name}"
        presentation_file_path = ensure_path_correctness(presentation_file_path)
        with open(presentation_file_path, 'wb') as presentation_file:
            presentation_file.write(response.content)
        logging.info(f"Downloaded {url} to {presentation_file_path}")
        __update_cache__(url, presentation_file_path, cache_file_path, cache)
        paths_to_presentations.append(presentation_file_path)
    return paths_to_presentations


def __update_cache__(url: str, presentation_file_path: str, cache_file_path: str, cache: List[dict]):
    cache.append({"path": presentation_file_path, "url": url})
    with open(cache_file_path, 'w') as f:
        json.dump(cache, f)
    logging.debug(f"Updated cache file: {cache_file_path} to include {presentation_file_path}")


# TODO ensure file name ends with pptx
def __get_file_name_from_response__(response: Response):
    """
    Get filename from content-disposition
    """
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        file_name_from_content_disposition = re.findall('filename=(.+)', content_disposition)
        if len(file_name_from_content_disposition) > 0:
            file_name = file_name_from_content_disposition[0].strip('"')
            logging.debug(f"File name retrieved from content-disposition header: {file_name}")
            return file_name
    return __extract_file_name_from_url__(response.url).strip('"')


def __extract_file_name_from_url__(url: str):
    file_name = re.findall(r"[^/]*$", url)[0].strip('"')
    logging.debug(f"File name through regex is {file_name} retrieved URL {url}")
    return file_name


def __scrape_presentation_urls__(search_keywords: List[str], sleep_secs=30):
    urls = []
    for search_keyword in search_keywords:
        search_query = f"{search_keyword} filetype:pptx"
        logging.info(f"Searching for '{search_query}'")
        results = search(search_query, num_results=100)  # 100 is max
        urls += results
        if search_keyword != search_keywords[-1]:
            logging.info(f"Will sleep for {sleep_secs} seconds to avoid rate limit")
            time.sleep(sleep_secs)

    return urls
