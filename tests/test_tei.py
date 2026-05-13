from pathlib import Path

from msstools.tei import csv_to_tei


TEST_DATA = Path(__file__).parent / "testdata"


def test_csv_to_tei(tmp_path):
    output_file = tmp_path / "output-tei.xml"
    csv_to_tei(TEST_DATA / "demo-readings.csv", output_file)

    assert output_file.exists()
    output_data = output_file.read_text()
    assert output_data.startswith('<TEI xmlns="http://www.tei-c.org/ns/1.0">\n\t<teiHeader>')
    assert '<p>Derived from `demo-readings.csv`</p>' in output_data
    assert '<rdg wit="B C D">1</rdg>' in output_data
    assert '<listWit>\n\t\t\t\t\t<witness n="0236K" />' in output_data
    assert '<rdg wit="D E">2</rdg>' in output_data


def test_csv_to_tei_max2(tmp_path):
    output_file = tmp_path / "output-tei.xml"
    csv_to_tei(TEST_DATA / "demo-readings.csv", output_file, max_readings=2)

    assert output_file.exists()
    output_data = output_file.read_text()
    assert output_data.startswith('<TEI xmlns="http://www.tei-c.org/ns/1.0">\n\t<teiHeader>')
    assert '<p>Derived from `demo-readings.csv`</p>' in output_data
    assert '<rdg wit="B C D">1</rdg>' in output_data
    assert '<listWit>\n\t\t\t\t\t<witness n="0236K" />' in output_data
    assert '<rdg wit="D E">2</rdg>' not in output_data


def test_csv_to_tei_dates(tmp_path, capsys):
    output_file = tmp_path / "output-tei.xml"
    csv_to_tei(
        TEST_DATA / "demo-readings.csv",
        output_file,
        dates=TEST_DATA / "demo-dates.csv",
    )

    assert output_file.exists()
    output_data = output_file.read_text()
    assert output_data.startswith('<TEI xmlns="http://www.tei-c.org/ns/1.0">\n\t<teiHeader>')
    assert '<p>Derived from `demo-readings.csv`</p>' in output_data
    assert '<rdg wit="B C D">1</rdg>' in output_data
    assert '<listWit>\n\t\t\t\t\t<witness n="0236K">' in output_data
    assert '<origDate notBefore="200" notAfter="299" />' in output_data

    captured = capsys.readouterr()
    assert "Witness C not in dates" in captured.out
