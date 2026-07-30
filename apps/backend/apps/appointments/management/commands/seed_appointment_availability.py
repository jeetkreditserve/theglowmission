from datetime import timedelta, time

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.appointments.models import AppointmentAvailabilityWindow


class Command(BaseCommand):
    help = "Seed default dated appointment availability windows for Monday through Saturday."

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show which dates would be created without writing changes.",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress output when no windows are created.",
        )
        parser.add_argument(
            "--only-if-empty",
            action="store_true",
            help="Seed only when no appointment availability windows exist.",
        )
        parser.add_argument(
            "--start-offset-days",
            type=int,
            default=0,
            help="First date offset from today to seed.",
        )
        parser.add_argument(
            "--end-offset-days",
            type=int,
            default=None,
            help="Last date offset from today to seed, inclusive. Defaults to APPOINTMENT_SLOT_HORIZON_DAYS.",
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
        quiet = options["quiet"]
        only_if_empty = options["only_if_empty"]
        label = options["label"]
        ordering = options["ordering"]
        start_offset_days = max(int(options["start_offset_days"]), 0)
        end_offset_days = options["end_offset_days"]
        if end_offset_days is None:
            end_offset_days = int(getattr(settings, "APPOINTMENT_SLOT_HORIZON_DAYS", 91))
        end_offset_days = max(int(end_offset_days), start_offset_days)
        starts_at = time(13, 30)
        ends_at = time(19, 30)

        if only_if_empty and AppointmentAvailabilityWindow.objects.exists():
            if not quiet:
                self.stdout.write(
                    self.style.SUCCESS("Appointment availability seed skipped because windows already exist.")
                )
            return

        today = timezone.localdate()
        start_date = today + timedelta(days=start_offset_days)
        end_date = today + timedelta(days=end_offset_days)
        existing_dates = set(
            AppointmentAvailabilityWindow.objects.filter(
                date__gte=start_date,
                date__lte=end_date,
            ).values_list("date", flat=True)
        )
        created = 0
        skipped = 0
        would_create = 0

        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() == 6:
                current_date += timedelta(days=1)
                continue
            if current_date in existing_dates:
                skipped += 1
                current_date += timedelta(days=1)
                continue
            if dry_run:
                would_create += 1
                current_date += timedelta(days=1)
                continue
            AppointmentAvailabilityWindow.objects.create(
                date=current_date,
                weekday=current_date.weekday(),
                starts_at=starts_at,
                ends_at=ends_at,
                active=True,
                label=label,
                ordering=ordering,
            )
            created += 1
            current_date += timedelta(days=1)

        if quiet and not created and not would_create:
            return
        self.stdout.write(
            self.style.SUCCESS(
                f"Appointment availability seed complete created={created} would_create={would_create} "
                f"skipped={skipped} start_date={start_date.isoformat()} end_date={end_date.isoformat()} dry_run={dry_run}"
            )
        )
