from functools import wraps
from sqlalchemy.orm.exc import NoResultFound


def handle_no_result(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except NoResultFound:
            return None

    return wrapper
