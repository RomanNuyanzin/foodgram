from rest_framework import serializers

from api.fields import Base64ImageField
from recipes.constants import (
    MIN_COOKING_TIME,
    MIN_INGREDIENT_AMOUNT,
    RECIPE_NAME_MAX_LENGTH,
)
from recipes.fields import (
    IngredientPrimaryKeyRelatedField,
    TagPrimaryKeyRelatedField,
)
from recipes.messages import (
    RECIPE_COOKING_TIME_INVALID_ERROR,
    RECIPE_COOKING_TIME_MIN_VALUE_ERROR,
    RECIPE_COOKING_TIME_REQUIRED_ERROR,
    RECIPE_DUPLICATE_INGREDIENTS_ERROR,
    RECIPE_DUPLICATE_TAGS_ERROR,
    RECIPE_IMAGE_INVALID_ERROR,
    RECIPE_IMAGE_REQUIRED_ERROR,
    RECIPE_INGREDIENTS_REQUIRED_ERROR,
    RECIPE_INGREDIENT_AMOUNT_INVALID_ERROR,
    RECIPE_INGREDIENT_AMOUNT_REQUIRED_ERROR,
    RECIPE_NAME_MAX_LENGTH_ERROR,
    RECIPE_NAME_REQUIRED_ERROR,
    RECIPE_TAGS_REQUIRED_ERROR,
    RECIPE_TEXT_REQUIRED_ERROR,
)
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class RecipeAuthorSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
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


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='ingredient.id')
    name = serializers.CharField(source='ingredient.name')
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeReadSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = RecipeAuthorSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True,
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.in_shopping_carts.filter(user=request.user).exists()


class RecipeIngredientWriteSerializer(serializers.Serializer):
    id = IngredientPrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(
        min_value=MIN_INGREDIENT_AMOUNT,
        error_messages={
            'required': RECIPE_INGREDIENT_AMOUNT_REQUIRED_ERROR,
            'invalid': RECIPE_INGREDIENT_AMOUNT_INVALID_ERROR,
            'min_value': RECIPE_INGREDIENT_AMOUNT_INVALID_ERROR,
        },
    )


class RecipeWriteSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = TagPrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(
        required=True,
        allow_null=False,
        error_messages={
            'required': RECIPE_IMAGE_REQUIRED_ERROR,
            'null': RECIPE_IMAGE_REQUIRED_ERROR,
            'invalid': RECIPE_IMAGE_INVALID_ERROR,
        },
    )
    name = serializers.CharField(
        required=True,
        allow_blank=False,
        max_length=RECIPE_NAME_MAX_LENGTH,
        error_messages={
            'required': RECIPE_NAME_REQUIRED_ERROR,
            'blank': RECIPE_NAME_REQUIRED_ERROR,
            'max_length': RECIPE_NAME_MAX_LENGTH_ERROR,
        },
    )
    text = serializers.CharField(
        required=True,
        allow_blank=False,
        error_messages={
            'required': RECIPE_TEXT_REQUIRED_ERROR,
            'blank': RECIPE_TEXT_REQUIRED_ERROR,
        },
    )
    cooking_time = serializers.IntegerField(
        required=True,
        min_value=MIN_COOKING_TIME,
        error_messages={
            'required': RECIPE_COOKING_TIME_REQUIRED_ERROR,
            'invalid': RECIPE_COOKING_TIME_INVALID_ERROR,
            'min_value': RECIPE_COOKING_TIME_MIN_VALUE_ERROR,
        },
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, attrs):
        ingredients = attrs.get('ingredients', serializers.empty)
        tags = attrs.get('tags', serializers.empty)

        if ingredients is serializers.empty or not ingredients:
            raise serializers.ValidationError(
                {'ingredients': RECIPE_INGREDIENTS_REQUIRED_ERROR}
            )

        ingredient_ids = [item['id'].id for item in ingredients]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                {'ingredients': RECIPE_DUPLICATE_INGREDIENTS_ERROR}
            )

        if tags is serializers.empty or not tags:
            raise serializers.ValidationError(
                {'tags': RECIPE_TAGS_REQUIRED_ERROR}
            )

        tag_ids = [tag.id for tag in tags]
        if len(tag_ids) != len(set(tag_ids)):
            raise serializers.ValidationError(
                {'tags': RECIPE_DUPLICATE_TAGS_ERROR}
            )

        return attrs

    def _save_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                recipe=recipe,
                ingredient=item['id'],
                amount=item['amount'],
            )
            for item in ingredients
        ])

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data['author'] = self.context['request'].user

        recipe = super().create(validated_data)
        recipe.tags.set(tags)
        self._save_ingredients(recipe, ingredients)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        instance = super().update(instance, validated_data)
        instance.tags.set(tags)
        instance.recipe_ingredients.all().delete()
        self._save_ingredients(instance, ingredients)

        return instance

    def to_representation(self, instance):
        return RecipeReadSerializer(
            instance,
            context=self.context,
        ).data
