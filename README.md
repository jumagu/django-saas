# SaaS Project

This is a SaaS (Software as a Service) boilerplate.

## Features

- User authentication and authorization
- Subscription management
- Payment integration with Stripe
- Admin dashboard

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/jumagu/django-saas.git
   cd django-saas
   ```

2. Create a virtual environment and activate it:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Apply migrations:

   ```bash
   python manage.py migrate
   ```

5. Create a superuser:

   ```bash
   python manage.py createsuperuser
   ```

6. Run the development server:
   ```bash
   python manage.py runserver
   ```

## Usage

- Access the App at `http://127.0.0.1:8000/`
- Access the admin dashboard at `http://127.0.0.1:8000/admin/`
