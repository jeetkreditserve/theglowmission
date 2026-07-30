from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("appointments", "0002_appointment_photos_and_finance"),
    ]

    operations = [
        migrations.AddField(
            model_name="appointmentavailabilitywindow",
            name="date",
            field=models.DateField(blank=True, db_index=True, null=True),
        ),
        migrations.AlterModelOptions(
            name="appointmentavailabilitywindow",
            options={"ordering": ["date", "weekday", "ordering", "starts_at", "id"]},
        ),
        migrations.AddIndex(
            model_name="appointmentavailabilitywindow",
            index=models.Index(fields=["date", "starts_at"], name="appointment_date_77b8e5_idx"),
        ),
        migrations.AddIndex(
            model_name="appointmentavailabilitywindow",
            index=models.Index(fields=["weekday", "starts_at"], name="appointment_weekda_c56b14_idx"),
        ),
    ]
