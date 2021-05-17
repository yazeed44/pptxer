import argparse
import logging
from presentations_downloader import scrape_presentations_to_dir
from presentations_text_extractor import extract_presentations_texts

# TODO add argument for sleep timer for scraping
arg_parser = argparse.ArgumentParser(
    description="Extract texts from presentations or scrape presentations "
                "with specific keywords from the internet"
)

subparsers = arg_parser.add_subparsers(dest="subparser_name", help="sub-command help")

parser_extract = subparsers.add_parser(
    "extractor",
    help="Extract body and note text from pptx files",
)
parser_extract.add_argument(
    "presentation_paths",
    nargs="+",
    help="Paths to pptx files or directories containing pptx files",
)

parser_scraper = subparsers.add_parser(
    "scraper",
    help="Scrape the internet looking for presentation files (pptx) that "
         "contains a specific keywords",
)
parser_scraper.add_argument(
    "keywords", nargs="+", help="Search keywords to look for within pptx files"
)
parser_scraper.add_argument(
    "--scrape-destination", help="Destination for storing scraped pptx files", type=str
)
parser_scraper.add_argument(
    "--skip-extract-text",
    help="Download PPTX files off the internet and exit. No extracting texts.",
    action="store_true",
)
for parser in [parser_extract, parser_scraper]:
    parser.add_argument(
        "--extract-output", help="Output text extractions to file (json)", type=str
    )
    parser.add_argument(
        "--single-array-result",
        action="store_false",
        help="if paths is an array, and this is true then results of "
             "extracting texts from different paths will combined into one"
             " array. Otherwise, Have 2D lists of each path result",
    )
    parser.add_argument(
        "--text-fields-flattened",
        action="store_true",
        help="Flatten all text extractions to be one level",
    )
    parser.add_argument(
        "-l",
        "--log",
        dest="logLevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level",
    )

parser_scraper.add_argument(
    "--disable-cache",
    action="store_true",
    help="Download presentations without checking cache to see if they've been"
         " downloaded before",
)
parser_scraper.add_argument(
    "--cache-file",
    help="Specify a cache file to be used. Format is {'path': 'path to pptx "
         "file', 'url': 'url to pptx file'}",
)

args = arg_parser.parse_args()

if args.logLevel:
    logging.basicConfig(level=getattr(logging, args.logLevel))
if args.subparser_name == "extractor":
    presentation_texts = extract_presentations_texts(
        args.presentation_paths,
        args.single_array_result,
        args.text_fields_flattened,
        args.extract_output,
    )
    if args.extract_output is None:
        print(presentation_texts)
elif args.subparser_name == "scraper":
    paths = scrape_presentations_to_dir(
        args.keywords,
        args.scrape_destination,
        None if args.disable_cache else args.cache_file,
    )
    if not args.skip_extract_text:
        presentation_texts = extract_presentations_texts(
            paths,
            args.single_array_result,
            args.text_fields_flattened,
            args.extract_output,
        )
        if args.extract_output is None:
            print(presentation_texts)
    else:
        print(paths)
