from django.shortcuts import render, redirect

from django.db import connection

from django.contrib.auth.decorators import login_required
from postgres_manager.models import Databases

from random import randint


def random_string(
    allowed="abcdefghijklmnpqrstuvwxyzABCDEFGHIJKLMNPQRSTUVWXYZ123456789-",
    max=30,
    is_password=True,
):
    new_name = ""
    for a in range(max):
        new_name = new_name + allowed[randint(0, len(allowed) - 1)]

    if is_password:
        return new_name

    is_ever_used = Databases.objects.filter(name=new_name)
    if not is_ever_used:
        return new_name
    random_string(allowed, max)


@login_required
def index(request):
    # populate_fake()
    databases = Databases.objects.all()
    return render(request, "render_accounts.html", context={"databases": databases})


@login_required
def create(request):
    # Create a new database
    new_user = random_string(max=15, is_password=False)
    new_password = random_string()
    new_database = Databases(name=new_user, password=new_password)
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE {new_user};")
        cursor.execute(
            f"CREATE USER {new_user} WITH ENCRYPTED PASSWORD '{new_password}';"
        )
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {new_user} TO {new_user};")
    new_database.save()
    return redirect('/')


@login_required
def delete(request):
    # Delete an existing database
    database_id = request.GET.get("id", None)
    database_to_delete = Databases.objects.filter(id=database_id)[0]
    name = database_to_delete.name
    with connection.cursor() as cursor:
        cursor.execute(f"DROP DATABASE IF EXISTS {name};")
        cursor.execute(f"DROP ROLE IF EXISTS {name};")
    database_to_delete.delete()
    return redirect('/')


def populate_fake():
    fake_databases = [
        {"name": "dskqI", "password": "OOO930dd"},
        {"name": "KF9328", "password": "OOO93DDDdd"},
        {"name": "EKFIfI", "password": "OOEZKSId"},
        {"name": "MMDPXx", "password": "OwwXXSI"},
    ]

    for database in fake_databases:
        new_database = Databases(name=database["name"], password=database["password"])
        new_database.save()
    print("Done.")
