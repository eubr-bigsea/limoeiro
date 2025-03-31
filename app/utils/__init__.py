import unicodedata

def remove_accents(input_str):
    """
    Removes accents from a given string.

    Args:
        input_str (str): The string to process.

    Returns:
        str: The string without accents.
    """
    if input_str is None:
        return None
    return ''.join(
        char for char in unicodedata.normalize('NFD', input_str)
        if unicodedata.category(char) != 'Mn'
    )