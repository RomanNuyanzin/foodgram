import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Импортирует ингредиенты из data/ingredients.csv'

    def handle(self, *args, **options):
        file_path = (
            Path(__file__).resolve().parents[4] / 'data' / 'ingredients.csv')

        if not file_path.exists():
            self.stdout.write(
                self.style.ERROR(f'Файл не найден: {file_path}')
            )
            return

        created_count = 0

        with open(file_path, encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            for row in reader:
                if len(row) != 2:
                    continue

                name, measurement_unit = row
                _, created = Ingredient.objects.get_or_create(
                    name=name,
                    measurement_unit=measurement_unit,
                )
                if created:
                    created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Импорт завершён. Добавлено ингредиентов: {created_count}'
            )
        )
