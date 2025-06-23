from pathlib import Path
from PIL import Image
from typer.testing import CliRunner
from msstools.main import app 

TEST_DATA = Path(__file__).parent/"testdata"


runner = CliRunner()

def test_csv_to_tei(tmp_path):
    output_file = tmp_path / "output-tei.xml"
    result = runner.invoke(app, [
        "csv-to-tei",
        str(TEST_DATA/"demo-readings.csv"),
        str(output_file),
    ])
    assert result.exit_code == 0
    
    assert output_file.exists()
    output_data = output_file.read_text()
    assert output_data.startswith('<TEI xmlns="http://www.tei-c.org/ns/1.0">\n\t<teiHeader>')
    assert '<p>Derived from `demo-readings.csv`</p>' in output_data
    assert '<rdg wit="B C D">1</rdg>' in output_data
    assert '<listWit>\n\t\t\t\t\t<witness n="0236K" />' in output_data
    assert '<rdg wit="D E">2</rdg>' in output_data


def test_csv_to_tei_max2(tmp_path):
    output_file = tmp_path / "output-tei.xml"
    result = runner.invoke(app, [
        "csv-to-tei",
        str(TEST_DATA/"demo-readings.csv"),
        str(output_file),
        "--max-readings", "2",
    ])
    assert result.exit_code == 0
    
    assert output_file.exists()
    output_data = output_file.read_text()
    assert output_data.startswith('<TEI xmlns="http://www.tei-c.org/ns/1.0">\n\t<teiHeader>')
    assert '<p>Derived from `demo-readings.csv`</p>' in output_data
    assert '<rdg wit="B C D">1</rdg>' in output_data
    assert '<listWit>\n\t\t\t\t\t<witness n="0236K" />' in output_data
    assert '<rdg wit="D E">2</rdg>' not in output_data


def test_csv_to_tei_dates(tmp_path):
    output_file = tmp_path / "output-tei.xml"
    result = runner.invoke(app, [
        "csv-to-tei",
        str(TEST_DATA/"demo-readings.csv"),
        str(output_file),
        "--dates",
        str(TEST_DATA/"demo-dates.csv"),
    ])
    assert result.exit_code == 0
    
    assert output_file.exists()
    output_data = output_file.read_text()
    assert output_data.startswith('<TEI xmlns="http://www.tei-c.org/ns/1.0">\n\t<teiHeader>')
    assert '<p>Derived from `demo-readings.csv`</p>' in output_data
    assert '<rdg wit="B C D">1</rdg>' in output_data
    assert '<listWit>\n\t\t\t\t\t<witness n="0236K">' in output_data
    assert '<origDate notBefore="200" notAfter="299" />' in output_data
    stdout = result.stdout.strip()
    assert 'Witness C not in dates' in stdout

