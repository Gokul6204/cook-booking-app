# Cook Booking Platform

A full-stack web application for booking cooks, built with Django (Python) and MySQL, using HTML/CSS/vanilla JavaScript on the frontend.

## Features
- Custom user roles: customer and cook
- Cook profiles with cuisine, dishes, experience, hourly rate, availability, ratings
- Search/filter cooks by cuisine, dish, location, rating, price
- Booking flow with date/time selection and status tracking
- Reviews/ratings
- Dashboards for customers and cooks
- Django templates, responsive CSS, and vanilla JS with form validation

## Quickstart

1) Create and activate a virtual environment
```bash
python -m venv .venv
. .venv/Scripts/activate
# or on Unix/Mac
# source .venv/bin/activate
```

2) Install dependencies
```bash
pip install -r requirements.txt
```

3) Configure database
- Copy `.env.example` to `.env` and edit values.
- Defaults to SQLite if MySQL env vars are not set.

4) Apply migrations and create a superuser
```bash
python manage.py migrate
python manage.py createsuperuser
```

5) Run the server
```bash
python manage.py runserver
```

6) Access the app
- Home: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/

## Environment Variables
Copy `.env.example` to `.env` and update as needed.
- DATABASE_ENGINE=mysql
- DATABASE_NAME=cook_booking
- DATABASE_USER=root
- DATABASE_PASSWORD=yourpassword
- DATABASE_HOST=127.0.0.1
- DATABASE_PORT=3306

If MySQL variables are not provided, the project will use SQLite.

## Notes
- This project uses a custom user model (`core.User`). Create migrations before first run if you change models.
- Static files are served via Django during development. For production, configure a proper static files server.

