import pytest
from django.urls import reverse
from rest_framework.authtoken.models import Token
from django_rest_passwordreset.models import ResetPasswordToken
from unittest.mock import patch

from users.models import ConfirmEmailToken, User


pytestmark = pytest.mark.django_db


@pytest.fixture
def strong_password():
    return 'VeryStrongPass123!'


def test_user_register_success(client, strong_password):
    response = client.post(
        reverse('orders:user-register'),
        data={
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': 'register@example.com',
            'password': strong_password,
        },
    )

    assert response.status_code == 201
    assert response.json()['Status'] is True
    user = User.objects.get(email='register@example.com')
    assert user.check_password(strong_password) is True
    assert Token.objects.filter(user=user).exists() is True


def test_user_register_missing_fields_returns_400(client):
    response = client.post(
        reverse('orders:user-register'),
        data={
            'first_name': 'Ivan',
            'email': 'register-missing@example.com',
        },
    )

    assert response.status_code == 400
    assert response.json()['Status'] is False


def test_user_register_returns_readable_error_for_too_long_first_name(
    client,
    strong_password,
):
    response = client.post(
        reverse('orders:user-register'),
        data={
            'first_name': 'I' * 151,
            'last_name': 'Petrov',
            'email': 'long-name@example.com',
            'password': strong_password,
        },
    )

    assert response.status_code == 200
    assert response.json()['Status'] is False
    assert response.json()['Errors']['first_name'] == [
        'First name is too long. Maximum length is 150 characters.',
    ]


def test_user_register_returns_readable_error_for_too_long_email(
    client,
    strong_password,
):
    response = client.post(
        reverse('orders:user-register'),
        data={
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'email': f"{'a' * 245}@example.com",
            'password': strong_password,
        },
    )

    assert response.status_code == 200
    assert response.json()['Status'] is False
    assert response.json()['Errors']['email'] == [
        'Email is too long. Maximum length is 254 characters.',
    ]


def test_user_login_success_for_verified_user(client, strong_password):
    user = User.objects.create_user(
        email='login-ok@example.com',
        password=strong_password,
        first_name='Log',
        last_name='In',
    )
    user.email_is_verified = True
    user.is_active = True
    user.save()

    response = client.post(
        reverse('orders:user-login'),
        data={'email': user.email, 'password': strong_password},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload['Status'] is True
    assert payload['Token']


def test_user_login_unverified_user_returns_403(client, strong_password):
    user = User.objects.create_user(
        email='login-unverified@example.com',
        password=strong_password,
    )
    user.email_is_verified = False
    user.is_active = True
    user.save()

    response = client.post(
        reverse('orders:user-login'),
        data={'email': user.email, 'password': strong_password},
    )

    assert response.status_code == 403
    assert response.json()['Status'] is False


def test_confirm_account_activates_user_and_removes_token(client, strong_password):
    user = User.objects.create_user(
        email='confirm@example.com',
        password=strong_password,
        is_active=False,
    )
    token = ConfirmEmailToken.objects.create(user=user, key='confirm-key-123')

    response = client.post(
        reverse('orders:user-register-confirm'),
        data={'email': user.email, 'token': token.key},
    )

    user.refresh_from_db()
    assert response.status_code == 201
    assert user.is_active is True
    assert user.email_is_verified is True
    assert ConfirmEmailToken.objects.filter(pk=token.pk).exists() is False


def test_verify_email_by_token_marks_user_as_verified(client, strong_password):
    user = User.objects.create_user(
        email='verify-email@example.com',
        password=strong_password,
        is_active=False,
    )
    token = Token.objects.create(user=user)

    response = client.get(reverse('orders:verify-email', args=[token.key]))

    user.refresh_from_db()
    assert response.status_code == 200
    assert user.email_is_verified is True
    assert user.is_active is False


def test_edit_user_get_requires_authentication(client):
    response = client.get(reverse('orders:user-edit'))
    assert response.status_code == 401


def test_edit_user_get_and_post_for_authenticated_user(client, strong_password):
    user = User.objects.create_user(
        email='edit-user@example.com',
        password=strong_password,
        first_name='Old',
        last_name='Name',
    )
    token = Token.objects.create(user=user)
    auth_header = f'Token {token.key}'

    get_response = client.get(
        reverse('orders:user-edit'),
        HTTP_AUTHORIZATION=auth_header,
    )
    post_response = client.post(
        reverse('orders:user-edit'),
        data={'first_name': 'New', 'last_name': 'Surname'},
        HTTP_AUTHORIZATION=auth_header,
    )

    user.refresh_from_db()
    assert get_response.status_code == 200
    assert get_response.json()['email'] == user.email
    assert post_response.status_code == 201
    assert user.first_name == 'New'
    assert user.last_name == 'Surname'


@patch('users.views.user_views.send_email_4_reset_passw.delay')
def test_password_reset_request_returns_ok_and_calls_task(
    mock_delay,
    client,
    strong_password,
):
    user = User.objects.create_user(
        email='reset-request@example.com',
        password=strong_password,
    )
    user.is_active = True
    user.save()

    response = client.post(
        reverse('orders:password-reset'),
        data={'email': user.email},
    )

    assert response.status_code == 200
    assert response.json()['status'] == 'OK'
    assert ResetPasswordToken.objects.filter(user=user).exists() is True
    assert mock_delay.called is True


def test_password_reset_confirm_changes_password_and_deletes_reset_tokens(
    client,
    strong_password,
):
    user = User.objects.create_user(
        email='reset-confirm@example.com',
        password=strong_password,
    )
    user.is_active = True
    user.save()
    auth_token = Token.objects.create(user=user)
    ResetPasswordToken.objects.create(user=user)

    response = client.post(
        reverse('orders:password-reset-confirm'),
        data={
            'token': auth_token.key,
            'password': 'AnotherStrongPass123!',
        },
    )

    user.refresh_from_db()
    assert response.status_code == 200
    assert response.json()['status'] == 'OK'
    assert user.check_password('AnotherStrongPass123!') is True
    assert ResetPasswordToken.objects.filter(user=user).exists() is False
