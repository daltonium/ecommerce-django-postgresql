from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    WHY AbstractUser and not AbstractBaseUser?
    ─────────────────────────────────────────
    AbstractBaseUser = blank slate. You build EVERYTHING from scratch:
    password hashing, permissions, login logic. Powerful but complex.

    AbstractUser = Django's full user model with everything already built
    (login, password hashing, permissions, admin support). You just EXTEND it.
    For BlueCart, AbstractUser is the right choice — we want to ADD fields,
    not rewrite auth from scratch.
    """

    email = models.EmailField(unique=True)
    is_seller = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email