from importlib.metadata import version
from pathlib import Path

import pikepdf
from PIL import Image
from typer.testing import CliRunner

from msstools.main import app


runner = CliRunner()


def create_test_image(path: Path, color=(255, 0, 0)) -> Path:
    image = Image.new("RGB", (20, 20), color=color)
    image.save(path)
    return path


def outline_titles(pdf_path: Path) -> list[str]:
    pdf = pikepdf.Pdf.open(pdf_path)
    with pdf.open_outline() as outline:
        return [item.title for item in outline.root]


def test_cite_command():
    result = runner.invoke(app, ["cite"])
    output = " ".join(result.stdout.split())

    assert result.exit_code == 0
    assert "Montoro, Peter, and Robert Turnbull." in output
    assert "Tools, Tricks, and Techniques" in output
    assert "Comparative Oriental Manuscript Studies Bulletin" in output
    assert "10.25592/uhhfdm.18366" in output


def test_bibtex_command():
    result = runner.invoke(app, ["bibtex"])

    assert result.exit_code == 0
    assert "@article{msstools," in result.stdout
    assert "author = {Montoro, Peter and Turnbull, Robert}" in result.stdout
    assert "doi = {10.25592/uhhfdm.18366}" in result.stdout


def test_version_command():
    result = runner.invoke(app, ["version"])

    assert result.exit_code == 0
    assert result.stdout.strip() == version("msstools")


def test_combine_command(tmp_path):
    image1 = create_test_image(tmp_path / "Stavros26-000-1r.jpg", color=(255, 0, 0))
    image2 = create_test_image(tmp_path / "Stavros26-001-1v.jpg", color=(0, 255, 0))
    output_pdf = tmp_path / "combined.pdf"

    result = runner.invoke(
        app,
        [
            "combine",
            str(image1),
            str(image2),
            str(output_pdf),
            "--strip-pattern",
            r"^Stavros26-\d+-",
        ],
    )

    assert result.exit_code == 0
    assert output_pdf.exists()
    with pikepdf.Pdf.open(output_pdf) as pdf:
        assert len(pdf.pages) == 2
    assert outline_titles(output_pdf) == ["1r", "1v"]
