from typer.testing import CliRunner
from msstools.main import app
from msstools.count import greek_char_count, count_greek_chars

import matplotlib
matplotlib.use("Agg")  # Prevent GUI backend during testing

runner = CliRunner()

def test_greek_char_count():
    assert greek_char_count("ἀνθρώπων") == 8
    assert greek_char_count("καὶ λόγος") == 8
    assert greek_char_count("No Greek here!") == 0

def test_count_greek_chars_function(tmp_path):
    # Create fake text files with |F ...| markers and Greek content
    file1 = tmp_path / "file1.txt"
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

    count_greek_chars([file1, file2], warning_stds=1.0, output_path=output_path, show=False)

    # Plot should be created
    assert output_path.exists()
    # Plot should be a PNG
    assert output_path.suffix == ".png"

def test_count_greek_chars_cli(tmp_path):
    # Input text file with |F markers and Greek characters
    file = tmp_path / "file.txt"
    file.write_text(
        "|F 71r|\nλόγος καὶ πνεῦμα\n|F 71v|\nὕδωρ\n|F 72r|\nἄνθρωπος\n",
        encoding="utf-8"
    )
    plot_path = tmp_path / "greek_plot.png"

    result = runner.invoke(app, [
        "count-greek-chars",
        str(file),
        "--output-path", str(plot_path)
    ])

    assert result.exit_code == 0
    assert plot_path.exists()

def test_folio_errors_are_detected(tmp_path, capsys):
    file = tmp_path / "weird_sequence.txt"
    file.write_text(
        "|F 1r|\nλόγος\n|F 3v|\nπνεῦμα\n",  # 1 → 3 skips folio 2
        encoding="utf-8"
    )

    count_greek_chars([file], warning_stds=2.0, output_path=None, show=False)

    captured = capsys.readouterr()
    assert "Folio error from 1r to 3v in file weird_sequence.txt" in captured.out
