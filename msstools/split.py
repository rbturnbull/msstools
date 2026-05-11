from pathlib import Path
import shutil
from PIL import Image


def split_images(
    prefix: Path,
    images: list[Path],
    rtl: bool = False,
    overlap: float = 10.0,
    start: int = 1,
    skip: int = 0,
    recto_verso: bool = True,
    margin_left: int = 0,
    margin_right: int = 0,
    force: bool = False,
):
    """
    Split an image into recto and verso parts.
    """
    counter = start
    padding_width = _number_width(
        start=start,
        images_count=len(images),
        skip=skip,
        recto_verso=recto_verso,
    )

    recto_marker = "r" if recto_verso else ""
    verso_marker = "v" if recto_verso else ""

    prefix = Path(prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)

    for index, image_path in enumerate(images):
        suffix = image_path.suffix
        if index < skip:
            # copy image to final location without splitting
            page_number = _format_number(counter, padding_width)
            path = prefix.parent / f"{prefix.name}-{page_number}{suffix}"
            if not path.exists() or force:
                shutil.copy(image_path, path)
            counter += 1
            continue

        print(f"Splitting {image_path.name}")
        with Image.open(image_path) as img:
            if margin_left or margin_right:
                width, height = img.size
                img = img.crop((margin_left, 0, width - margin_right, height))

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

            verso_number = _format_number(counter, padding_width)
            verso_path = (
                prefix.parent / f"{prefix.name}-{verso_number}{verso_marker}{suffix}"
            )
            print("\tVerso", verso_path)
            counter += 1
            recto_number = _format_number(counter, padding_width)
            recto_path = (
                prefix.parent / f"{prefix.name}-{recto_number}{recto_marker}{suffix}"
            )
            print("\tRecto", recto_path)

            if not recto_verso:
                counter += 1

            if not verso_path.exists() or force:
                verso_img.save(verso_path)
            if not recto_path.exists() or force:
                recto_img.save(recto_path)


def _number_width(start: int, images_count: int, skip: int, recto_verso: bool) -> int:
    """
    Return the width needed to zero-pad all output page numbers for a run.
    """
    counter = start
    highest_number = start

    for index in range(images_count):
        if index < skip:
            highest_number = max(highest_number, counter)
            counter += 1
            continue

        highest_number = max(highest_number, counter)
        counter += 1
        highest_number = max(highest_number, counter)

        if not recto_verso:
            counter += 1

    return len(str(highest_number))


def _format_number(number: int, width: int) -> str:
    return f"{number:0{width}d}"
