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
    force: bool = False,
):
    """
    Split an image into recto and verso parts.
    """
    counter = start

    recto_marker = "r" if recto_verso else ""
    verso_marker = "v" if recto_verso else ""

    prefix = Path(prefix)
    prefix.parent.mkdir(parents=True, exist_ok=True)

    for image_path in images:
        suffix = image_path.suffix
        if counter <= skip:
            # copy image to final location without splitting
            path = prefix.parent / f"{prefix.name}-{counter}{suffix}"
            if not path.exists() or force:
                shutil.copy(image_path, prefix.parent / f"{prefix.name}-{counter}{suffix}")
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

            verso_path = prefix.parent / f"{prefix.name}-{counter}{verso_marker}{suffix}"
            counter += 1
            recto_path = prefix.parent / f"{prefix.name}-{counter}{recto_marker}{suffix}"

            if not recto_verso:
                counter += 1

            if not verso_path.exists() or force:
                verso_img.save(verso_path)
            if not recto_path.exists() or force:
                recto_img.save(recto_path)
