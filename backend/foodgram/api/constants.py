"""Файл для хранения констант."""

LENGTH_FOR_CHARFIELD = 150
"""Длина поля CharField."""

LEN_ERROR_MESSAGE = f'Длина строки не может превышать {LENGTH_FOR_CHARFIELD}'
"""Сообщение об ошибке при превышении длины строки."""

LENGTH_FOR_TEXTFIELD = 500
"""Длина поля TextField."""

LENGTH_FOR_EMAIL = 254
"""Длина поля Email пользователя."""

LENGTH_FOR_RECIPE_NAME = 200
"""Длина поля Name рецепта."""

RECIPES_APP_LABEL = 'recipes'
"""Название приложения для вызова класса модели."""

MIN_VALIDATOR_VALUE = 1
"""Минимальное значение для валидации."""

MIN_VALIDATOR_ERROR_MESSAGE = 'Количество должно быть больше одного'
"""Сообщение об ошибке при неверном миниальном значении."""

MAX_AMOUNT_VALUE = 10000
"""Максимально допустимое значение для количества ингредиента."""
