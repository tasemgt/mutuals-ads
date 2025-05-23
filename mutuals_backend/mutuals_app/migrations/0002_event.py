# Generated by Django 5.2 on 2025-05-24 17:41

import jsonfield.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("mutuals_app", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("event_id", models.IntegerField(unique=True)),
                ("event_name", models.CharField(max_length=255)),
                ("event_date", models.DateField()),
                ("location", models.CharField(max_length=100)),
                ("ticket_price", models.FloatField()),
                ("venue_id", models.IntegerField()),
                ("tags", jsonfield.fields.JSONField()),
            ],
        ),
    ]
