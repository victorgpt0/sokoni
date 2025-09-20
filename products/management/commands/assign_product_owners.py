from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from products.models import Product


class Command(BaseCommand):
    help = "Assign existing products to users"

    def handle(self, *args, **options):
        # Get the first superuser or create one if none exists
        try:
            default_user = User.objects.filter(is_superuser=True).first()
            if not default_user:
                default_user = User.objects.first()
            if not default_user:
                self.stdout.write(
                    self.style.ERROR("No users found. Please create a user first.")
                )
                return
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error finding default user: {e}"))
            return

        # Count products without users
        products_without_user = Product.objects.filter(user__isnull=True)
        count = products_without_user.count()

        if count == 0:
            self.stdout.write(
                self.style.SUCCESS("All products already have owners assigned.")
            )
            return

        # Assign all products without users to the default user
        products_without_user.update(user=default_user)

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully assigned {count} products to user: {default_user.username}"
            )
        )
