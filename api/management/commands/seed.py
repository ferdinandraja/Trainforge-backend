from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from api.models import Subscription

User = get_user_model()


class Command(BaseCommand):
    help = "Seed database with admin and demo users"

    def handle(self, *args, **kwargs):

        # ADMIN
        if not User.objects.filter(username="admin").exists():

            admin = User.objects.create_superuser(
                username="admin",
                email="admin@trainforge.com",
                password="Admin123!"
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "Admin user created"
                )
            )

        else:
            admin = User.objects.get(username="admin")

            self.stdout.write(
                self.style.WARNING(
                    "Admin already exists"
                )
            )

        # TRAINER
        if not User.objects.filter(username="trainer1").exists():

            trainer = User.objects.create_user(
                username="trainer1",
                email="trainer1@trainforge.com",
                password="Trainer123!"
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "Trainer user created"
                )
            )

        else:
            trainer = User.objects.get(username="trainer1")

            self.stdout.write(
                self.style.WARNING(
                    "Trainer already exists"
                )
            )

        # SUBSCRIPTION
        if not Subscription.objects.filter(
            trainer=trainer
        ).exists():

            Subscription.objects.create(
                trainer=trainer,
                plan_name="professional",
                status="active",
                monthly_price=49.99,
                start_date="2026-01-01",
            )

            self.stdout.write(
                self.style.SUCCESS(
                    "Subscription created"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Database seeded successfully"
            )
        )