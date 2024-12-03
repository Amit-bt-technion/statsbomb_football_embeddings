
def get_value_of_nested_key(dictionary: dict, key: str, default=None):
    """
    this function iterates through a nested dictionary based on a dot ('.') notation of nested dictionary keys.
    :param dictionary: the dictionary in which to perform the lookup
    :param key: a dot notation string representing the dictionary key hierarchy from root to desired key
    :param default: what to return in case the desired key is not present in the dictionary
    :return: the value of the key if found in dictionary, and otherwise return the default value
    """
    # TODO: attend list indexes as well
    for key in key.split('.'):
        if key not in dictionary:
            return default
        dictionary = dictionary[key]
    return dictionary
