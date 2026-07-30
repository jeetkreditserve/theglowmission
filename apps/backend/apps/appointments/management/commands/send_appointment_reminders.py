from django.core.management.base import BaseCommand

from apps.appointments.services import send_due_appointment_reminders


class Command(BaseCommand):
    help = "Send due appointment reminders once for each configured reminder offset."

    def handle(self, *args, **options):
        result = send_due_appointment_reminders()
        self.stdout.write(self.style.SUCCESS(f"Appointment reminders sent={result['sent']} skipped={result['skipped']}"))
