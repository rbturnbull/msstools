import pytest

from msstools.strings import remove_accents, remove_accents_from_file


@pytest.fixture
def greek_text_with_accents():
    return "Καλημέρα, πῶς εἶσαι;\nἘγώ εἰμὶ καλῶς.\n"


@pytest.fixture
def expected_output():
    return "Καλημερα, πως εισαι;\nΕγω ειμι καλως.\n"


def test_remove_accents(greek_text_with_accents, expected_output):
    assert remove_accents(greek_text_with_accents) == expected_output


def test_remove_accents_from_file(tmp_path, greek_text_with_accents, expected_output):
    input_file = tmp_path / "with_accents.txt"
    output_file = tmp_path / "without_accents.txt"

    input_file.write_text(greek_text_with_accents, encoding="utf-8")

    remove_accents_from_file(input_file, output_file)

    assert output_file.exists()
    assert output_file.read_text(encoding="utf-8") == expected_output
