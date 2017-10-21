from ..models import User
from util.misc import get_unique_str_fn

_unique_str_fn = get_unique_str_fn()


class UserTestUtil:
    DEFAULT_USER_PASSWORD = _unique_str_fn()

    @staticmethod
    def create_user():
        some_string = _unique_str_fn()
        email = '{}@{}.com'.format(some_string, some_string)
        user_counter_val_str = '{}'.format(some_string)
        user = User(email=email, username=user_counter_val_str)
        user.set_password(UserTestUtil.DEFAULT_USER_PASSWORD)
        user.save()
        return user



