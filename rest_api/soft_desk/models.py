from django.db import models

from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model

from django.utils.translation import gettext_lazy as _

class UserManager(BaseUserManager):
    def create_user(self, email, password, first_name=None, last_name=None):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('Users must have an email address')
        if not password:
            raise ValueError('Users must have a password')
        user = self.model(
            email=self.normalize_email(email)
        )
        user.username = email
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_staffuser(self, email, password):
        """
        Creates and saves a staff user with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """
        Creates and saves a superuser with the given email and password.
        """
        user = self.create_user(
            email,
            password=password,
        )
        user.is_staff = True
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    """
    Entity User
    """
    user_id = models.BigAutoField(primary_key=True)
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )

    is_admin = models.BooleanField(default=False) # a superuser

    objects = UserManager()

    USERNAME_FIELD = 'email' # ça fonctionne pas quand on on crée un simple user forcer username avec email dans
    REQUIRED_FIELDS = [] # Email & Password are required by default.

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True


class Project(models.Model):
    """
    Entity Project
    """
    project_id = models.BigAutoField(primary_key=True)
    title = models.CharField(max_length=128)
    description = models.CharField(max_length=1024, blank=True)


    class Type(models.TextChoices):
        APPLICATION = 'APPL', _('Application')
        PRODUCT = 'PROD', _('Product')
        PROJECT = 'PROJ', _('Project')

    type = models.CharField(max_length=4, choices=Type.choices, default=Type.APPLICATION)
    author_user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Contributor(models.Model):
    """
    Entity Liens entre User et Project
    """
    user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)


    class Permission(models.TextChoices):
        CREATE = 'C', _('Create')
        READ = 'R', _('Read')
        UPDATE = 'U', _('Update')
        DELETE = 'D', _('Delete')

    permission = models.CharField(max_length=1, choices=Permission.choices, default=Permission.READ)


    class Role(models.TextChoices):
        DEVELOPER = 'DEV', _('Developer')
        TESTER = 'TES', _('Tester')
        CREATOR = 'CRE', _('Creator')
        IN_CHARGE_OF = 'ICO', _('In Charge Of')

    role = models.CharField(max_length=3, choices=Role.choices, default=Role.CREATOR)


    class Meta:
        """
        Contrainte d'unicité pour éviter des liens en doublons
        """
        unique_together = ('user', 'project', )

    def __str__(self):
        return f"{self.user.email} - {self.project.title}"


class Issue(models.Model):
    """
    Entity Issue
    """
    title = models.CharField(max_length=128)
    desc = models.CharField(max_length=2048, blank=True)
    tag = models.CharField(max_length=16)


    class Priority(models.TextChoices):
        LOW = 'L', _('Low')
        NORMAL = 'N', _('Normal')
        HIGH = 'H', _('High')
        URGENT = 'U', _('Urgent')
        IMMEDIATE = 'I', _('Immediate')

    priority = models.CharField(max_length=1, choices=Priority.choices, default=Priority.NORMAL)
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE)


    class Status(models.TextChoices):
        NEW = 'NEW', _('New')
        IN_PROGRESS = 'INP', _('In Progress')
        COMPLETED = 'COM', _('Completed')
        REJECTED = 'REJ', _('Rejected')
        CLOSED = 'CLO', _('CLOSED')

    status = models.CharField(max_length=3, choices=Status.choices, default=Status.NEW)
    author_user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='author_user')
    assignee_user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE, related_name='assignee_user')
    time_created = models.DateTimeField(auto_now_add=True)


    class Meta:
        """
        Contrainte d'unicité pour éviter des anomalies en doublons
        """
        unique_together = ('title', 'project', 'author_user',)

    def __str__(self):
        return self.title


class Comment(models.Model):
    """
    Entity Comment
    """
    comment_id = models.BigAutoField(primary_key=True)
    description = models.CharField(max_length=1024, blank=True)
    author_user = models.ForeignKey(to=get_user_model(), on_delete=models.CASCADE)
    issue = models.ForeignKey(to=Issue, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Comment : {self.comment_id} - {self.author_user.email}"
