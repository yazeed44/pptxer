# PPTXER: A fast high-level Presentations Scraper for Python and Command Line

This project is made to make it as easy as possible to scrape presentations (pptx files) from the internet and extract their text (body and notes). It can be used in Python or command line.
## Installation
```shell
pip install pptxer
```
Verify installation by running  
```shell
pptxer --version
```
### Downloader
This mode scrapes presentations  that contains a specific keywords from search engines, and downloads them to a directory. The texts within these files will be extracted automatically unless otherwise specified.

- To download pptx files that contain "COVID-19 Safety" and "Contagious diseases" to directory `test_dir`
    - Python
    ```
  from pptxer.presentations_downloader import scrape_presentations_to_dir

  search_keywords = ["COVID-19 Safety", "Contagious diseases"]
  # If download_dir_path is skipped, then a directory with search keywords splitted by "_" will be created
  paths_to_files = scrape_presentations_to_dir(search_keywords, download_dir_path="test_dir")
  # For this example, a directory with name "test_dir" will be created, and files will be written to it
  ```
    - Command line
    ```shell
      # This will download presentations to test_dir and extract their texts to a json file
      pptxer download "COVID-19 Safety" "Contagious diseases" --dst test_dir
      # To only download
      pptxer download "COVID-19 Safety" "Contagious diseases" --dst test_dir --no-extract-text
  ```
### Extractor
This mode extracts texts from pptx files and outputs a dict with each slide body and note texts. If command line is used then a json file will be outputted.


- To extract text from presentation files (pptx) or loop through presentation files within a directory
    - Python
    ```python
    # Single file
  texts = extract_presentations_texts(["directory/test.pptx"])

  # Directory. Will scan the directory for pptx file, extract their texts and return them
  texts = extract_presentations_texts(["directory/"])

  # Combined file and directory
  texts = extract_presentations_texts(["directory/", "directory2/test.pptx"])
  ```
    - Command line
    ```shell
  # Single file
  pptxer extract directory/test.pptx
  # Directory
  pptxer extract directory/
  # File and directory
  pptxer extract directory1 directory2/test.pptx
  
  ```
  The output will be similar to the following:
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

## Rate Limit
As of now, we're using third-party search engines to look up files, and almost all search engines throttle or soft ban if they detected automated queries coming from your IP. The soft ban usually lasts about a day, and you will not be able to use `pptxer` in meanwhile, but you can use any search engines on your browser normally. 

  
## Issues
Feel free to open an issue if you have any problems.
