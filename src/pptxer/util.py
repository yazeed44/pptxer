"""This is a simple utility file for downloading presentation, and extracting text from them"""
import os
import json
from statistics import mean, median
import logging


def __open_json_file_or_create_and_dump_obj__(file_path, json_obj) -> dict:
    if os.path.exists(file_path):
        with open(file_path) as json_file:
            return json.load(json_file)
    else:
        logging.info("%s does not exist. Will create and dump json_obj in", file_path)
        with open(file_path, "w") as json_file:
            json.dump(json_obj, json_file, ensure_ascii=False)
            return json_obj


def __calculate_length_stats_for_list_of_strings__(str_list, list_name="") -> dict:
    # If list_name is empty, then we will return generic names such as avg, sum
    # If it is not empty, then we will embed the list_name in each field,
    # such as avgOf{list_name}
    if list_name != "":
        list_name = list_name[0].upper() + list_name[1:]
    length_array = [len(string) for string in str_list]
    stats_calc_and_names = [
        (sum(length_array), "totalLength"),
        (mean(length_array), "avgLength"),
        (min(length_array), "minLength"),
        (max(length_array), "maxLength"),
        (median(length_array), "medianLength"),
    ]
    return {
        f"{field_name}{list_name}": calculation
        for calculation, field_name in stats_calc_and_names
    }


# If dir does not exist, then create it
# If there exists a file with same path, then add _1, _2, _i to its file name
def __ensure_path_correctness__(path: str) -> str:
    file_directory = os.path.dirname(path)
    if not os.path.exists(file_directory):
        logging.info("%s does not exist. Will attempt to create it", file_directory)
        os.makedirs(file_directory)
    # If a file exists with the same name, then add _1, or _2 at the end
    new_path = path
    i = 1
    while os.path.exists(new_path):
        file_name_without_extension, extension = os.path.splitext(
            os.path.basename(path)
        )
        file_name_without_extension += f"_{i}"
        new_path = os.path.join(file_directory, file_name_without_extension + extension)
        logging.debug(
            "%s already exists. Will change file name to be %s", path, new_path
        )
        i += 1
    logging.debug("%s is valid. Will write to it", new_path)
    return new_path
