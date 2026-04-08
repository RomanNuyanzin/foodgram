from .constants import BASE36_ALPHABET, BASE36_RADIX


def encode_base36(number):
    if number < 0:
        raise ValueError('Число должно быть неотрицательным.')

    if number == 0:
        return '0'

    result = ''
    while number:
        number, remainder = divmod(number, BASE36_RADIX)
        result = BASE36_ALPHABET[remainder] + result
    return result


def decode_base36(value):
    return int(value, BASE36_RADIX)
