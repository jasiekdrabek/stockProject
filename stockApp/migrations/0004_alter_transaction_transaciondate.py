# Generated by Django 5.0.6 on 2024-07-17 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockApp', '0003_selloffer_company'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='transacionDate',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
