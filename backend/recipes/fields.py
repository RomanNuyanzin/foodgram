from rest_framework import serializers

from recipes.messages import (
    RECIPE_INGREDIENT_NOT_FOUND_ERROR,
    RECIPE_TAG_NOT_FOUND_ERROR,
)


class IngredientPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'does_not_exist': RECIPE_INGREDIENT_NOT_FOUND_ERROR,
        'incorrect_type': RECIPE_INGREDIENT_NOT_FOUND_ERROR,
    }


class TagPrimaryKeyRelatedField(serializers.PrimaryKeyRelatedField):
    default_error_messages = {
        'does_not_exist': RECIPE_TAG_NOT_FOUND_ERROR,
        'incorrect_type': RECIPE_TAG_NOT_FOUND_ERROR,
    }