# Generated by Django 5.1.1 on 2024-10-12 13:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('stockApp', '0005_rename_change_amount_balanceupdate_changeamount_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='trafficlog',
            name='userClass',
            field=models.CharField(default='WebsiteActiveUser', max_length=255),
        ),
    ]