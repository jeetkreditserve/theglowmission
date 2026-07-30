#!/usr/bin/env sh
set -eu

/app/scripts/wait-for-db.sh postgres:5432 true
python manage.py migrate --noinput

last_availability_seed_date=""

while true; do
  today="$(TZ="${TIME_ZONE:-Asia/Kolkata}" date +%F)"
  if [ "$last_availability_seed_date" != "$today" ]; then
    python manage.py seed_appointment_availability \
      --start-offset-days "${APPOINTMENT_AVAILABILITY_SCHEDULER_OFFSET_DAYS:-91}" \
      --end-offset-days "${APPOINTMENT_AVAILABILITY_SCHEDULER_OFFSET_DAYS:-91}" \
      --quiet
    last_availability_seed_date="$today"
  fi
  python manage.py send_appointment_reminders
  sleep "${APPOINTMENT_SCHEDULER_POLL_SECONDS:-300}"
done
