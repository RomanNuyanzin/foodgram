from django.urls import path

from users.views import (
    SubscribeAPIView,
    SubscriptionListAPIView,
    UserAvatarAPIView,
)

urlpatterns = [
    path(
        'users/subscriptions/',
        SubscriptionListAPIView.as_view(),
        name='subscriptions',
    ),
    path(
        'users/<int:id>/subscribe/',
        SubscribeAPIView.as_view(),
        name='subscribe',
    ),
    path(
        'users/me/avatar/',
        UserAvatarAPIView.as_view(),
        name='user-avatar',
    ),
]