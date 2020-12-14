from django.db import models
from django.contrib.auth.models import User, AbstractUser

# Create your models here.
# class Usuario(AbstractUser):

#     image = models.ImageField(upload_to='users/%Y/%m/%d', null=True, blank=True)

#     def get_image(self):
#         if self.image:
#             return '{}{}'.format(MEDIA_URL, self.image)
#         return '{}{}'.format(STATIC_URL, 'img/empty.png')

# class MyAccountManager(BaseUserManager):
#     def create_user(self, email, username, password=None):
#         if not email:
#             raise ValueError("No existe email")
#         if not username:
#             raise ValueError("No existe usuario")

#         user = self.model(
#             email=self.normalize_email(email),
#             usernone=username,
#         )

#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, username, password):
#         user = self.create_user(
#                email=self.normalize_email(email),
#                password=password,
#                username=username,
#         )
#         user.is_admin = True
#         user.is_staff = True
#         user.is_superuser = True
#         user.save(using=self._db)
#         return user


# class Account(AbstractBaseUser):

#     email                     = models.EmailField(verbose_name="email", max_length=60, unique=True)
#     username                 = models.CharField( max_length=30, unique=True)
#     date_joined                = models.DateTimeFieldDateTimeField(verbose_name='date joined', auto_now_add=True)
#     last_login                = models.(verbose_name='last login', auto_now=True)
#     is_admin                = models.BooleanField(default=False)
#     is_active                = models.BooleanField(default=True)
#     is_staff                = models.BooleanField(default=False)
#     is_superuser            = models.BooleanField(default=False)
#     #first_name              = models.CharField(default=False)

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['username',]

#     objects = MyAccountManager()

#     def str(self):
#         return self.email

#     def has_perm(self, perm, obj=None):
#         return self.is_admin

#     def has_module_perms(self, app_label):

#         return True

#         return True