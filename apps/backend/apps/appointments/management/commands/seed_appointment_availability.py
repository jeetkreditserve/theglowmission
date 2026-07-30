from datetime import time

from django.core.management.base import BaseCommand

from apps.appointments.models import AppointmentAvailabilityWindow


class Command(BaseCommand):
    help = "Seed default appointment availability windows for Monday through Saturday."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show which weekdays would be created without writing changes.",
        )
        parser.add_argument(
            "--label",
            default="Studio hours",
            help="Label for newly-created availability windows.",
        )
        parser.add_argument(
            "--ordering",
            type=int,
            default=0,
            help="Ordering for newly-created availability windows.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        label = options["label"]
        ordering = options["ordering"]
        starts_at = time(13, 30)
        ends_at = time(19, 30)
        existing_weekdays = set(
            AppointmentAvailabilityWindow.objects.filter(weekday__in=range(6)).values_list("weekday", flat=True)
        )
        created = 0
        skipped = 0
        would_create = 0

        for weekday in range(6):
            if weekday in existing_weekdays:
                skipped += 1
                continue
            if dry_run:
                would_create += 1
                continue
            AppointmentAvailabilityWindow.objects.create(
                weekday=weekday,
                starts_at=starts_at,
                ends_at=ends_at,
                active=True,
                label=label,
                ordering=ordering,
            )
            created += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Appointment availability seed complete created={created} would_create={would_create} "
                f"skipped={skipped} dry_run={dry_run}"
            )
        )
