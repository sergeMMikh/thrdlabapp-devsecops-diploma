# import random
from celery import shared_task
# from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage


@shared_task(serializer='json')
def send_email_4_verification(current_site: str,
                              user_email: str,
                              token: str) -> None:
    message = f"Please follow this link to confirm your password: \n " \
              f"http://{current_site}/api/v1/user/verify_email/" \
              f"{token}"
    email = EmailMessage(
        'Verify email',
        message,
        to=[user_email],
    )
    email.send()


@shared_task(serializer='json')
def send_email_4_reset_passw(user_email, token):
    # token, _ = Token.objects.get_or_create(user=user)
    message = f"Please use this token for you request : \n " \
              f"{token}"
    email = EmailMessage(
        'reset_password',
        message,
        to=[user_email],
    )
    email.send()


@shared_task(serializer='json')
def send_email(user_email,
               sabject,
               message):
    email = EmailMessage(
        sabject,
        message,
        to=[user_email],
    )
    email.send()
