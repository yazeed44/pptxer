import json
import re
import time
import logging
import requests
from googlesearch import search
from fake_headers import Headers

from util import load_config, ensure_path_correctness, load_cleaned_up_cache

config = load_config()


# For cache to work correctly, it assumes a few things
# 1 - the url of the pptx file is not changing
# 2 - The relative path of the file will not change
# 3 - Cache file and downloads are within the same directory as python files or below

# TODO scrape from slideshare
# TODO scrape from Bing
# TODO scrape from Searx (local instance for unlimited rate)
# TODO Check if keywords are not empty
def scrape_presentations_to_dir(search_keywords=config["searchKeywords"],
                                presentations_download_dir_path="",
                                presentations_download_cache_file_path=config[
                                    "presentationsDownloadCacheFilePath"]):
    # TODO handle if presentations_download_cache_file_path is None
    # TODO handle if presentations_dir_path does not exist within os
    if presentations_download_dir_path is None or len(presentations_download_dir_path) == 0:
        presentations_download_dir_path = '_'.join(search_keywords)
    presentations_cache = load_cleaned_up_cache(presentations_download_cache_file_path)
    raw_pptx_urls = __scrape_presentation_urls__(search_keywords)
    # Filter pptx that are already downloaded
    cache_hits = [cache for cache in presentations_cache if cache["url"] in raw_pptx_urls]
    cache_misses_urls = list(set(raw_pptx_urls) - set([cache["url"] for cache in cache_hits]))
    logging.info(f"{len(cache_hits)}/{len(raw_pptx_urls)} is already cached. Will attempt to download those that aren't cached")
    paths_to_presentations = [cache["path"] for cache in cache_hits]
    for url in cache_misses_urls:
        try:
            # TODO download files concurrently
            response = requests.get(url, timeout=10, headers=Headers(headers=True).generate())
        except Exception as e:
            logging.warning(e)
            logging.info(f"Due to an error downloading the file, we will skip downloading {url}")
        presentation_file_name = __get_file_name_from_response__(response)
        presentation_file_path = f"{presentations_download_dir_path}/{presentation_file_name}"
        presentation_file_path = ensure_path_correctness(presentation_file_path)
        with open(presentation_file_path, 'wb') as presentation_file:
            presentation_file.write(response.content)
        logging.info(f"Downloaded {url} to {presentation_file_path}")
        __update_presentations_cache__(url, presentation_file_path, presentations_download_cache_file_path,
                                       presentations_cache)
        paths_to_presentations.append(presentation_file_path)
    return paths_to_presentations


def __update_presentations_cache__(url, presentation_file_path, presentations_cache_file_path, presentations_cache):
    presentations_cache.append({"path": presentation_file_path, "url": url})
    with open(presentations_cache_file_path, 'w') as f:
        json.dump(presentations_cache, f)
    logging.debug(f"Updated cache file: {presentations_cache_file_path} to include {presentation_file_path}")


# TODO ensure file name ends with pptx
def __get_file_name_from_response__(response):
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


def __extract_file_name_from_url__(url):
    file_name = re.findall(r"[^/]*$", url)[0].strip('"')
    logging.debug(f"File name through regex is {file_name} retrieved URL {url}")
    return file_name


def __scrape_presentation_urls__(search_keywords, sleep_secs=30):
    presentations_urls = []

    for search_keyword in search_keywords:
        search_query = f"{search_keyword} filetype:pptx"
        logging.info(f"Searching for '{search_query}'")
        results = search(search_query, num_results=100)  # 100 is max
        presentations_urls += results
        logging.info(f"Will sleep for {sleep_secs} seconds to avoid rate limit")
        time.sleep(sleep_secs)

    return presentations_urls
