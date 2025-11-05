from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("shop", "0004_productreview_and_more"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="productreview",
            name="unique_active_product_review",
        ),
        migrations.AddField(
            model_name="productreview",
            name="author_name",
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name="productreview",
            name="user",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="product_reviews",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddConstraint(
            model_name="productreview",
            constraint=models.UniqueConstraint(
                condition=models.Q(deleted_at__isnull=True, user__isnull=False),
                fields=("product", "user"),
                name="unique_active_product_review",
            ),
        ),
    ]
