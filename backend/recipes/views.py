from django.db.models import Sum
from django.http import Http404, HttpResponse
from django.shortcuts import redirect
from django.views import View
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from core.utils import decode_base36, encode_base36
from recipes.filters import RecipeFilter
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from recipes.pagination import RecipePagination
from recipes.permissions import IsAuthorOrReadOnly
from recipes.serializers import (
    IngredientSerializer,
    RecipeReadSerializer,
    RecipeShortSerializer,
    RecipeWriteSerializer,
    TagSerializer,
)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientViewSet(ReadOnlyModelViewSet):
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    pagination_class = RecipePagination
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_queryset(self):
        return (
            Recipe.objects
            .select_related('author')
            .prefetch_related(
                'tags',
                'recipe_ingredients__ingredient',
            )
            .all()
        )

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def _add_to_relation(self, request, relation_model):
        recipe = self.get_object()
        relation, created = relation_model.objects.get_or_create(
            user=request.user,
            recipe=recipe,
        )
        if not created:
            raise ValidationError('Рецепт уже добавлен.')

        serializer = RecipeShortSerializer(
            recipe,
            context={'request': request},
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def _remove_from_relation(self, relation_model):
        recipe = self.get_object()
        deleted_count, _ = relation_model.objects.filter(
            user=self.request.user,
            recipe=recipe,
        ).delete()

        if not deleted_count:
            raise ValidationError('Рецепт не найден.')

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
    )
    def favorite(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_relation(request, Favorite)
        return self._remove_from_relation(Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        url_path='shopping_cart',
    )
    def shopping_cart(self, request, pk=None):
        if request.method == 'POST':
            return self._add_to_relation(request, ShoppingCart)
        return self._remove_from_relation(ShoppingCart)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='download_shopping_cart',
    )
    def download_shopping_cart(self, request):
        ingredients = (
            RecipeIngredient.objects
            .filter(recipe__in_shopping_carts__user=request.user)
            .values(
                'ingredient__name',
                'ingredient__measurement_unit',
            )
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name')
        )

        lines = ['Список покупок:\n']

        if not ingredients:
            lines.append('Список покупок пуст.\n')
        else:
            for item in ingredients:
                lines.append(
                    f"{item['ingredient__name']} "
                    f"({item['ingredient__measurement_unit']}) — "
                    f"{item['total_amount']}\n"
                )

        response = HttpResponse(
            ''.join(lines),
            content_type='text/plain; charset=utf-8',
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response

    @action(
        detail=True,
        methods=['get'],
        url_path='get-link',
        permission_classes=[AllowAny],
    )
    def get_link(self, request, pk=None):
        recipe = self.get_object()
        short_code = encode_base36(recipe.id)
        short_link = request.build_absolute_uri(f'/s/{short_code}')
        return Response(
            {'short-link': short_link},
            status=status.HTTP_200_OK,
        )


class RecipeShortLinkRedirectView(View):
    def get(self, request, short_code):
        try:
            recipe_id = decode_base36(short_code)
        except ValueError:
            raise Http404('Некорректная короткая ссылка.')

        if not Recipe.objects.filter(id=recipe_id).exists():
            raise Http404('Рецепт не найден.')

        return redirect(f'/recipes/{recipe_id}')