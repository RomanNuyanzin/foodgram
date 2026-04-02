from django_filters import rest_framework as filters

from recipes.models import Recipe


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug',
    )
    author = filters.NumberFilter(field_name='author__id')
    is_favorited = filters.NumberFilter(method='filter_is_favorited')
    is_in_shopping_cart = filters.NumberFilter(method='filter_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('tags', 'author')

    def filter_is_favorited(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if not request or request.user.is_anonymous or value != 1:
            return queryset
        return queryset.filter(favorited_by__user=request.user)

    def filter_is_in_shopping_cart(self, queryset, name, value):
        request = getattr(self, 'request', None)
        if not request or request.user.is_anonymous or value != 1:
            return queryset
        return queryset.filter(in_shopping_carts__user=request.user)