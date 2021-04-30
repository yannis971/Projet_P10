from django.db import models

from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser

class UserManager(BaseUserManager):
    def create_user(self, email, password, first_name, last_name,):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
        	first_name,
        	last_name,
            email=self.normalize_email(email)
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password, first_name="", last_name=""):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
        	first_name,
        	last_name,
            email,
            password=password,
        )
        user.staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name="", last_name="")::
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
        	first_name,
        	last_name,
            email,
            password=password,
        )
        user.staff = True
        user.admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_active = models.BooleanField(default=True)
    staff = models.BooleanField(default=False) # a admin user; non super-user
    admin = models.BooleanField(default=False) # a superuser

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [] # Email & Password are required by default.


    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def __str__(self):
        return self.email

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        return self.staff

    @property
    def is_admin(self):
        "Is the user a admin member?"
        return self.admin

     objects = UserManager()


class Project(models.Model):
    """
    Entité Project : -
    """
    title = models.CharField(max_length=128)
    descrption = models.CharField(max_length=1024, blank=True)
    type = models.Charfield(max_length=32)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name='author_user')


class Contributor(models.Model):
    """
    Entité Liens entre User et Project
    """
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    project = models.ForeignKey(to=project, on_delete=models.CASCADE)
    #permission = models.ChoiceField()
    role = models.CharField(max_length=32)

    class Meta:
        """
        Contrainte d'unicité pour éviter des liens en doublons
        """
        unique_together = ('user', 'project', )
