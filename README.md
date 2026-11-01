# Overview

I wrote this software to learn how a server-side web framework builds pages from data, handles user input, and stores that data in a real database. Live Poll is a small web app where anyone can create a poll with a question and 2 to 6 options, share a link to it, and watch the results update live as people vote. Each browser can vote once per poll.

The app is built with Django and stores its polls and votes in a Supabase (PostgreSQL) database.

To start the test server and open the app:

1. Create and activate a virtual environment, then install the dependencies:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set `DATABASE_URL` to your Supabase connection string (Supabase dashboard > **Connect** > **Session pooler** URI, with your database password filled in). If `DATABASE_URL` is not set, the app falls back to a local SQLite file.
3. Create the database tables and start the server:
   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```
4. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in a web browser.

Run the automated tests with `python manage.py test`.

[Software Demo Video](http://youtube.link.goes.here)

# Web Pages

- **Home / Create Poll** (`/`): A form for entering a question and up to six options. When the form is submitted, Django validates it (the question can't be empty, at least two options are required, and options can't repeat) and either shows the errors or saves the poll and redirects to its vote page. Below the form is a list of the 10 most recent polls with their vote totals, pulled from the database.
- **Vote** (`/poll/<id>/`): Shows the question and options for the poll whose ID is in the URL, plus a "Copy link" button for sharing. Submitting a vote increases that option's count in the database and redirects to the results page. If this browser already voted in this poll (tracked with Django sessions), the page says so and links to the results instead.
- **Results** (`/poll/<id>/results/`): A bar chart of each option's vote count and percentage, calculated by the Django view from the database, with the leading option highlighted. It also shows when the last vote was cast; this time is saved on the poll in the database only when a vote is actually counted. A small JavaScript file asks the server for the latest numbers every 2.5 seconds (from `/poll/<id>/results.json`) and updates the chart in place, so results change live without reloading the page.

A poll ID that doesn't exist returns a 404 "Poll not found" page.

# Development Environment

- Visual Studio Code / Cursor, Git, and Windows PowerShell
- Django's built-in development server and test runner
- Supabase for hosting the PostgreSQL database

Languages and libraries:

- Python 3 with Django 6
- `psycopg` (PostgreSQL driver), `dj-database-url` (reads the database URL), and `python-dotenv` (loads `.env`)
- HTML (Django templates), CSS, and plain JavaScript (`fetch`) for the live results

# Useful Websites

- [Django Documentation](https://docs.djangoproject.com/)
- [Django Tutorial: Writing your first Django app](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
- [Supabase: Connecting to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [MDN: Using the Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)

# Future Work

- Add user accounts so people can manage and close their own polls.
- Use WebSockets (Django Channels) for instant updates instead of polling every few seconds.
- Make the one-vote rule stronger than a browser session (for example, sign-in or one-time codes).
