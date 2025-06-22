

def number_sentences(data: str) -> str:
    """
    Number <S> sentence tags within <P> blocks, restarting at 1 after each </P>.

    Args:
        data (str): The input text containing XML-like markup.

    Returns:
        str: The text with <S> tags numbered like <S 1>, <S 2>, etc.
    """
    data_len = len(data)
    result = []
    s_num = 1
    in_tag = False
    tag_start = 0
    current_index = 0

    while current_index < data_len:
        char = data[current_index]

        if not in_tag and char != "<":
            result.append(char)
            current_index += 1
            continue

        if char == "<":
            in_tag = True
            tag_start = current_index
            current_index += 1
            continue

        if in_tag and char == ">":
            tag_end = current_index
            current_tag = data[tag_start:tag_end + 1]

            if "/P" in current_tag:
                s_num = 1
            elif current_tag.startswith("<S") and not current_tag.startswith("</"):
                current_tag = f"<S {s_num}>"
                s_num += 1

            result.append(current_tag)
            in_tag = False
            current_index += 1
            continue

        current_index += 1

    return ''.join(result)
