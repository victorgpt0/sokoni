from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0001_initial'),
    ]

    operations = [
        migrations.AddConstraint(
            model_name='product',
            constraint=models.CheckConstraint(
                check=models.Q(stock_quantity__gte=0),
                name='products_product_stock_quantity_non_negative'
            ),
        ),
    ]

