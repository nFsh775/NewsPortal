from django import template


register = template.Library()

bad_words = [
    'шутер',
    'Обама',
    'пивоваренное',
]

@register.filter()
def censor_text(text):
    if not isinstance(text, str):
        raise ValueError("Фильтр может быть применен только к строковым переменным")

    for word in bad_words:
        censored_word = word[0] + '*' * (len(word) - 1)
        text = text.replace(word, censored_word)
        text = text.replace(word.capitalize(), censored_word.capitalize())

    return text