from presentations_text_extractor import extract_presentations_texts
import argparse

# TODO add verbose
# TODO add argument for sleep timer for scraping
arg_parser = argparse.ArgumentParser(
    description="Extract texts from presentations or scrape presentations with specific keywords from the internet")

subparsers = arg_parser.add_subparsers(dest="subparser_name", help="sub-command help")

parser_extract = subparsers.add_parser('extractor', help="Extract body and note text from pptx files",
                                       )
parser_extract.add_argument("presentation_paths", nargs='+',
                            help="Paths to pptx files or directories containing pptx files")

parser_scraper = subparsers.add_parser('scraper',
                                       help="Scrape the internet looking for presentation files (pptx) that contains a specific keywords",
                                       )
parser_scraper.add_argument('keywords', nargs='+', help="Keywords to look for")
parser_scraper.add_argument('--scrape-destination', default=".", help="Destination for storing scraped pptx files",
                            type=str)
parser_scraper.add_argument("--extract-text", help="Extract text after scraping", action="store_true")

for parser in [parser_extract, parser_scraper]:
    parser.add_argument("--single-array-result", action="store_false",
                        help="if paths is an array, and this is true then results of extracting texts from different paths will combined into one array. Otherwise, Have 2D lists of each path result")
    parser.add_argument("--text-fields-flattened", action="store_true",
                        help="Flatten all text extractions to be one level")
    parser.add_argument("--extract-output", help="Output text extractions to file (json)", type=str)

args = arg_parser.parse_args()
if args.subparser_name == 'extractor':
    presentation_texts = extract_presentations_texts(args.presentation_paths, args.single_array_result,
                                                     args.text_fields_flattened,
                                                     args.extract_output)
    if args.extract_output is None:
        print(presentation_texts)
