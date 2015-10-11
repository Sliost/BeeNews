from functools import wraps
from flask import request, abort

def requires_token(f):
    """ Wrapper allowing to filter calls only for token authenticated users

    :param f: the function to wrap
    :return: a unauthorized answer or the given function result
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        """ The wraps decorator

        :param args: initial f's args
        :param kwargs: initial f's kwargs
        :return: an abortion if unauthorized or f
        """
        if 'X-BeenewsAPI-Token' not in request.headers:
            abort(418, {'_other': ['unauthorized']})

        return f(*args, **kwargs)

    return decorated
