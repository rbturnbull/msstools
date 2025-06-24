from pathlib import Path
import typer


app = typer.Typer()

@app.command()
def split_images(
    prefix: Path = typer.Argument(..., help="Path to the image file to be split"),
    images: list[Path] = typer.Argument(..., help="List of image files to be split"),
    rtl: bool = typer.Option(False, help="Split images in right-to-left direction"),
    overlap: float = typer.Option(10, help="Overlap percentage between split images"),
    start: int = typer.Option(1, help="The folio number for the first image"),
    skip: int = typer.Option(0, help="Number of pages to skip before splitting"),
    recto_verso: bool = typer.Option(True, help="Use 'r' and 'v' suffixes for recto and verso pages. Otherwise it uses sequential pagination."),
    force: bool = typer.Option(False, help="Force overwrite existing files"),
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
        start=start,
        skip=skip,
        recto_verso=recto_verso,
        force=force,
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