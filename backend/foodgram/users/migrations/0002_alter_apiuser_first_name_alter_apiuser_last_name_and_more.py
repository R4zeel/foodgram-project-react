# Generated by Django 5.0.3 on 2024-04-03 20:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='apiuser',
            name='first_name',
            field=models.CharField(max_length=150, verbose_name='Имя'),
        ),
        migrations.AlterField(
            model_name='apiuser',
            name='last_name',
            field=models.CharField(max_length=150, verbose_name='Фамилия'),
        ),
        migrations.AlterField(
            model_name='apiuser',
            name='password',
            field=models.CharField(max_length=150, verbose_name='Пароль'),
        ),
        migrations.AlterField(
            model_name='apiuser',
            name='role',
            field=models.CharField(max_length=150, verbose_name='Роль'),
        ),
    ]
