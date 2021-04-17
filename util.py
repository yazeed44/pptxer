import os
import json
from statistics import mean, median

DEFAULT_CONFIG = {
    "search_keywords": ["Search Query 1", "Search Query 2",
                        "Search Query 3 after:2019"  # We can also use search arguments
                        ],
    "presentationsDownloadCacheFilePath": "presentation_download_cache.json",
    "downloadDirectory": "presentations/"}


def open_json_file_or_create_and_dump_obj(file_path, json_obj):
    if os.path.exists(file_path):
        with open(file_path) as f:
            return json.load(f)
    else:
        with open(file_path, 'w') as f:
            json.dump(json_obj, f)
            return json_obj


def load_config():
    return open_json_file_or_create_and_dump_obj("config.json", DEFAULT_CONFIG)


def calculate_length_stats_for_list_of_strings(str_list, list_name=""):
    # If list_name is empty, then we will return generic names such as avg, sum
    # If it is not empty, then we will embed the list_name in each field, such as avgOf{list_name}
    if list_name != "":
        list_name = list_name[0].upper() + list_name[1:]  # Capitalize the first letter
    length_array = [len(string) for string in str_list]
    stats_calc_and_names = [(sum(length_array), "totalLength"), (mean(length_array), "avgLength"),
                            (min(length_array), "minLength"),
                            (max(length_array), "maxLength"), (median(length_array), "medianLength")]
    return {f"{field_name}{list_name}": calculation for calculation, field_name in
            stats_calc_and_names}


# If dir does not exist, then create it
# If there exists a file with same path, then add _1, _2, _i to its file name
def ensure_path_correctness(path: str):
    file_directory = os.path.dirname(path)
    if not os.path.exists(file_directory):
        os.makedirs(file_directory)
    # If a file exists with the same name, then add _1, or _2 at the end
    new_path = path
    i = 1
    while os.path.exists(new_path):
        file_name_without_extension, extension = os.path.splitext(os.path.basename(path))
        file_name_without_extension += f"_{i}"
        new_path = os.path.join(file_directory, file_name_without_extension + extension)
        i += 1
    return new_path
