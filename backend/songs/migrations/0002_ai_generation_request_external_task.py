# Generated manually for Exercise 4 (Strategy pattern external task tracking)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("songs", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="aigenerationrequest",
            name="external_task_id",
            field=models.CharField(blank=True, db_index=True, max_length=128),
        ),
        migrations.AddField(
            model_name="aigenerationrequest",
            name="external_status",
            field=models.CharField(blank=True, max_length=64),
        ),
    ]
