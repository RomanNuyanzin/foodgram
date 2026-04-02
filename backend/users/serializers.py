from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from api.fields import Base64ImageField
from recipes.serializers import RecipeShortSerializer
from users.messages import (
    EMAIL_ALREADY_EXISTS_ERROR,
    EMAIL_INVALID_ERROR,
    EMAIL_MAX_LENGTH_ERROR,
    EMAIL_REQUIRED_ERROR,
    EMAIL_RESERVED_ERROR,
    FIRST_NAME_MAX_LENGTH_ERROR,
    FIRST_NAME_REQUIRED_ERROR,
    LAST_NAME_MAX_LENGTH_ERROR,
    LAST_NAME_REQUIRED_ERROR,
    PASSWORD_REQUIRED_ERROR,
    USERNAME_ALREADY_EXISTS_ERROR,
    USERNAME_MAX_LENGTH_ERROR,
    USERNAME_REQUIRED_ERROR,
)
from users.models import User
from users.validators import (
    contains_reserved_fragment,
    validate_first_name_value,
    validate_last_name_value,
    validate_username_value,
)


class FoodgramUserSerializer(BaseUserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.subscribers.filter(user=request.user).exists()


class FoodgramUserCreateSerializer(BaseUserCreateSerializer):
    email = serializers.EmailField(
        required=True,
        allow_blank=False,
        max_length=254,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=EMAIL_ALREADY_EXISTS_ERROR,
            )
        ],
        error_messages={
            'required': EMAIL_REQUIRED_ERROR,
            'blank': EMAIL_REQUIRED_ERROR,
            'invalid': EMAIL_INVALID_ERROR,
            'max_length': EMAIL_MAX_LENGTH_ERROR,
        },
    )

    username = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=150,
        trim_whitespace=True,
        validators=[
            UniqueValidator(
                queryset=User.objects.all(),
                message=USERNAME_ALREADY_EXISTS_ERROR,
            )
        ],
        error_messages={
            'required': USERNAME_REQUIRED_ERROR,
            'blank': USERNAME_REQUIRED_ERROR,
            'max_length': USERNAME_MAX_LENGTH_ERROR,
        },
    )

    first_name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=150,
        trim_whitespace=True,
        error_messages={
            'required': FIRST_NAME_REQUIRED_ERROR,
            'blank': FIRST_NAME_REQUIRED_ERROR,
            'max_length': FIRST_NAME_MAX_LENGTH_ERROR,
        },
    )

    last_name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=150,
        trim_whitespace=True,
        error_messages={
            'required': LAST_NAME_REQUIRED_ERROR,
            'blank': LAST_NAME_REQUIRED_ERROR,
            'max_length': LAST_NAME_MAX_LENGTH_ERROR,
        },
    )

    password = serializers.CharField(
        required=True,
        allow_blank=False,
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
        error_messages={
            'required': PASSWORD_REQUIRED_ERROR,
            'blank': PASSWORD_REQUIRED_ERROR,
        },
    )

    class Meta(BaseUserCreateSerializer.Meta):
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )

    def validate_email(self, value):
        local_part = value.split('@')[0]
        if contains_reserved_fragment(local_part):
            raise serializers.ValidationError(EMAIL_RESERVED_ERROR)
        return value.strip()

    def validate_username(self, value):
        try:
            return validate_username_value(value)
        except ValueError as error:
            raise serializers.ValidationError(str(error))

    def validate_first_name(self, value):
        try:
            return validate_first_name_value(value)
        except ValueError as error:
            raise serializers.ValidationError(str(error))

    def validate_last_name(self, value):
        try:
            return validate_last_name_value(value)
        except ValueError as error:
            raise serializers.ValidationError(str(error))


class SubscriptionSerializer(FoodgramUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source='recipes.count',
        read_only=True,
    )

    class Meta(FoodgramUserSerializer.Meta):
        fields = FoodgramUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes = obj.recipes.all()

        recipes_limit = None
        if request:
            recipes_limit = request.query_params.get('recipes_limit')

        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except (TypeError, ValueError):
                pass

        return RecipeShortSerializer(
            recipes,
            many=True,
            context=self.context,
        ).data


class UserAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)