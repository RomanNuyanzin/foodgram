from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListAPIView
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import Subscription, User
from users.serializers import SubscriptionSerializer, UserAvatarSerializer


class SubscriptionPagination(PageNumberPagination):
    page_size = 6
    page_size_query_param = 'limit'


class SubscriptionListAPIView(ListAPIView):
    serializer_class = SubscriptionSerializer
    permission_classes = (IsAuthenticated,)
    pagination_class = SubscriptionPagination

    def get_queryset(self):
        return User.objects.filter(
            subscribers__user=self.request.user
        ).order_by('id')


class SubscribeAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, id):
        author = get_object_or_404(User, id=id)

        if request.user == author:
            raise ValidationError('Нельзя подписаться на самого себя.')

        subscription, created = Subscription.objects.get_or_create(
            user=request.user,
            author=author,
        )
        if not created:
            raise ValidationError('Вы уже подписаны на этого автора.')

        serializer = SubscriptionSerializer(
            author,
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, id):
        author = get_object_or_404(User, id=id)

        deleted_count, _ = Subscription.objects.filter(
            user=request.user,
            author=author,
        ).delete()

        if not deleted_count:
            raise ValidationError('Подписка не найдена.')

        return Response(status=status.HTTP_204_NO_CONTENT)


class UserAvatarAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        serializer = UserAvatarSerializer(
            request.user,
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request):
        if request.user.avatar:
            request.user.avatar.delete(save=False)
        request.user.avatar = None
        request.user.save(update_fields=('avatar',))
        return Response(status=status.HTTP_204_NO_CONTENT)