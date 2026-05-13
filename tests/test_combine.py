from pathlib import Path

import pikepdf
import pytest
from PIL import Image

from msstools.combine import create_pdf


def create_test_image(path: Path, color=(255, 0, 0)) -> Path:
    image = Image.new("RGB", (20, 20), color=color)
    image.save(path)
    return path


def outline_titles(pdf_path: Path) -> list[str]:
    pdf = pikepdf.Pdf.open(pdf_path)
    with pdf.open_outline() as outline:
        return [item.title for item in outline.root]


def test_create_pdf_combines_images_with_filename_outline(tmp_path):
    images = [
        create_test_image(tmp_path / "folio-001r.jpg", color=(255, 0, 0)),
        create_test_image(tmp_path / "folio-001v.jpg", color=(0, 255, 0)),
    ]
    output_pdf = tmp_path / "combined" / "output.pdf"

    create_pdf(images, output_pdf)

    assert output_pdf.exists()
    with pikepdf.Pdf.open(output_pdf) as pdf:
        assert len(pdf.pages) == 2
    assert outline_titles(output_pdf) == ["folio-001r", "folio-001v"]


def test_create_pdf_strips_pattern_from_outline_labels(tmp_path):
    images = [
        create_test_image(tmp_path / "Stavros26-000-1r.jpg", color=(255, 0, 0)),
        create_test_image(tmp_path / "Stavros26-001-1v.jpg", color=(0, 255, 0)),
    ]
    output_pdf = tmp_path / "output.pdf"

    create_pdf(images, output_pdf, strip_pattern=r"^Stavros26-\d+-")

    assert outline_titles(output_pdf) == ["1r", "1v"]


def test_create_pdf_rejects_empty_image_list(tmp_path):
    with pytest.raises(ValueError, match="No image paths provided"):
        create_pdf([], tmp_path / "output.pdf")
