from pathlib import Path
import csv

from django.core.management.base import BaseCommand
from django.apps import apps
from django.db.utils import IntegrityError

from utils.constants import API_APP_LABEL


class FileOpenException(Exception):
    """Вызов исключения при некорректном открытии файла."""
    pass


class Command(BaseCommand):
    """Команда для импорта данных из CSV-файла."""
    def handle(self, **options):
        files = [
            'ingredient.csv',
        ]
        for file in files:
            model_name = Path(file).stem
            model_class = apps.get_model(API_APP_LABEL, model_name)
            try:
                with open(f'static/data/{file}', newline='') as f:
                    dataframe = csv.DictReader(f)
                    for row in dataframe:
                        try:
                            model_class.objects.create(**row)
                        except IntegrityError:
                            self.stdout.write(
                                f'Object {model_name} ID:'
                                f'{row.get("id")} already exists'
                            )
                            continue
                    self.stdout.write(
                        f'Data import finished for model: {model_name}'
                    )
            except FileOpenException as error:
                self.stdout.write(f'Ошибка при открытии файла: {error}')
                continue
