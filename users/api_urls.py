from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from users.views.user_views import (
    ConfirmAccount,
    EditUser,
    LoginAccount,
    RegisterAccount,
    ResetPasswordConfirm,
    ResetPasswordRequestToken,
    UserEmailVerify,
)

app_name = 'orders'

urlpatterns = [
                  path('user/login', LoginAccount.as_view(), name='user-login'),
                  path('user/register', RegisterAccount.as_view(), name='user-register'),
                  path('user/register/confirm',
                       ConfirmAccount.as_view(), name='user-register-confirm'),
                  path('user/details', EditUser.as_view(), name='user-edit'),
                  path('user/verify_email/<token>/',
                       UserEmailVerify.as_view(), name='verify-email'),
                  path('user/password_reset', ResetPasswordRequestToken.as_view(),
                       name='password-reset'),
                  path('user/password_reset/confirm', ResetPasswordConfirm.as_view(),
                       name='password-reset-confirm'),
                  path('token/', obtain_auth_token),

               ]
