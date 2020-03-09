from fasjson.web import errors


def root():
    raise errors.WebApiError('method not implemented', 405, data={'reason': 'method not implemented'})
