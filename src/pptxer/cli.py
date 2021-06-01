import logging

import click
from pptxer import __version__
from pptxer.presentations_downloader import scrape_presentations_to_dir
from pptxer.presentations_text_extractor import extract_presentations_texts


@click.group()
@click.version_option(version=__version__)
@click.option("--extracted-text-dst", help="Output text extractions to file (json)",
              type=click.Path(file_okay=True, dir_okay=False))
@click.option("--extracted-text-single-array/--no-extracted-text-single-array", default=True,
              help="if paths is an array, and this is true then results of "
                   "extracting texts from different paths will combined into one"
                   " array. Otherwise, Have 2D lists of each path result""")
@click.option("--flatten-extracted-text/--no-flatten-extracted-text", default=False,
              help="Flatten all text extractions to be one level")
@click.option("--verbosity", "-v",
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"], case_sensitive=False))
@click.pass_context
def cli(ctx, extracted_text_dst, extracted_text_single_array, flatten_extracted_text, verbosity):
    ctx.ensure_object(dict)
    ctx.obj["extracted_text_dst"] = extracted_text_dst
    ctx.obj["extracted_text_single_array"] = extracted_text_single_array
    ctx.obj["flatten_extracted_text"] = flatten_extracted_text

    if verbosity:
        logging.basicConfig(level=getattr(logging, verbosity.upper(), "NOTSET"))
    pass


@cli.command("download")
@click.pass_context
@click.argument("keywords", nargs=-1)
@click.option("--dst", help="Destination for storing downloaded pptx files",
              type=click.Path(exists=False, file_okay=False, dir_okay=True, writable=True, readable=True))
@click.option("--should-extract-text/--no-extract-text", default=True,
              help="Do not extract text of pptx files. Download files and exit.")
def download(ctx, keywords, dst, should_extract_text):
    extracted_text_dst, extracted_text_single_array, flatten_extract_text = ctx.obj.values()
    paths = scrape_presentations_to_dir(keywords, dst)
    if should_extract_text:
        __extract__(paths, extracted_text_dst, extracted_text_single_array, flatten_extract_text)
    else:
        click.echo(paths)


@cli.command()
@click.pass_context
@click.argument("pptx_paths", nargs=-1, type=click.Path(exists=True, file_okay=True, dir_okay=True))
def extract(ctx, pptx_paths):
    extracted_text_dst, extracted_text_single_array, flatten_extract_text = ctx.obj.values()
    __extract__(pptx_paths, extracted_text_dst, extracted_text_single_array, flatten_extract_text)


def __extract__(pptx_paths, extracted_text_dst, extracted_text_single_array, flatten_extract_text):
    if len(pptx_paths) == 0:
        click.echo("No paths were provided. exiting...")
        return
    texts = extract_presentations_texts(pptx_paths, single_array_result=extracted_text_single_array,
                                        text_fields_flattened=flatten_extract_text,
                                        extract_output_file_path=extracted_text_dst)
    if extracted_text_dst is None:
        click.echo(texts)
    else:
        click.echo(f"Extracted texts to {extracted_text_dst}")


def main():
    cli()


if __name__ == "__main__":
    main()
