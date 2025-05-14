from django import template

register = template.Library()

@register.filter
def bengali_numbers(value):
    """Convert an integer to its Bengali numeral representation."""
    if isinstance(value, int):
        bengali_numerals = {
            '0': '০', '1': '১', '2': '২', '3': '৩',
            '4': '৪', '5': '৫', '6': '৬', '7': '৭',
            '8': '৮', '9': '৯'
        }
        return ''.join(bengali_numerals.get(digit, digit) for digit in str(value))
    return value
