from pathlib import Path
import shutil
from PIL import Image


def split_images(
    prefix: Path,
    images: list[Path],
    rtl: bool = False,
    overlap: float = 10.0,
    skip: int = 0,
    margin_left: int = 0,
    margin_right: int = 0,
    force: bool = False,
    recto: list[str] | None = None,
):
    """
    Split images into left and right parts.
    """
    recto_by_image = _parse_recto_refs(recto)
    output_index = 0
    output_width = _number_width(images_count=len(images), skip=skip)
    current_folio: int | None = None

    prefix = Path(prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)

    for image_index, image_path in enumerate(images):
        suffix = image_path.suffix
        if image_index < skip:
            path = _output_path(prefix, output_index, output_width, "", suffix)
            if not path.exists() or force:
                shutil.copy(image_path, path)
            output_index += 1
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

            verso_ref = f"-{current_folio}v" if current_folio is not None else ""
            verso_path = _output_path(
                prefix, output_index, output_width, verso_ref, suffix
            )
            print("\tVerso", verso_path)
            output_index += 1

            recto_folio = recto_by_image.get(image_path.name)
            if recto_folio is None and current_folio is not None:
                recto_folio = current_folio + 1

            recto_ref = f"-{recto_folio}r" if recto_folio is not None else ""
            recto_path = _output_path(
                prefix, output_index, output_width, recto_ref, suffix
            )
            print("\tRecto", recto_path)
            output_index += 1

            if recto_folio is not None:
                current_folio = recto_folio

            if not verso_path.exists() or force:
                verso_img.save(verso_path)
            if not recto_path.exists() or force:
                recto_img.save(recto_path)


def _parse_recto_refs(recto: list[str] | None = None) -> dict[str, int]:
    recto_by_image: dict[str, int] = {}
    for value in recto or []:
        try:
            filename, folio = value.split("=", 1)
            recto_by_image[Path(filename).name] = int(folio)
        except ValueError as error:
            raise ValueError(
                f"Invalid recto reference {value!r}. Expected FILENAME=FOLIO."
            ) from error

    return recto_by_image


def _number_width(images_count: int, skip: int) -> int:
    output_count = min(skip, images_count) + max(0, images_count - skip) * 2
    highest_index = max(0, output_count - 1)
    return len(str(highest_index))


def _format_number(number: int, width: int) -> str:
    return f"{number:0{width}d}"


def _output_path(
    prefix: Path,
    output_index: int,
    output_width: int,
    folio_ref: str,
    suffix: str,
) -> Path:
    number = _format_number(output_index, output_width)
    return prefix.parent / f"{prefix.name}-{number}{folio_ref}{suffix}"
