ALPHABET = '0123456789abcdefghijklmnopqrstuvwxyz'


def encode_base36(number):
    if number < 0:
        raise ValueError('Число должно быть неотрицательным.')

    if number == 0:
        return '0'

    result = ''
    while number:
        number, remainder = divmod(number, 36)
        result = ALPHABET[remainder] + result
    return result


def decode_base36(value):
    return int(value, 36)
