from rest_framework import exceptions, status
from rest_framework.response import Response
from rest_framework.views import exception_handler


AUTH_REQUIRED_MESSAGE = (
    'Пожалуйста, зарегистрируйтесь или, если уже зарегистрированы, '
    'войдите в систему.'
)

USER_NOT_FOUND_MESSAGE = 'Пользователя с таким id не существует.'
TAG_NOT_FOUND_MESSAGE = 'Тэга с таким id не существует.'
INGREDIENT_NOT_FOUND_MESSAGE = 'Ингредиента с таким id не существует.'
RECIPE_NOT_FOUND_MESSAGE = (
    'Рецепт с таким id не был найден, пожалуйста проверьте id рецепта.'
)


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is None:
        return response

    if isinstance(exc, (exceptions.NotAuthenticated, exceptions.AuthenticationFailed)):
        return Response(
            {'detail': AUTH_REQUIRED_MESSAGE},
            status=status.HTTP_401_UNAUTHORIZED,
        )

    if response.status_code == status.HTTP_404_NOT_FOUND:
        detail = response.data.get('detail') if isinstance(response.data, dict) else None
        detail_text = str(detail)

        if detail_text == 'No User matches the given query.':
            response.data = {'detail': USER_NOT_FOUND_MESSAGE}
        elif detail_text == 'No Tag matches the given query.':
            response.data = {'detail': TAG_NOT_FOUND_MESSAGE}
        elif detail_text == 'No Ingredient matches the given query.':
            response.data = {'detail': INGREDIENT_NOT_FOUND_MESSAGE}
        elif detail_text == 'No Recipe matches the given query.':
            response.data = {'detail': RECIPE_NOT_FOUND_MESSAGE}

    return response