# Generated by Django 4.2.7 on 2024-01-19 06:57

import CreditApp.models
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("CreditApp", "0007_alter_customer_approved_limit"),
    ]

    operations = [
        migrations.AlterField(
            model_name="loan",
            name="end_date",
            field=models.DateField(
                null=True, validators=[CreditApp.models.validate_date_not_past]
            ),
        ),
        migrations.AlterField(
            model_name="loan",
            name="start_date",
            field=models.DateField(
                null=True, validators=[CreditApp.models.validate_date_not_past]
            ),
        ),
    ]