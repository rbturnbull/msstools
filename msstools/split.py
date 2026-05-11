from pathlib import Path
import shutil
from PIL import Image


def split_images(
    prefix: Path,
    images: list[Path],
    rtl: bool = False,
    overlap: float = 10.0,
    start: int = 0,
    skip: int = 0,
    recto_verso: bool = True,
    margin_left: int = 0,
    margin_right: int = 0,
    force: bool = False,
    duplicates: list[int] | None = None,
):
    """
    Split an image into recto and verso parts.
    """
    duplicates = duplicates or []
    folio = _folio_label(start, duplicates)
    padding_width = _number_width(
        start=start,
        images_count=len(images),
        skip=skip,
        recto_verso=recto_verso,
        duplicates=duplicates,
    )

    recto_marker = "r" if recto_verso else ""
    verso_marker = "v" if recto_verso else ""

    prefix = Path(prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)

    for index, image_path in enumerate(images):
        suffix = image_path.suffix
        if index < skip:
            # copy image to final location without splitting
            page_number = _format_number(index, padding_width)
            path = prefix.parent / f"{prefix.name}--{page_number}{suffix}"
            if not path.exists() or force:
                shutil.copy(image_path, path)
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

            verso_number = _format_number(folio.number, padding_width)
            verso_duplicate = _duplicate_suffix(folio)
            verso_path = (
                prefix.parent
                / f"{prefix.name}-f{verso_number}{verso_marker}{verso_duplicate}{suffix}"
            )
            print("\tVerso", verso_path)
            folio = _next_folio(folio, duplicates)
            recto_number = _format_number(folio.number, padding_width)
            recto_duplicate = _duplicate_suffix(folio)
            recto_path = (
                prefix.parent
                / f"{prefix.name}-f{recto_number}{recto_marker}{recto_duplicate}{suffix}"
            )
            print("\tRecto", recto_path)

            if not recto_verso:
                folio = _next_folio(folio, duplicates)

            if not verso_path.exists() or force:
                verso_img.save(verso_path)
            if not recto_path.exists() or force:
                recto_img.save(recto_path)


def _number_width(
    start: int,
    images_count: int,
    skip: int,
    recto_verso: bool,
    duplicates: list[int] | None = None,
) -> int:
    """
    Return the width needed to zero-pad all output page numbers for a run.
    """
    split_count = max(0, images_count - skip)
    highest_number = max(start, skip - 1)

    if split_count:
        if recto_verso:
            final_folio = _advance_folio(
                _folio_label(start, duplicates),
                split_count,
                duplicates,
            )
            highest_number = max(highest_number, final_folio.number)
        else:
            final_folio = _advance_folio(
                _folio_label(start, duplicates),
                (split_count * 2) - 1,
                duplicates,
            )
            highest_number = max(highest_number, final_folio.number)

    return len(str(highest_number))


def _format_number(number: int, width: int) -> str:
    return f"{number:0{width}d}"


class FolioLabel:
    def __init__(self, number: int, duplicate_index: int = 0):
        self.number = number
        self.duplicate_index = duplicate_index


def _folio_label(number: int, duplicates: list[int] | None = None) -> FolioLabel:
    duplicates = duplicates or []
    duplicate_index = 0 if number in duplicates else -1
    return FolioLabel(number=number, duplicate_index=duplicate_index)


def _next_folio(folio: FolioLabel, duplicates: list[int] | None = None) -> FolioLabel:
    duplicates = duplicates or []
    if folio.number in duplicates and folio.duplicate_index == 0:
        return FolioLabel(number=folio.number, duplicate_index=1)

    return _folio_label(folio.number + 1, duplicates)


def _advance_folio(
    folio: FolioLabel,
    count: int,
    duplicates: list[int] | None = None,
) -> FolioLabel:
    for _ in range(count):
        folio = _next_folio(folio, duplicates)
    return folio


def _duplicate_suffix(folio: FolioLabel) -> str:
    if folio.duplicate_index >= 0:
        return chr(ord("A") + folio.duplicate_index)

    return ""
