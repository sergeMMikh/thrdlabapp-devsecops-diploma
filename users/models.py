# from django.contrib.auth.models import AbstractUser
# from django.db import models
#
#
# class User(AbstractUser):
#     telephone_number = models.CharField(max_length=20, null=True)
#
#     def __str__(self):
#         # return f"{self._meta.fields}"
#         return f"{self.first_name}, {self.last_name}, {self.email}"


from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from django_rest_passwordreset.models import get_token_generator


class UserManager(BaseUserManager):
    """
    Custom user manager where the username is the email address
    """
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        if not password:
            raise ValueError('User must have Password')

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and return a superuser with an email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    """
    Custom user model that uses email as username
    """

    REQUIRED_FIELDS = []
    objects = UserManager()
    USERNAME_FIELD = 'email'
    email = models.EmailField(_('email address'), unique=True)
    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=(
            """Required. 150 characters or fewer.
             Letters, digits and @/./+/-/_ only."""),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
        default='unlnown',
    )
    # is_active = models.BooleanField(
    #     _('active'),
    #     default=False,
    #     help_text=_(
    #         'Designates whether this user should be treated as active. '
    #         'Unselect this instead of deleting accounts.',
    #     ),
    # )
    email_is_verified = models.BooleanField(
        _('verified'),
        default=False,
        help_text=_(
            'Designates whether this user email is verified.',
        ),
    )

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = "List of users"
        ordering = ('email',)


class Person(models.Model):
    first_name = models.CharField(max_length=250, null=False, default='')
    surname = models.CharField(max_length=250, null=True)
    telephone_number = models.CharField(max_length=20, null=True)
    email = models.CharField(max_length=100, null=True)

    def __str__(self):
        return f"{self.first_name} {self.surname}"


class ConfirmEmailToken(models.Model):
    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        """ generates a pseudo random code using
        os.urandom and binascii.hexlify """
        return get_token_generator().generate_token()

    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_(
            "The User which is associated to this password reset token"),
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("When was this token generated"),
    )

    # Key field, though it is not the primary key of the model
    key = models.CharField(
        _("Key"),
        max_length=64,
        db_index=True,
        unique=True,
    )

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        return super(ConfirmEmailToken, self).save(*args, **kwargs)

    def __str__(self):
        return "Password reset token for user {user}".format(user=self.user)
