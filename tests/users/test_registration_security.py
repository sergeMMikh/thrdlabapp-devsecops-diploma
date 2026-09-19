import pytest
from django.urls import reverse

from users.models import User


pytestmark = pytest.mark.django_db


@pytest.mark.parametrize('password', ['123', 'UniquePersonName123!'])
def test_registration_rejects_weak_or_similar_password_without_saving(client, password):
    response = client.post(reverse('orders:user-register'), {
        'first_name': 'UniquePersonName123',
        'last_name': 'Person',
        'email': 'reject@example.com',
        'password': password,
    })
    assert response.status_code == 400
    assert 'password' in response.json()['Errors']
    assert not User.objects.filter(email='reject@example.com').exists()


def test_registration_cannot_self_verify_email(client):
    response = client.post(reverse('orders:user-register'), {
        'first_name': 'Test',
        'last_name': 'Person',
        'email': 'unverified@example.com',
        'password': 'UnrelatedStrongPass987!',
        'email_is_verified': True,
    })
    assert response.status_code == 201
    user = User.objects.get(email='unverified@example.com')
    assert not user.email_is_verified
    assert user.check_password('UnrelatedStrongPass987!')
