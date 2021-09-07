from six import text_type
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import AbstractBaseUser

class AppTokenGenerator(PasswordResetTokenGenerator):

    def _make_hash_value(self, user: AbstractBaseUser, timestamp: int) -> str:
        return (text_type(user.pk)+text_type(timestamp)+text_type(user.is_active))

    
token_generator = AppTokenGenerator()