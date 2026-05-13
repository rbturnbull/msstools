from pathlib import Path

import matplotlib

from msstools.count import compare_counts, count_greek_chars, greek_char_count

matplotlib.use("Agg")

TEST_DATA = Path(__file__).parent / "testdata"


def test_greek_char_count():
    assert greek_char_count("ἀνθρώπων") == 8
    assert greek_char_count("καὶ λόγος") == 8
    assert greek_char_count("No Greek here!") == 0


def test_count_greek_chars_function(tmp_path):
    file1 = tmp_path / "file0.txt"
    file1.write_text(
        "|F 1r|\nἀνθρώπων καὶ λόγος\nSome other text\n|F 1v|\nλόγος μόνον\n",
        encoding="utf-8",
    )
    file2 = tmp_path / "file2.txt"
    file2.write_text(
        "|F 2r|\nκαὶ λόγος λόγος λόγος\n|F 2v|\nno greek here\n",
        encoding="utf-8",
    )
    output_path = tmp_path / "dummy" / "plot.png"

    count_greek_chars(
        str(file1)[:-5],
        end_homily=2,
        warning_stdev=1.0,
        output_path=output_path,
        show=False,
    )

    assert output_path.exists()
    assert output_path.suffix == ".png"


def test_count_greek_chars_on_test_data(tmp_path, capsys):
    plot_path = tmp_path / "greek_plot.png"

    count_greek_chars(
        str(TEST_DATA / "X264-H"),
        end_homily=1,
        output_path=plot_path,
    )

    captured = capsys.readouterr()
    assert "Mean:                41.0" in captured.out
    assert "Standard Deviation:  56.1" in captured.out
    assert "Folio side error from 72r to 73r in file X264-H0.txt" in captured.out
    assert plot_path.exists()


def test_folio_errors_are_detected(tmp_path, capsys):
    file = tmp_path / "weird_sequence0.txt"
    file.write_text(
        "|F 1r|\nλόγος\n|F 3v|\nπνεῦμα\n",
        encoding="utf-8",
    )

    count_greek_chars(
        str(file)[:-5],
        end_homily=1,
        warning_stdev=2.0,
        output_path=None,
        show=False,
    )

    captured = capsys.readouterr()
    assert "Folio error from 1r to 3v in file weird_sequence0.txt" in captured.out


def test_compare_counts(tmp_path, capsys):
    output_path = tmp_path / "comparison_plot.svg"

    compare_counts(
        str(TEST_DATA / "Base-H"),
        str(TEST_DATA / "X264-H"),
        output_svg=output_path,
        start_homily=0,
        end_homily=2,
        threshold=5,
    )

    assert output_path.exists()
    stdout = capsys.readouterr().out
    assert "Base Sentence Count: 13\n" in stdout
    assert "Sentence 1.1.2 not found in comparison text." in stdout
    assert "Paragraph 1.3 not found in comparison text." in stdout
    assert "Homily 2 not found in comparison text" in stdout
    assert "Sentence 1.1.1 above the threshold" in stdout
    output_svg = output_path.read_text(encoding="utf-8")
    assert '<?xml version="1.0" encoding="utf-8" ?>\n<svg baseProfile="tiny"' in output_svg
    assert '<rect fill="black" height="10"' in output_svg
    assert '<rect fill="blue" height="10"' in output_svg
    assert '<rect fill="red" height="10"' in output_svg
    assert '<rect fill="green" height="10" width="1" x="0"' in output_svg
