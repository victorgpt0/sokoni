"""
Management command to seed users and customer profiles.
Usage: python manage.py seed_users --count 25
"""

import random
from datetime import datetime, date

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import transaction
from accounts.models import Customer, CustomerAddress


class Command(BaseCommand):
    help = "Seed users with customer profiles and addresses"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            type=int,
            default=25,
            help="Number of users to create (default: 25)",
        )
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Clear existing non-superuser users before seeding",
        )
        parser.add_argument(
            "--with-addresses",
            action="store_true",
            help="Create addresses for each user",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            self.stdout.write(self.style.WARNING("Clearing existing users..."))
            # Don't delete superusers
            CustomerAddress.objects.all().delete()
            Customer.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()

        with transaction.atomic():
            users = self.create_users(options["count"])
            self.stdout.write(f"Created {len(users)} users with customer profiles")

            if options["with_addresses"]:
                addresses = self.create_addresses(users)
                self.stdout.write(f"Created {len(addresses)} customer addresses")

        self.stdout.write(self.style.SUCCESS("User seeding completed successfully!"))

    def create_users(self, count):
        """Create users with customer profiles."""
        # Kenyan and international names
        first_names = [
            # Kenyan names
            "Wanjiku",
            "Kamau",
            "Atieno",
            "Ochieng",
            "Njeri",
            "Mwangi",
            "Akinyi",
            "Otieno",
            "Wanjiru",
            "Kariuki",
            "Adhiambo",
            "Kipchoge",
            "Nyawira",
            "Kiptoo",
            "Wambui",
            "Koech",
            "Awino",
            "Rotich",
            "Wairimu",
            "Langat",
            "Nekesa",
            "Bett",
            "Mumbua",
            "Tanui",
            # International names
            "John",
            "Sarah",
            "Michael",
            "Emily",
            "David",
            "Jessica",
            "Christopher",
            "Ashley",
            "Daniel",
            "Amanda",
            "Matthew",
            "Lisa",
            "Andrew",
            "Michelle",
            "Joshua",
            "Jennifer",
            "Anthony",
            "Elizabeth",
            "Kevin",
            "Nicole",
            "Brian",
            "Stephanie",
            "Mark",
            "Helen",
        ]

        last_names = [
            # Kenyan surnames
            "Wanjiku",
            "Kamau",
            "Ochieng",
            "Otieno",
            "Mwangi",
            "Kariuki",
            "Kipchoge",
            "Kiptoo",
            "Koech",
            "Rotich",
            "Langat",
            "Bett",
            "Tanui",
            "Cheruiyot",
            "Kiprotich",
            "Kemboi",
            "Mutua",
            "Mwenda",
            "Nyong'o",
            "Odinga",
            "Ruto",
            "Gachagua",
            "Waiguru",
            "Kidero",
            # International surnames
            "Smith",
            "Johnson",
            "Williams",
            "Brown",
            "Jones",
            "Garcia",
            "Miller",
            "Davis",
            "Rodriguez",
            "Martinez",
            "Hernandez",
            "Lopez",
            "Gonzalez",
            "Wilson",
            "Anderson",
            "Thomas",
            "Taylor",
            "Moore",
            "Jackson",
            "Martin",
            "Lee",
            "Thompson",
            "White",
        ]

        # Kenyan phone number prefixes
        kenyan_prefixes = [
            "254701",
            "254702",
            "254703",
            "254704",
            "254705",
            "254706",
            "254707",
            "254708",
            "254709",
            "254710",
            "254711",
            "254712",
            "254713",
            "254714",
            "254715",
            "254716",
            "254717",
            "254718",
            "254719",
            "254720",
            "254721",
            "254722",
            "254723",
            "254724",
            "254725",
            "254726",
            "254727",
            "254728",
        ]

        users = []
        existing_usernames = set(User.objects.values_list("username", flat=True))
        existing_emails = set(User.objects.values_list("email", flat=True))

        for i in range(count):
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)

            # Generate unique username
            base_username = f"{first_name.lower().replace('\'', '')}.{last_name.lower().replace('\'', '')}"
            username = base_username
            counter = 1
            while username in existing_usernames:
                username = f"{base_username}{counter}"
                counter += 1
            existing_usernames.add(username)

            # Generate unique email
            base_email = f"{username}@example.com"
            email = base_email
            counter = 1
            while email in existing_emails:
                email = f"{username}{counter}@example.com"
                counter += 1
            existing_emails.add(email)

            try:
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password="password123",  # Same password for all test users
                    first_name=first_name,
                    last_name=last_name,
                    is_active=True,
                )

                # Create customer profile
                phone_suffix = "".join([str(random.randint(0, 9)) for _ in range(6)])
                phone_number = f"+{random.choice(kenyan_prefixes)}{phone_suffix}"

                Customer.objects.create(
                    user=user,
                    phone_number=phone_number,
                    date_of_birth=self.generate_birth_date(),
                    gender=random.choice(["M", "F", "O"]),
                )

                users.append(user)

                if (i + 1) % 10 == 0:
                    self.stdout.write(f"Created {i + 1} users...")

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Error creating user {username}: {str(e)}")
                )
                continue

        return users

    def create_addresses(self, users):
        """Create realistic Kenyan addresses for users."""
        kenyan_cities = [
            "Nairobi",
            "Mombasa",
            "Kisumu",
            "Nakuru",
            "Eldoret",
            "Thika",
            "Malindi",
            "Kitale",
            "Garissa",
            "Kakamega",
            "Machakos",
            "Meru",
            "Nyeri",
            "Kericho",
            "Embu",
            "Migori",
            "Homa Bay",
            "Bungoma",
            "Voi",
            "Wajir",
            "Isiolo",
            "Narok",
            "Nanyuki",
            "Kajiado",
        ]

        nairobi_areas = [
            "Westlands",
            "Karen",
            "Kilimani",
            "Lavington",
            "Parklands",
            "Kileleshwa",
            "South B",
            "South C",
            "Runda",
            "Muthaiga",
            "Spring Valley",
            "Riverside",
            "Hurlingham",
            "Kiambu Road",
            "Ngong Road",
            "Thika Road",
            "Mombasa Road",
        ]

        mombasa_areas = [
            "Nyali",
            "Bamburi",
            "Shanzu",
            "Tudor",
            "Changamwe",
            "Likoni",
            "Old Town",
            "Mvita",
            "Kisauni",
            "Jomba",
        ]

        street_names = [
            "Kimathi Street",
            "Uhuru Highway",
            "Kenyatta Avenue",
            "Moi Avenue",
            "Harambee Avenue",
            "University Way",
            "Tom Mboya Street",
            "Jogoo Road",
            "Ngong Road",
            "Waiyaki Way",
            "Outer Ring Road",
            "Thika Road",
            "Valley Road",
            "Riverside Drive",
            "Mama Ngina Street",
            "Haile Selassie Avenue",
        ]

        kenyan_counties = [
            "Nairobi",
            "Mombasa",
            "Kisumu",
            "Nakuru",
            "Uasin Gishu",
            "Kiambu",
            "Kilifi",
            "Trans Nzoia",
            "Garissa",
            "Kakamega",
            "Machakos",
            "Meru",
            "Nyeri",
            "Kericho",
            "Embu",
            "Migori",
            "Homa Bay",
            "Bungoma",
        ]

        addresses = []
        for user in users:
            # Create 1-3 addresses per user
            num_addresses = random.randint(1, 3)

            for i in range(num_addresses):
                city = random.choice(kenyan_cities)

                # Use specific areas for major cities
                if city == "Nairobi":
                    area = random.choice(nairobi_areas)
                    street = f"{random.choice(street_names)}, {area}"
                elif city == "Mombasa":
                    area = random.choice(mombasa_areas)
                    street = f"{random.choice(street_names)}, {area}"
                else:
                    street = f"{random.randint(1, 999)} {random.choice(street_names)}"

                # Generate apartment/house number
                apartment = ""
                if random.choice([True, False]):  # 50% chance of apartment
                    if city in ["Nairobi", "Mombasa", "Kisumu"]:
                        apartment = f"Apartment {random.randint(1, 50)}, Floor {random.randint(1, 10)}"
                    else:
                        apartment = f"House {random.randint(1, 200)}"

                try:
                    address = CustomerAddress.objects.create(
                        customer=user.customer,
                        type=random.choice(["shipping", "billing"]),
                        first_name=user.first_name,
                        last_name=user.last_name,
                        company=(
                            f"{random.choice(['', 'Safaricom', 'Equity Bank', 'KCB', 'Co-op Bank', 'EABL', 'Kenya Airways'])}"
                            if random.random() < 0.3
                            else ""
                        ),
                        address_line_1=street,
                        address_line_2=apartment,
                        city=city,
                        state=random.choice(kenyan_counties),
                        postal_code=f"{random.randint(10000, 99999)}-{random.randint(10000, 99999)}",
                        country="Kenya",
                        is_default=(i == 0),  # First address is default
                    )
                    addresses.append(address)

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Error creating address for {user.username}: {str(e)}"
                        )
                    )
                    continue

        return addresses

    def generate_birth_date(self):
        """Generate a realistic birth date."""
        # Age between 18 and 70
        current_year = datetime.now().year
        birth_year = random.randint(current_year - 70, current_year - 18)
        birth_month = random.randint(1, 12)

        # Handle February and leap years
        if birth_month == 2:
            max_day = 29 if birth_year % 4 == 0 else 28
        elif birth_month in [4, 6, 9, 11]:
            max_day = 30
        else:
            max_day = 31

        birth_day = random.randint(1, max_day)

        return date(birth_year, birth_month, birth_day)
