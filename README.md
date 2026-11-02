# Overview

{Important!  Do not say in this section that this is college assignment.  Talk about what you are trying to accomplish as a software engineer to further your learning.}

As a software engineer, my goal with this project was to master full-stack web development using a robust server-side framework. I wanted to understand how backend web architectures process user input, interact securely with relational databases, manage client sessions, and communicate with modern browser APIs to deliver real-time reactive experiences without relying on heavy frontend frameworks.

{Provide a description the web app that you wrote. Describe how to start a test server on your computer and what website to open up to see the first page of the app.}

Live Poll is an interactive web application where users can create custom polls with 2 to 6 options, share a direct link with others, cast votes with one-vote-per-browser protection, and observe real-time animated results updating live as votes come in.

To start the test server on your computer:
1. Create and activate a Python virtual environment, then install the dependencies:
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```
2. Copy `.env.example` to `.env` and set `DATABASE_URL` to your Supabase PostgreSQL connection string (or leave it unset to use the local SQLite fallback).
3. Apply the database migrations and start the Django development server:
   ```powershell
   python manage.py migrate
   python manage.py runserver
   ```
4. Open your web browser and navigate to:
   ```
   http://127.0.0.1:8000/
   ```

{Describe your purpose for writing this software.}

The purpose of writing this software is to gain hands-on proficiency in building production-grade, database-backed web applications. I wanted to deepen my understanding of model-view-controller (MVC/MVT) patterns, atomic database transactions that prevent race conditions during concurrent user voting, RESTful JSON polling architectures, and deploying serverless applications backed by cloud-hosted PostgreSQL (Supabase) and Vercel.

{Provide a link to your YouTube demonstration.  It should be a 4-5 minute demo of the software running (starting the server and navigating through the web pages) and a walkthrough of the code.}

[Software Demo Video]()

# Web Pages

{Describe each of the web pages you created and how the web app transitions between each of them.  Also describe what is dynamically created on each page.}

1. **Home / Create Poll Page (`/`)**:
   - **Transitions:** Serves as the landing page. Submitting the creation form sends a POST request; upon validation, Django creates the poll atomically and redirects directly to that poll's Vote page (`/poll/<id>/`). Clicking any poll title in the recent polls list navigates to its Vote page, and clicking its "results" link navigates directly to its Results page.
   - **Dynamic Content:** Dynamically renders the form with a question input and up to 6 option inputs along with server-side validation error banners. Below the form, it dynamically queries and displays the 10 most recent polls from the database, aggregating total vote counts in real time.

2. **Vote Page (`/poll/<id>/`)**:
   - **Transitions:** Selecting an option and clicking "Vote" sends a POST request that atomically increments the vote count in the database, marks the poll ID in the user's session, and redirects to the Results page (`/poll/<id>/results/`). If the browser session indicates the user has already voted, the voting form is replaced with an informational notice and a direct button to "See results". A "or just see results" link also allows users to view current standings without voting.
   - **Dynamic Content:** Dynamically retrieves the poll question and choice options matching the URL ID from the database. It renders radio buttons for each choice, CSRF token validation, a shareable URL generated using `request.build_absolute_uri()`, and interactive copy-link functionality.

3. **Results Page (`/poll/<id>/results/`)**:
   - **Transitions:** Navigated to automatically after voting or manually via links on the Home and Vote pages. Contains a top navigation brand link to return to Home or start a new poll, and a "Vote in this poll" button if the user has not yet cast a vote.
   - **Dynamic Content:** Dynamically calculates total votes, individual choice vote counts, and percentage shares. It dynamically highlights the leading option and displays the formatted timestamp of the most recent vote. A client-side JavaScript engine (`results.js`) queries the dynamic JSON endpoint (`/poll/<id>/results.json`) every 2.5 seconds, animating CSS bar chart heights and updating numbers in real time without refreshing the page.

# Development Environment

{Describe the tools that you used to develop the software}

- **Operating System & Shell:** Windows 11 with Windows PowerShell
- **Integrated Development Environment (IDE):** Visual Studio Code
- **Version Control:** Git and GitHub for source code repository management
- **Database Systems:** SQLite for local development; Supabase (PostgreSQL 15) with connection pooling for cloud production
- **Deployment & Cloud Hosting:** Vercel serverless platform for web hosting
- **Testing Tools:** Django unit test runner and Google Chrome / Microsoft Edge for multi-browser and incognito session testing

{Describe the programming language that you used and any libraries.}

- **Programming Languages:**
  - Python 3 (3.12 / 3.14): Backend application logic, routing, and database models
  - JavaScript (ES6+): Asynchronous DOM updates, live polling fetch requests, and Web Share API
  - HTML5 & CSS3: Semantic markup, responsive layout, and keyframe animations
- **Libraries and Packages:**
  - Django (v6.1.2): Server-side web framework providing MVT architecture, session management, ORM, and templating
  - psycopg & psycopg-binary (v3.3.6): PostgreSQL adapter for Python
  - dj-database-url (v3.1.2): Database URL configuration parsing
  - python-dotenv (v1.2.4): Environment variable loading from `.env` files
  - WhiteNoise (v6.8.2): Static file serving and compression for WSGI applications
  - sqlparse (v0.6.0): SQL parsing and formatting engine
  - tzdata (v2026.6): Timezone data provider

# Useful Websites

{Make a list of websites that you found helpful in this project}
* [Django Documentation](https://docs.djangoproject.com/)
* [Django Tutorial: Writing your first Django app](https://docs.djangoproject.com/en/stable/intro/tutorial01/)
* [Supabase: Connecting to Postgres](https://supabase.com/docs/guides/database/connecting-to-postgres)
* [MDN Web Docs: Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch)
* [Vercel Documentation: Python Serverless](https://vercel.com/docs/frameworks/backend/python)

# Future Work

{Make a list of things that you need to fix, improve, and add in the future.}
* Item 1: Add user accounts and authentication so users can edit, manage, or close their own polls.
* Item 2: Integrate WebSockets (Django Channels) for instant bidirectional updates instead of periodic polling.
* Item 3: Implement stronger voting restrictions (such as IP-based rate limiting or one-time tokens) beyond browser session tracking.
