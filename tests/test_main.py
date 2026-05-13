from importlib.metadata import version
from pathlib import Path

import matplotlib
import pikepdf
from PIL import Image
from typer.testing import CliRunner

from msstools.main import app


matplotlib.use("Agg")

runner = CliRunner()
TEST_DATA = Path(__file__).parent / "testdata"


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


def test_split_images_command(tmp_path):
    image = create_test_image(tmp_path / "page.jpg")

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "split"),
            str(image),
            "--recto",
            "page.jpg=49",
        ],
    )

    assert result.exit_code == 0
    assert (tmp_path / "split-0.jpg").exists()
    assert (tmp_path / "split-1-49r.jpg").exists()


def test_split_images_command_rejects_invalid_recto_anchor(tmp_path):
    image = create_test_image(tmp_path / "page.jpg")

    result = runner.invoke(
        app,
        [
            "split-images",
            str(tmp_path / "split"),
            str(image),
            "--recto",
            "page.jpg",
        ],
    )

    assert result.exit_code != 0
    assert "Invalid recto reference 'page.jpg'. Expected FILENAME=FOLIO." in str(
        result.exception
    )


def test_remove_accents_command(tmp_path):
    input_file = tmp_path / "with_accents.txt"
    output_file = tmp_path / "without_accents.txt"
    input_file.write_text("Καλημέρα, πῶς εἶσαι;\n", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "remove-accents",
            str(input_file),
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.read_text(encoding="utf-8") == "Καλημερα, πως εισαι;\n"


def test_number_sentences_command(tmp_path):
    input_file = tmp_path / "input.xml"
    output_file = tmp_path / "output.xml"
    input_file.write_text("<P>\n<S>A.</S>\n<S>B.</S>\n</P>", encoding="utf-8")

    result = runner.invoke(
        app,
        [
            "number-sentences",
            str(input_file),
            str(output_file),
        ],
    )

    assert result.exit_code == 0
    assert output_file.read_text(encoding="utf-8") == "<P>\n<S 1>A.</S>\n<S 2>B.</S>\n</P>"


def test_count_greek_chars_command(tmp_path):
    plot_path = tmp_path / "greek_plot.png"

    result = runner.invoke(
        app,
        [
            "count-greek-chars",
            str(TEST_DATA / "X264-H"),
            "--end-homily",
            "1",
            "--output",
            str(plot_path),
        ],
    )

    assert result.exit_code == 0
    assert "Mean:                41.0" in result.stdout
    assert "Standard Deviation:  56.1" in result.stdout
    assert "Folio side error from 72r to 73r in file X264-H0.txt" in result.stdout
    assert plot_path.exists()


def test_compare_counts_command(tmp_path):
    output_path = tmp_path / "comparison_plot.svg"

    result = runner.invoke(
        app,
        [
            "compare-counts",
            str(TEST_DATA / "Base-H"),
            str(TEST_DATA / "X264-H"),
            "--output-svg",
            str(output_path),
            "--start-homily",
            "0",
            "--end-homily",
            "2",
            "--threshold",
            "5",
        ],
    )

    assert result.exit_code == 0
    assert output_path.exists()
    assert "Base Sentence Count: 13\n" in result.stdout
    assert "Sentence 1.1.2 not found in comparison text." in result.stdout


def test_csv_to_tei_command(tmp_path):
    output_file = tmp_path / "output-tei.xml"

    result = runner.invoke(
        app,
        [
            "csv-to-tei",
            str(TEST_DATA / "demo-readings.csv"),
            str(output_file),
            "--dates",
            str(TEST_DATA / "demo-dates.csv"),
        ],
    )

    assert result.exit_code == 0
    output_data = output_file.read_text()
    assert output_data.startswith('<TEI xmlns="http://www.tei-c.org/ns/1.0">\n\t<teiHeader>')
    assert '<origDate notBefore="200" notAfter="299" />' in output_data
    assert "Witness C not in dates" in result.stdout
