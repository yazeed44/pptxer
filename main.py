import json
import os
import re
import time

from googlesearch import search
from pptx import Presentation
import requests
from fake_headers import Headers

presentations_file_extensions = ["pptx"]

processed_presentations_file_name = "processed_presentations_urls.json"
with open(processed_presentations_file_name) as f:
    processed_presentations_urls = json.load(f)

search_keywords = ["Augmented Reality", "Virtual Reality", "Oculus VR", "Mixed Reality", "HoloLens",
                   "Social VR", "Inside-out tracking", "Virtual Reality headset"]


def scrape_presentation_urls():
    presentations_urls = []
    for search_keyword in search_keywords:
        for file_extension in presentations_file_extensions:
            search_query = f"{search_keyword} filetype:{file_extension}"
            print(f"Searching for '{search_query}'")
            results = search(search_query, num_results=100)
            new_results = [new_result for new_result in results if
                           new_result not in presentations_urls and new_result not in processed_presentations_urls]
            presentations_urls += new_results
            time.sleep(30)

    return presentations_urls


def get_file_name_from_response(response):
    """
    Get filename from content-disposition
    """
    content_disposition = response.headers.get('content-disposition')
    if content_disposition:
        file_name_from_content_disposition = re.findall('filename=(.+)', content_disposition)
        if len(file_name_from_content_disposition) > 0:
            return file_name_from_content_disposition[0]
    return extract_file_name_from_url(response.url)


def extract_file_name_from_url(url):
    url_regex_file_name = re.findall(r"(?=\w+\.\w{3,4}$).+", url)
    if url_regex_file_name:
        return url_regex_file_name[0]
    else:
        return url


def get_presentation_urls_from_cached_file():
    with open("presentations_urls.json") as f:
        return json.load(f)


def post_presentation_processing(url):
    processed_presentations_urls.append(url)
    with open(processed_presentations_file_name, 'w') as f:
        json.dump(processed_presentations_urls, f)


# TODO remove double quote (test_quote.strip('"'))
# TODO ensure file name ends with pptx
def main():
    # presentation_urls = scrape_presentation_urls()
    # presentation_urls = ["https://enable.unc.edu/wp-content/uploads/2019/05/CHIP_XRHealthcare.pptx"]
    presentation_urls = get_presentation_urls_from_cached_file()
    presentation_urls = [url for url in presentation_urls if
                         url.endswith("pptx") and url not in processed_presentations_urls]
    for url in presentation_urls:
        try:

            response = requests.get(url, headers=Headers(headers=True).generate())
            presentation_file_name = get_file_name_from_response(response)
            print(f"Loaded {presentation_file_name}. Will attempt to process")
            with open(presentation_file_name, 'wb') as presentation_file:
                presentation_file.write(response.content)

            presentation = Presentation(presentation_file_name)
            has_notes = any([slide.has_notes_slide for slide in presentation.slides])
            if has_notes:
                print(f"{presentation_file_name} has notes. Storing ...")
            else:
                print(
                    f"{presentation_file_name} has no notes. Attempting to discard\n. Discarding result = {os.remove(presentation_file_name) is None}")
            post_presentation_processing(response.url)
        except:
            print(f"Error with {url}. Skipping")
            post_presentation_processing(url)
            continue

    print("Done")


if __name__ == '__main__':
    main()
