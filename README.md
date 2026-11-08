# SaaS Project

A Django SaaS boilerplate with user accounts, Stripe subscriptions, and plan-based permissions.

## Features

- Sign-up and login with [django-allauth](https://docs.allauth.org/) (username or email, optional GitHub login, mandatory email verification)
- Subscription plans and prices managed from the Django admin and synced to Stripe
- Stripe Checkout for subscribing, plus billing pages to view, refresh, and cancel a plan
- Plan-based access control through Django groups and permissions
- Landing page, pricing page, and user dashboard styled with Tailwind CSS and DaisyUI (light/dark theme)

## Tech stack

- Python / Django 5.0
- PostgreSQL ([Neon](https://neon.tech/)) in production, SQLite for local development
- Stripe
- Tailwind CSS 3 + DaisyUI
- Docker, deployed on [Railway](https://railway.app/)

## Requirements

- Python 3.12 (Django 5.0 supports Python 3.10 to 3.12, and 3.12 is the version used by the Dockerfile and CI)
- Node.js 20+ and npm (to build the CSS)
- A Stripe account (test keys are fine for local development)
- An SMTP account to send verification emails (for example, Gmail with an app password)

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

3. Install the Python and Node.js dependencies:

   ```bash
   pip install -r requirements.txt
   npm install
   ```

4. Create your `.env` file in the project root and fill it in (see [Environment variables](#environment-variables)):

   ```bash
   cp .env.example .env
   ```

   > **Important:** if you want to use SQLite locally, delete or comment out the `DATABASE_URL` line. An empty `DATABASE_URL=""` makes Django fail with `ImproperlyConfigured`.

5. Build the CSS:

   ```bash
   npm run tailwind:build
   ```

6. Apply migrations and create a superuser. Django commands run from the `src/` directory:

   ```bash
   cd src
   python manage.py migrate
   python manage.py createsuperuser
   ```

7. Run the development server:

   ```bash
   python manage.py runserver
   ```

While working on templates, run `npm run tailwind:dev` from the project root in a second terminal to rebuild the CSS on every change.

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `DJANGO_SECRET_KEY` | Yes | Django secret key. |
| `DJANGO_DEBUG` | Yes | `1` for development, `0` for production. |
| `BASE_URL` | Yes | Public URL of the app, without a trailing slash (`http://localhost:8000` locally). Used to build the Stripe Checkout return URLs. |
| `STRIPE_SECRET_KEY` | Yes | Stripe secret key. Plans, prices, and customers are created in Stripe when they are saved. |
| `STRIPE_TEST_OVERRIDE` | No | Set to `1` to allow a `sk_test_` key when `DJANGO_DEBUG=0`. Without it, a test key in production raises an error. |
| `DATABASE_URL` | No | PostgreSQL connection string. If it is not set, SQLite (`src/db.sqlite3`) is used. |
| `GITHUB_CLIENT_ID` | No | Client ID of the GitHub OAuth App. See [GitHub login](#github-login-optional). |
| `GITHUB_CLIENT_SECRET` | No | Client secret of the GitHub OAuth App. |
| `CONN_MAX_AGE` | No | Database connection lifetime in seconds. Default: `300`. |
| `EMAIL_HOST` | Yes* | SMTP host. Default: `smtp.gmail.com`. |
| `EMAIL_PORT` | Yes* | SMTP port. Default: `587`. |
| `EMAIL_HOST_USER` | Yes* | SMTP user. |
| `EMAIL_HOST_PASSWORD` | Yes* | SMTP password or app password. |
| `EMAIL_USE_TLS` | No | Default: `True`. |
| `EMAIL_USE_SSL` | No | Default: `False`. |
| `ADMIN_USER_NAME` | No | Name of the admin who receives server error (500) emails. |
| `ADMIN_USER_EMAIL` | No | Email of that admin. Error emails are only sent if it is set. |

\* Sign-up requires email verification, so without a working SMTP configuration users cannot register.

`STRIPE_PUBLIC_KEY` and `DJANGO_VERSION` appear in `.env.example` but are not read by the code yet.

## Setting up plans

To create the default plans (Starter, Pro, and Enterprise), run:

```bash
python manage.py setup_plans
```

It reuses the products and prices that already exist in the Stripe test account, so nothing new is created in Stripe. It also creates a group for each plan and syncs its permissions. It is safe to run more than once, and it stops without changes if a price doesn't match what is in Stripe.

To create other plans by hand:

1. Go to the admin (`/admin/`) and create a **Subscription** (a plan). Saving it creates the matching product in Stripe.
2. Add one or more **Subscription prices** to the plan (monthly or yearly). Each one creates a price in Stripe. Only prices marked as *featured* appear on `/pricing/`.
3. Assign at least one group and one permission (`basic`, `pro`, `advanced`, `basic_ai`) to the plan (the admin requires both), then run:

   ```bash
   python manage.py sync_permissions
   ```

   When a user subscribes, they are added to the plan's groups, so you can check access with `user.has_perm('subscriptions.pro')`.

Users can only check out after confirming their email, because that is when their Stripe customer is created.

## GitHub login (optional)

1. Create an OAuth App in GitHub (*Settings → Developer settings → OAuth Apps*) with the callback URL `http://localhost:8000/accounts/github/login/callback/`. An OAuth App accepts a single callback domain, so production needs its own app with `https://<your-domain>/accounts/github/login/callback/`.
2. Set the app's client ID and secret as `GITHUB_CLIENT_ID` and `GITHUB_CLIENT_SECRET`, then restart the server.

If either variable is missing, the GitHub button is not shown. Don't also add a GitHub **Social application** in the Django admin: allauth fails if the same provider is configured in both places.

## Management commands

Run them from `src/`:

| Command | Description |
| --- | --- |
| `python manage.py setup_plans` | Creates the default plans, their prices, and groups using the existing Stripe products and prices. See [Setting up plans](#setting-up-plans). |
| `python manage.py sync_permissions` | Copies each active plan's permissions to its groups. |
| `python manage.py sync_user_subs` | Refreshes active user subscriptions from Stripe. Accepts `--days-left`, `--days-ago`, `--days-start`, and `--days-end` to filter by period end date. |
| `python manage.py sync_user_subs --clear-dangling` | Cancels active Stripe subscriptions that don't belong to any user subscription in the database. |
| `python manage.py vendor_pull` | Downloads third-party static files into `src/staticfiles/vendors`. |

## Deployment

The app is deployed to Railway using the `Dockerfile`. The container builds the CSS, collects static files, runs migrations on startup, and serves the app with Gunicorn. Set the environment variables above in Railway.

GitHub Actions workflows in `.github/workflows`:

- **5 - Branch Neon DB for Django Tests**: on every push to `master`, creates a temporary Neon branch from `production` and runs the test suite against it.
- **6 - Schedule a Production Worker**: syncs subscriptions with Stripe twice a day, and clears dangling subscriptions on the 1st of each month.

Both need the repository secrets `NEON_API_KEY` and `NEON_PROJECT_ID`. Workflow 6 also needs `STRIPE_SECRET_KEY`.

## Usage

- App: `http://127.0.0.1:8000/`
- Pricing: `http://127.0.0.1:8000/pricing/`
- Dashboard: `http://127.0.0.1:8000/dashboard/`
- Billing: `http://127.0.0.1:8000/accounts/billing/`
- Admin: `http://127.0.0.1:8000/admin/`
