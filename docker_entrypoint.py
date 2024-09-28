import os
import sys
from subprocess import run

import django
from django.contrib.auth import get_user_model


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "hsa_update_server.settings")
    django.setup()
    migrate_if_needed()
    create_superuser_if_needed()
    print("Running server.")
    sys.exit(
        run(["gunicorn", "--bind", "0.0.0.0:8000", "-w", str(os.cpu_count() * 2), "hsa_update_server.wsgi"]).returncode
    )
 

def migrate_if_needed():
    print("Checking database for unapplied migrations.")
    res = run(["python", "manage.py", "migrate", "--check"], capture_output=True)
    if res.returncode == 0:
        print("Okay.")
    elif len(res.stderr) > 0:
        sys.stderr.buffer.write(res.stderr)
        sys.stderr.flush()
        sys.exit(res.returncode)
    else:
        print("Applying migrations.")
        res = run(["python", "manage.py", "migrate"])
        if res.returncode != 0:
            sys.exit(res.returncode)


def create_superuser_if_needed():
    print("Checking for superuser.")
    User = get_user_model()
    if User.objects.filter(is_superuser=True).count() > 0:
        print("Superuser already exists")
        return
    if (
        "HSA_SUPERUSER_USERNAME" not in os.environ
        or "HSA_SUPERUSER_PASSWORD" not in os.environ
    ):
        print(
            "Unable to create the superuser as one of the HSA_SUPERUSER_USERNAME or HSA_SUPERUSER_PASSWORD environment variables is not set. Exiting."
        )
        sys.exit(1)
    User.objects.create_superuser(
        os.environ["HSA_SUPERUSER_USERNAME"], None, os.environ["HSA_SUPERUSER_PASSWORD"]
    )
    print("Superuser created.")


if __name__ == "__main__":
    main()
