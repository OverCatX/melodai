# Generated manually

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("songs", "0003_alter_user_options_rename_google_id_user_username_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="email",
            field=models.EmailField(blank=True, default="", max_length=254),
        ),
        migrations.AddField(
            model_name="user",
            name="google_id",
            field=models.CharField(
                blank=True, db_index=True, max_length=255, null=True, unique=True
            ),
        ),
        migrations.AddField(
            model_name="user",
            name="session_token",
            field=models.CharField(
                blank=True, db_index=True, max_length=128, null=True, unique=True
            ),
        ),
    ]
