from pathlib import Path
import shutil
from PIL import Image
import typer


app = typer.Typer()

@app.command()
def split_image(
    prefix: Path = typer.Argument(..., help="Path to the image file to be split"),
    images: list[Path] = typer.Argument(..., help="List of image files to be split"),
    rtl: bool = typer.Option(False, help="Split images in right-to-left direction"),
    overlap: float = typer.Option(10, help="Overlap percentage between split images"),
    skip: int = typer.Option(0, help="Number of pages to skip before splitting"),
    force: bool = typer.Option(False, help="Force overwrite existing files"),
):
    """
    Split an image into recto and verso parts.
    """
    counter = 0
    for image_path in images:
        if counter < skip:
            # copy image to final location without splitting
            path = prefix.parent / f"{prefix.name}-{counter}.jpg"
            if not path.exists() or force:
                shutil.copy(image_path, prefix.parent / f"{prefix.name}-{counter}.jpg")
            counter += 1
            continue
        
        print(f"Splitting {image_path.name}")
        with Image.open(image_path) as img:
            width, height = img.size
            overlap_px = int(width * (overlap / 100.0))
            half = width // 2

            # The overlap is centered around the midpoint
            left_crop = (0, 0, half + overlap_px // 2, height)
            right_crop = (half - overlap_px // 2, 0, width, height)

            if rtl:
                verso_img = img.crop(right_crop)
                recto_img = img.crop(left_crop) 
            else:
                verso_img = img.crop(left_crop) 
                recto_img = img.crop(right_crop)

            verso_path = prefix.parent / f"{prefix.name}-{counter}v.jpg"
            counter += 1
            recto_path = prefix.parent / f"{prefix.name}-{counter}r.jpg"

            if not verso_path.exists() or force:
                verso_img.save(verso_path)
            if not recto_path.exists() or force:
                recto_img.save(recto_path)


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
    paths:list[Path] = typer.Argument(..., help="Paths to text files to count Greek characters"),
    warning_stds:float = typer.Option(1.8, help="Standard deviation threshold for warnings"),
    output_path:Path = typer.Option(None, help="Path to save the output plot"),
    show:bool = typer.Option(False, help="Show the plot in a window"),
):
    """
    Count Greek characters in text files and generate a plot.
    """
    from msstools.count import count_greek_chars
    count_greek_chars(paths, warning_stds, output_path, show)