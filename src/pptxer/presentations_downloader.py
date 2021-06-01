"""This module scrapes presentations files that contains a specific keywords from search engines"""
import os
import re
import time
from typing import List

import requests
from fake_headers import Headers
from googlesearch import search
from requests import Response, RequestException

from pptxer.util import __ensure_path_correctness__
from pptxer import logger


def scrape_presentations_to_dir(
        search_keywords: List[str], download_dir_path=""
) -> List[str]:
    """
    Scrape presentations that contain search keywords links off search engines, download them to download_dir_path
    , and return their paths

            Parameters:
                    search_keywords (List[str]): A decimal integer
                    download_dir_path (string): Path to the directory where scrapped pptx files will be stored in

            Returns:
                    presentations_paths (List[str]): A list of paths to downloaded pptx files
    """

    if search_keywords is None or len(search_keywords) == 0:
        raise ValueError(
            f"search keywords must be list of strings with length higher than 0\n"
            f"search_keywords={search_keywords}"
        )
    if download_dir_path is None or len(download_dir_path) == 0:
        download_dir_path = "_".join(search_keywords)
    logger.info(
        "Will start scraping with following params: "
        "search_keywords = %s, "
        "download_dir_path = %s, ",
        search_keywords,
        download_dir_path,
    )
    raw_pptx_urls = __scrape_presentation_urls__(search_keywords)
    paths_to_presentations = []
    for url in raw_pptx_urls:
        try:
            response = requests.get(
                url, timeout=10, headers=Headers(headers=True).generate()
            )
        except RequestException as download_error:
            logger.warning(download_error)
            logger.info(
                "Due to an error downloading the file, we will skip downloading %s", url
            )
        file_name = __get_file_name_from_response__(response)
        path = os.path.join(download_dir_path, file_name)
        path = __ensure_path_correctness__(path)
        with open(path, "wb") as presentation_file:
            presentation_file.write(response.content)
        logger.info("Downloaded %s to %s", url, path)
        paths_to_presentations.append(path)
    return paths_to_presentations


def __get_file_name_from_response__(response: Response):
    """
    Get filename from content-disposition
    """
    content_disposition = response.headers.get("content-disposition")
    if content_disposition and "filename" in content_disposition:
        filename = re.findall("filename=(.+)", content_disposition)[0]
        logger.debug(
            "File name retrieved from content-disposition header: %s", filename
        )
    else:
        filename = __extract_file_name_from_url__(response.url).strip('"')
    filename = filename if len(filename) < 248 else filename[:248]
    if not filename.endswith(".pptx"):
        filename += ".pptx"
    logger.debug("Final file name: %s", filename)
    return filename


def __extract_file_name_from_url__(url: str):
    file_name = re.findall(r"[^/]*$", url)[0].strip('"')
    logger.debug("File name through regex is %s retrieved URL %s", file_name, url)
    return file_name


def __scrape_presentation_urls__(search_keywords: List[str], sleep_secs=30):
    urls = []
    for search_keyword in search_keywords:
        search_query = f"{search_keyword} filetype:pptx"
        logger.info("Searching for '%s'", search_query)
        results = search(search_query, num_results=100)  # 100 is max
        urls += results
        if search_keyword != search_keywords[-1]:
            logger.info("Will sleep for %d seconds to avoid rate limit", sleep_secs)
            time.sleep(sleep_secs)

    return urls
