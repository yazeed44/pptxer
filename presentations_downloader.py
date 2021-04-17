import json
import re
import sys
import time

import requests
from googlesearch import search
from fake_headers import Headers

from util import load_config, open_json_file_or_create_and_dump_obj, ensure_path_correctness

config = load_config()
presentations_cache = open_json_file_or_create_and_dump_obj(config["presentationsDownloadCacheFilePath"], [])


# TODO scrape from slideshare
# TODO scrape from Bing

def scrape_presentations_to_dir(search_keywords=config["searchKeywords"],
                                presentations_dir_path=config["downloadDirectory"],
                                presentations_download_cache_file_path=config[
                                    "presentationsDownloadCacheFilePath"]):
    urls = __scrape_presentation_urls__(search_keywords)
    paths_to_presentations = []
    for url in urls:
        try:
            response = requests.get(url, headers=Headers(headers=True).generate())
        except:
            e = sys.exc_info()[0]
            print(f"Failed to download {url}. Error is:\n{e}")
            continue
        # TODO deal with duplicate file names overwriting each other
        presentation_file_name = __get_file_name_from_response__(response)
        presentation_file_path = f"{presentations_download_dir_path}/{presentation_file_name}"
        presentation_file_path = ensure_path_correctness(presentation_file_path)
        with open(presentation_file_path, 'wb') as presentation_file:
            presentation_file.write(response.content)
        print(f"Downloaded {url} to {presentation_file_path}.")
        __update_presentations_cache__(url, presentation_file_path, presentations_cache_file_path)
        paths_to_presentations.append(presentation_file_path)
    return paths_to_presentations


def __update_presentations_cache__(url, presentation_file_path, presentations_cache_file_path):
    presentations_cache.append({"path": presentation_file_path, "url": url})
    with open(presentations_cache_file_path, 'w') as f:
        json.dump(presentations_cache, f)


# TODO ensure file name ends with pptx
def __get_file_name_from_response__(response):
    """
    Get filename from content-disposition
    """
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        file_name_from_content_disposition = re.findall('filename=(.+)', content_disposition)
        if len(file_name_from_content_disposition) > 0:
            return file_name_from_content_disposition[0].strip('"')
    return __extract_file_name_from_url__(response.url).strip('"')


def __extract_file_name_from_url__(url):
    return re.findall(r"[^/]*$", url)[0]


def __scrape_presentation_urls__(search_keywords, sleep_secs=30):
    presentations_urls = []
    cached_urls = [presentation["url"] for presentation in presentations_cache]

    for search_keyword in search_keywords:
        search_query = f"{search_keyword} filetype:pptx"
        print(f"Searching for '{search_query}'")
        results = search(search_query, num_results=100)  # 100 is max
        new_results = [new_result for new_result in results if
                       new_result not in presentations_urls and new_result not in cached_urls]
        presentations_urls += new_results
        print(f"Will sleep for {sleep_secs} to avoid rate limit")
        time.sleep(sleep_secs)

    return presentations_urls
