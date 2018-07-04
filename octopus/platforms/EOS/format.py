def format_func_name(name, param_str, return_str):
    result = '{} '.format(return_str) if return_str else ''
    return ('{}{}({})'.format(result, name, param_str))


def format_bb_name(function_id, offset):
    return ('block_%x_%x' % (function_id, offset))
