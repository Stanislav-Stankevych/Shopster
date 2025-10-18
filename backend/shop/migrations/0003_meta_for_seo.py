from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0002_soft_delete"),
    ]

    operations = [
        migrations.AddField(
            model_name="category",
            name="meta_title",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="category",
            name="meta_description",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="product",
            name="meta_title",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name="product",
            name="meta_description",
            field=models.CharField(blank=True, max_length=500),
        ),
        migrations.AddField(
            model_name="product",
            name="meta_keywords",
            field=models.CharField(blank=True, max_length=255),
        ),
    ]
