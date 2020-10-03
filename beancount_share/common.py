def read_config(config_string):
    """
    Args:
      config_string: A configuration string in JSON format given in source file.
    Returns:
      A dict of the configuration string.
    """
    if len(config_string) == 0:
        config_obj = {}
    else:
        config_obj = eval(config_string, {}, {})

    if not isinstance(config_obj, dict):
        raise RuntimeError("Invalid plugin configuration: should be a single dict.")
    return config_obj
