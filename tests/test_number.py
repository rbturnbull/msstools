from typer.testing import CliRunner
from msstools.main import app 

runner = CliRunner()

def test_number_sentences_cli(tmp_path):
    input_text = (
        "<P>\n"
        "<S>This is the first sentence.</S>\n"
        "<S>This is the second sentence.</S>\n"
        "</P>\n"
        "<P>\n"
        "<S>This is the third sentence.</S>\n"
        "</P>"
    )

    expected_output = (
        "<P>\n"
        "<S 1>This is the first sentence.</S>\n"
        "<S 2>This is the second sentence.</S>\n"
        "</P>\n"
        "<P>\n"
        "<S 1>This is the third sentence.</S>\n"
        "</P>"
    )

    input_file = tmp_path / "input.xml"
    output_file = tmp_path / "output.xml"
    input_file.write_text(input_text, encoding='utf-8')

    result = runner.invoke(app, [
        "number-sentences",
        str(input_file),
        str(output_file)
    ])

    assert result.exit_code == 0
    assert output_file.exists()
    assert output_file.read_text(encoding='utf-8') == expected_output
