# Presentations Scraper: A fast high-level Presentations Scraper for Python and Command Line

This project is made to make it as easy as possible to scrape presentations (pptx files) from the internet and extract their text (body and notes). There are two modes:
- Downloader
- Extractor

### Downloader
This mode scrapes presentations files that contains a specific keywords from search engines based, and downloads them to a directory. The texts within these files will be extracted automatically unless otherwise specified.

### Extractor
This mode extracts texts from pptx files and outputs a dict with each slide body and note texts. If command line is used then a json file will be outputted.

For example, command ```python presentations_scraper.py extractor test.pptx``` will result
```
[{
'path': 'test.pptx', 
'slides': [
            {'noteText': 'Note Line 1\nNote Line 2', 'bodyText': 'Label Test 1Body Line 1\nBody Line 2'}, 
            {'noteText': 'Note Line 1\nNote Line2', 'bodyText': ''}], 
            'bodyTextLengthStats': {'totalLength': 35, 'avgLength': 17.5, 'minLength': 0, 'maxLength': 35, 'medianLength': 17.5}, 
            'noteTextLengthStats': {'totalLength': 45, 'avgLength': 22.5, 'minLength': 22, 'maxLength': 23, 'medianLength': 22.5}
}]
```

## Installation
TODO

## How to use
TODO add import module
- To download pptx files that contain specific keywords
    - Python
    ```
  search_keywords = ["I love", "hoarding"]
  # download_dir_path is optional. If skipped, then a directory with search keywords splitted by "_" will be created
  paths_to_files = scrape_presentations_to_dir(search_keywords, download_dir_path="test_dir")
  ```
    - Command line
    ```
  
  ```
  
## Issues
Feel free to open an issue if you have any problems.

