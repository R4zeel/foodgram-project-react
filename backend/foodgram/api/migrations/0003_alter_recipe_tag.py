# Generated by Django 5.0.3 on 2024-03-29 16:50

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_rename_metric_ingredient_measure'),
    ]

    operations = [
        migrations.AlterField(
            model_name='recipe',
            name='tag',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tag', verbose_name='Тэг'),
        ),
    ]
