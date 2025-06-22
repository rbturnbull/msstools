import pytest
from typer.testing import CliRunner
from msstools.main import app 

runner = CliRunner()

@pytest.fixture
def greek_text_with_accents():
    return "Καλημέρα, πῶς εἶσαι;\nἘγώ εἰμὶ καλῶς.\n"

@pytest.fixture
def expected_output():
    return "Καλημερα, πως εισαι;\nΕγω ειμι καλως.\n"

def test_remove_accents(tmp_path, greek_text_with_accents, expected_output):
    input_file = tmp_path / "with_accents.txt"
    output_file = tmp_path / "without_accents.txt"

    input_file.write_text(greek_text_with_accents, encoding="utf-8")

    result = runner.invoke(app, [
        "remove-accents",
        str(input_file),
        str(output_file),
    ])
    assert result.exit_code == 0
    assert output_file.exists()

    actual = output_file.read_text(encoding="utf-8")
    assert actual == expected_output
