from msstools.number import number_sentences


def test_number_sentences():
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

    assert number_sentences(input_text) == expected_output
