from ..models import User
from util.misc import get_unique_str_fn

_unique_str_fn = get_unique_str_fn()


class AUserBUserMixin:
    def setUp(self):
        super(AUserBUserMixin, self).setUp()
        self.a_user = UserTestUtil.create_user()
        self.b_user = UserTestUtil.create_user()

    def client_login_a_user(self):
        self.client.login(
            username=self.a_user.username,
            password=UserTestUtil.DEFAULT_USER_PASSWORD
        )


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



