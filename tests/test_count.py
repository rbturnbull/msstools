from pathlib import Path
from typer.testing import CliRunner
from msstools.main import app
from msstools.count import greek_char_count, count_greek_chars

import matplotlib
matplotlib.use("Agg")  # Prevent GUI backend during testing

runner = CliRunner()

TEST_DATA = Path(__file__).parent/"testdata"

def test_greek_char_count():
    assert greek_char_count("ἀνθρώπων") == 8
    assert greek_char_count("καὶ λόγος") == 8
    assert greek_char_count("No Greek here!") == 0


def test_count_greek_chars_function(tmp_path):
    # Create fake text files with |F ...| markers and Greek content
    file1 = tmp_path / "file0.txt"
    file1.write_text(
        "|F 1r|\nἀνθρώπων καὶ λόγος\nSome other text\n|F 1v|\nλόγος μόνον\n",
        encoding="utf-8"
    )
    file2 = tmp_path / "file2.txt"
    file2.write_text(
        "|F 2r|\nκαὶ λόγος λόγος λόγος\n|F 2v|\nno greek here\n",
        encoding="utf-8"
    )
    output_path = tmp_path / "plot.png"

    count_greek_chars(str(file1)[:-5], 2, warning_stdev=1.0, output_path=output_path, show=False)

    # Plot should be created
    assert output_path.exists()
    # Plot should be a PNG
    assert output_path.suffix == ".png"


def test_count_greek_chars_cli(tmp_path):
    plot_path = tmp_path / "greek_plot.png"

    result = runner.invoke(app, [
        "count-greek-chars",
        str(TEST_DATA/"X264-H"), 
        "1", 
        "--output", str(plot_path)
    ])
    assert result.exit_code == 0
    assert plot_path.exists()


def test_folio_errors_are_detected(tmp_path, capsys):
    file = tmp_path / "weird_sequence0.txt"
    file.write_text(
        "|F 1r|\nλόγος\n|F 3v|\nπνεῦμα\n",  # 1 → 3 skips folio 2
        encoding="utf-8"
    )

    count_greek_chars(str(file)[:-5], 1, warning_stdev=2.0, output_path=None, show=False)

    captured = capsys.readouterr()
    assert "Folio error from 1r to 3v in file weird_sequence0.txt" in captured.out



def test_compare_counts(tmp_path):

    output_path = tmp_path / "comparison_plot.svg"
    result = runner.invoke(app, [
        "compare-counts",
        str(TEST_DATA/"Base-H"), 
        str(TEST_DATA/"X264-H"), 
        str(output_path),
        "--start-homily", "0",
        "--end-homily", "2",
        "--threshold", "5"
    ])
    assert result.exit_code == 0
    assert output_path.exists()
    stdout = result.stdout.strip()
    assert 'Base Sentence Count: 13\n' in stdout
    assert 'Sentence 1.1.2 not found in comparison text.' in stdout
    assert 'Paragraph 1.3 not found in comparison text.' in stdout
    assert 'Homily 2 not found in comparison text' in stdout
    assert 'Sentence 1.1.1 above the threshold' in stdout
    output_svg = output_path.read_text(encoding='utf-8')
    assert '<?xml version="1.0" encoding="utf-8" ?>\n<svg baseProfile="tiny"' in output_svg
    assert '<rect fill="black" height="10"' in output_svg
    assert '<rect fill="blue" height="10"' in output_svg
    assert '<rect fill="red" height="10"' in output_svg
    assert '<rect fill="green" height="10" width="1" x="0"' in output_svg

