import re

from django.core.validators import RegexValidator

from users.constants import RESERVED_EXACT_VALUES, RESERVED_FRAGMENT_VALUES
from users.messages import (
    FIRST_NAME_EMAIL_LIKE_ERROR,
    FIRST_NAME_INVALID_CHARS_ERROR,
    LAST_NAME_EMAIL_LIKE_ERROR,
    LAST_NAME_INVALID_CHARS_ERROR,
    USERNAME_EMAIL_LIKE_ERROR,
    USERNAME_INVALID_CHARS_ERROR,
)

NORMALIZED_RESERVED_EXACT_VALUES = {
    re.sub(r'[^a-zA-Zа-яА-Я0-9]+', '', value).lower()
    for value in RESERVED_EXACT_VALUES
}

NORMALIZED_RESERVED_FRAGMENT_VALUES = {
    re.sub(r'[^a-zA-Zа-яА-Я0-9]+', '', value).lower()
    for value in RESERVED_FRAGMENT_VALUES
}

USERNAME_REGEX_VALIDATOR = RegexValidator(
    regex=r'^[A-Za-zА-Яа-я0-9_-]+\Z',
    message=USERNAME_INVALID_CHARS_ERROR,
)

FIRST_NAME_REGEX_VALIDATOR = RegexValidator(
    regex=r'^[A-Za-zА-Яа-яЁё\s-]+\Z',
    message=FIRST_NAME_INVALID_CHARS_ERROR,
)

LAST_NAME_REGEX_VALIDATOR = RegexValidator(
    regex=r'^[A-Za-zА-Яа-яЁё\s-]+\Z',
    message=LAST_NAME_INVALID_CHARS_ERROR,
)


def normalize_value(value: str) -> str:
    return re.sub(r'[^a-zA-Zа-яА-Я0-9]+', '', value).lower()


def contains_reserved_fragment(value: str) -> bool:
    normalized = normalize_value(value)
    return any(
        fragment in normalized
        for fragment in NORMALIZED_RESERVED_FRAGMENT_VALUES
    )


def is_reserved_exact(value: str) -> bool:
    normalized = normalize_value(value)
    return normalized in NORMALIZED_RESERVED_EXACT_VALUES


def looks_like_email(value: str) -> bool:
    return bool(re.fullmatch(r'[^@\s]+@[^@\s]+\.[^@\s]+', value.strip()))


def validate_username_value(value: str) -> str:
    value = value.strip()
    USERNAME_REGEX_VALIDATOR(value)

    if looks_like_email(value):
        raise ValueError(USERNAME_EMAIL_LIKE_ERROR)

    if contains_reserved_fragment(value):
        raise ValueError(
            'Введите реальный username, а не email или служебное название поля.'
        )

    return value


def validate_first_name_value(value: str) -> str:
    value = value.strip()
    FIRST_NAME_REGEX_VALIDATOR(value)

    if looks_like_email(value):
        raise ValueError(FIRST_NAME_EMAIL_LIKE_ERROR)

    if is_reserved_exact(value):
        raise ValueError('Введите реальное имя, а не название поля.')

    return value


def validate_last_name_value(value: str) -> str:
    value = value.strip()
    LAST_NAME_REGEX_VALIDATOR(value)

    if looks_like_email(value):
        raise ValueError(LAST_NAME_EMAIL_LIKE_ERROR)

    if is_reserved_exact(value):
        raise ValueError('Введите реальную фамилию, а не название поля.')

    return value