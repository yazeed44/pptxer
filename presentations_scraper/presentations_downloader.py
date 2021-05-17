"""This module scrapes presentations files that contains a specific keywords from search engines"""
import json
import logging
import re
import time
from typing import List

import requests
from fake_headers import Headers
from googlesearch import search
from requests import Response, RequestException

from util import ensure_path_correctness, load_cleaned_up_cache


# For cache to work correctly, it assumes a few things
# 1 - the url of the pptx file is not changing
# 2 - The relative path of the file will not change
# 3 - Cache file and downloads are within the same directory as python files


def scrape_presentations_to_dir(
        search_keywords: List[str], download_dir_path="", cache_file_path="cache.json"
) -> List[str]:
    if search_keywords is None or len(search_keywords) == 0:
        raise ValueError(f"search keywords must be list of strings with length higher than 0\n"
                         f"search_keywords={search_keywords}")
    if download_dir_path is None or len(download_dir_path) == 0:
        download_dir_path = "_".join(search_keywords)
    if cache_file_path is None:
        cache_file_path = "../cache.json"
    logging.info(
        "Will start scraping with following params: "
        "search_keywords = %s, "
        "download_dir_path = %s, "
        "cache_file_path = %s", search_keywords, download_dir_path, cache_file_path
    )
    cache = load_cleaned_up_cache(cache_file_path)
    raw_pptx_urls = __scrape_presentation_urls__(search_keywords)
    # Filter pptx that are already downloaded
    cache_hits = [cache for cache in cache if cache["url"] in raw_pptx_urls]
    cache_misses_urls = list(
        set(raw_pptx_urls) - set([cache["url"] for cache in cache_hits])
    )
    logging.info(
        "%d out of %d is already cached. Will attempt to download those that aren't cached", len(cache_hits),
        len(raw_pptx_urls))
    paths_to_presentations = [cache["path"] for cache in cache_hits]
    for url in cache_misses_urls:
        try:
            response = requests.get(
                url, timeout=10, headers=Headers(headers=True).generate()
            )
        except RequestException as download_error:
            logging.warning(download_error)
            logging.info("Due to an error downloading the file, we will skip downloading %s", url)
        file_name = __get_file_name_from_response__(response)
        path = f"{download_dir_path}/{file_name}"
        path = ensure_path_correctness(path)
        with open(path, "wb") as presentation_file:
            presentation_file.write(response.content)
        logging.info("Downloaded %s to %s", url, path)
        __update_cache__(url, path, cache_file_path, cache)
        paths_to_presentations.append(path)
    return paths_to_presentations


def __update_cache__(
        url: str, presentation_file_path: str, cache_file_path: str,
        cache: List[dict]
):
    cache.append({"path": presentation_file_path, "url": url})
    with open(cache_file_path, "w") as cache_file:
        json.dump(cache, cache_file)
    logging.debug(
        "Updated cache file: %s to include %s", cache_file_path, presentation_file_path)


def __get_file_name_from_response__(response: Response):
    """
    Get filename from content-disposition
    """
    content_disposition = response.headers.get("content-disposition")
    if content_disposition:
        filename = re.findall(
            "filename=(.+)", content_disposition
        )
        if len(filename) > 0:
            filename = filename[0].strip('"')
            logging.debug(
                "File name retrieved from content-disposition header: %s", filename)
    else:
        filename = __extract_file_name_from_url__(response.url).strip('"')
    if not filename.endswith(".pptx"):
        filename += ".pptx"
    return filename


def __extract_file_name_from_url__(url: str):
    file_name = re.findall(r"[^/]*$", url)[0].strip('"')
    logging.debug("File name through regex is %s retrieved URL %s", file_name, url)
    return file_name


def __scrape_presentation_urls__(search_keywords: List[str], sleep_secs=30):
    urls = []
    for search_keyword in search_keywords:
        search_query = f"{search_keyword} filetype:pptx"
        logging.info("Searching for '%s'", search_query)
        results = search(search_query, num_results=100)  # 100 is max
        urls += results
        if search_keyword != search_keywords[-1]:
            logging.info("Will sleep for %d seconds to avoid rate limit", sleep_secs)
            time.sleep(sleep_secs)

    return urls
