from pathlib import Path
import typer


app = typer.Typer()

@app.command()
def split_images(
    prefix: Path = typer.Argument(..., help="Path to the image file to be split"),
    images: list[Path] = typer.Argument(..., help="List of image files to be split"),
    rtl: bool = typer.Option(False, help="Split images in right-to-left direction"),
    overlap: float = typer.Option(10, help="Overlap percentage between split images"),
    skip: int = typer.Option(0, help="Number of pages to skip before splitting"),
    margin_left: int = typer.Option(0, help="Margin to remove from the left side of the image before splitting"),
    margin_right: int = typer.Option(0, help="Margin to remove from the right side of the image before splitting"),
    force: bool = typer.Option(False, help="Force overwrite existing files"),
    recto: list[str] | None = typer.Option(None, help="Recto folio anchors in the form FILENAME=FOLIO"),
    ignore: list[str] | None = typer.Option(None, help="List of image filenames to ignore"),
):
    """
    Split an image into recto and verso parts.
    """
    from msstools.split import split_images
    split_images(
        prefix=prefix,
        images=images,
        rtl=rtl,
        overlap=overlap,
        skip=skip,
        margin_left=margin_left,
        margin_right=margin_right,
        force=force,
        recto=recto,
        ignore=ignore,
    )


@app.command()
def remove_accents(
    input_file: Path = typer.Argument(..., help="Path to the input file"),
    output_file: Path = typer.Argument(..., help="Path to the output file"),
):
    """
    Remove accents from a text file.
    """
    from msstools.strings import remove_accents_from_file
    remove_accents_from_file(input_file, output_file)


@app.command()
def number_sentences(
    input_file: Path = typer.Argument(..., help="Path to the input file"),
    output_file: Path = typer.Argument(..., help="Path to the output file"),
):
    """
    Number <S> sentence tags within <P> blocks in a text file.
    """
    from msstools.number import number_sentences
    input_data = Path(input_file).read_text(encoding='utf-8')
    output_data = number_sentences(input_data)
    Path(output_file).write_text(output_data, encoding='utf-8')


@app.command()
def count_greek_chars(
    filename_prefix:str = typer.Argument(..., help="Prefix for the output files"),
    start_homily:int= typer.Option(0, help="The number of the homily to start with"),
    end_homily:int = typer.Option(32, help="The number of the homily to end with"),
    warning_stdev:float = typer.Option(1.8, help="Standard deviation threshold for warnings"),
    output:Path = typer.Option(None, help="Path to save the output plot"),
    show:bool = typer.Option(False, help="Show the plot in a window"),
):
    """
    Count Greek characters in text files and generate a plot.
    """
    from msstools.count import count_greek_chars
    count_greek_chars(
        filename_prefix=filename_prefix, 
        start_homily=start_homily,
        end_homily=end_homily,
        warning_stdev=warning_stdev, 
        output_path=output, 
        show=show,
    )


@app.command()
def compare_counts(
    base_prefix:str = typer.Argument(..., help="The prefix for files of the base text"),
    comparison_prefix:str = typer.Argument(..., help="The prefix for files of the comparison text"),
    output_svg:Path = typer.Option(None, help="Path to save the output as an SVG file"),
    start_homily:int= typer.Option(0, help="The number of the homily to start with"),
    end_homily:int = typer.Option(32, help="The number of the homily to end with"),
    threshold:int = typer.Option(50, help="The number of characters which the comparison text sentence can be above the base text sentence before triggering the warning indication"),
):
    """ Compares homily transcriptions with a base text and visualizes where text is missing """
    from msstools.count import compare_counts
    compare_counts(
        base_prefix=base_prefix,
        comparison_prefix=comparison_prefix,
        output_svg=output_svg,
        start_homily=start_homily,
        end_homily=end_homily,
        threshold=threshold,
    )


@app.command()
def csv_to_tei(
    input_csv:Path=typer.Argument(..., help="The path to the input CSV file containing readings"),
    output_xml:Path=typer.Argument(..., help="The path to the output XML file"),
    dates:Path=typer.Option(None, help="Optional path to a file containing dates"),
    max_readings:int=typer.Option(0, help="Maximum number of readings to process at each variation unit"),
):
    """ Convert a CSV file of readings into TEI XML format."""
    from msstools.tei import csv_to_tei

    csv_to_tei(
        input_csv=input_csv,
        output_xml=output_xml,
        dates=dates,
        max_readings=max_readings,
    )


@app.command()
def combine(
    image_paths: list[Path] = typer.Argument(..., help="List of image paths to combine into a PDF"),
    output_pdf: Path = typer.Argument(..., help="Path to the output PDF file"),
    strip_pattern: str = typer.Option("", help="Optional regex pattern to ignore in folio labels"),
):
    """ Combine a list of images into a PDF with an outline based on the image filenames."""
    from msstools.combine import create_pdf

    create_pdf(
        image_paths=image_paths,
        output_pdf=output_pdf,
        strip_pattern=strip_pattern,
)
    

@app.command()
def cite():
    """ 
    Display the citation for this software. If you use this software in your research, please cite the article.
    """
    from rich import print

    print(
        "Montoro, Peter, and Robert Turnbull. [green]“Tools, Tricks, and Techniques: Managing the Manuscripts of Chrysostom’s Homilies on Romans.”[/] " \
        "[red]Comparative Oriental Manuscript Studies Bulletin[/] 11 (2025): 265–88. [purple]DOI: 10.25592/uhhfdm.18366[/]",
    )


@app.command()
def bibtex():
    """ Display the BibTeX entry for this software."""
    from rich import print

    bibtex = Path(__file__).parent / "msstools.bib"
    print(bibtex.read_text(encoding='utf-8'))


@app.command()
def version():
    """ Display the version of this software. """
    from importlib.metadata import version
    from rich import print
    print(version("msstools"))