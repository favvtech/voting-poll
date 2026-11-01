# Live Poll Web App: Project Handoff

## Prompt to paste into a new chat

> Read `LIVE_POLL_PROJECT_HANDOFF.md` in this folder. It holds every decision made so far for my Live Poll web app (BYU CSE 310 Web Apps module). Follow it exactly: build the Django app described here in this folder, test it yourself with little supervision, and only stop for things that truly need me. Don't change the stack or scope without asking.

---

## 1. Context

- **Student project** for a sprint-based course module: **Web Apps**.
- **OS:** Windows, **shell:** PowerShell.
- The student wants something **basic but 100% functional**, buildable in two days or less.
- The agent is expected to **build and test with little human supervision**.

## 2. Final decisions (do not change without asking)

| Topic | Decision |
|---|---|
| App | **Live Poll** web app |
| Framework | **Django (Python)** |
| Database | **SQLite** (Django default) through Django models |
| Hosting | **Local only**, using `python manage.py runserver`. No deployment. |
| Real-time updates | **JavaScript polling** of a Django JSON view every 2 to 3 seconds. No WebSockets or Django Channels. |
| Firebase / Vercel / Vite | **Dropped.** They were in an earlier plan, before the module requirements changed. |

### Why these choices
- The module needs a framework that **generates pages on the server**. Django is the framework the course recommends.
- Django with SQLite covers **both** optional requirements: a database and a third dynamic page.
- Running locally means no accounts or keys are needed, so the agent can build and test everything on its own.
- Polling is simple, reliable, and works the same anywhere. Live updates still work locally across multiple tabs and browsers.

## 3. Module requirements (from the assignment)

Write a web app using Django, Node, React, or ASP.NET. It must demonstrate:

**All basic requirements:**
1. At least **two HTML pages** filled with content decided by the Python (Django) code.
2. **Interactive:** the content shown must be based in part on user input.
3. Runs on the **local computer** using the framework's **test server**.

**At least one additional requirement** (this project meets both):
- Integrate a **database**.
- Add a **third dynamically generated page**.

**Also:** use the **Web App README.md template** (see section 9).

## 4. Features (scope is locked to these)

1. **Create poll:** a question plus 2 to 6 options.
2. **Collect votes:** anyone with the link can vote once.
3. **Live results:** counts and percentage bars that update automatically, without reloading the page.
4. **Shareable link:** a "Copy link" button on the poll page.

**Needed for real use:**
- **Validation:** the question can't be empty, there must be at least 2 non-empty options, and options can't repeat.
- **One vote per browser per poll,** tracked with **Django sessions**.
- **Safe vote counting** with `F("votes") + 1` and `update()`, so votes made at the same moment are all counted.
- Friendly error messages and a 404 page for polls that don't exist.
- CSRF protection on every form (Django's default).
- A basic responsive layout that works on mobile.

**Out of scope:** user accounts, editing polls, deployment, WebSockets.

## 5. Architecture

### Project layout (target)
```
live_poll/                 # project root (this folder)
├── manage.py
├── requirements.txt       # Django
├── README.md              # filled-in Web App README template
├── .gitignore             # venv/, db.sqlite3, __pycache__/, *.pyc
├── livepoll/              # Django project (settings, root urls)
└── polls/                 # Django app
    ├── models.py
    ├── views.py
    ├── urls.py
    ├── forms.py
    ├── admin.py
    ├── tests.py
    ├── templates/polls/
    │   ├── base.html
    │   ├── home.html
    │   ├── vote.html
    │   └── results.html
    └── static/polls/
        ├── styles.css
        └── results.js
```

### Models
- `Poll`: `question` (CharField, max 200), `created_at` (DateTimeField, auto_now_add)
- `Choice`: `poll` (ForeignKey to Poll, related_name="choices", on_delete CASCADE), `text` (CharField, max 100), `votes` (PositiveIntegerField, default 0)

### Pages and routes
| URL | View | Type | Purpose |
|---|---|---|---|
| `/` | `home` | HTML (GET/POST) | **Page 1:** form to create a poll, plus a list of recent polls from the database. A successful POST redirects to the vote page. |
| `/poll/<int:poll_id>/` | `vote` | HTML (GET/POST) | **Page 2:** shows the question, options, and a "Copy link" button. POST records the vote, then redirects to the results page. If the browser already voted, show a message and a link to results. |
| `/poll/<int:poll_id>/results/` | `results` | HTML (GET) | **Page 3:** counts, percentages, and bars calculated in the view. Includes `results.js`. |
| `/poll/<int:poll_id>/results.json` | `results_json` | JSON (GET) | Returns `{question, total, choices:[{id,text,votes,percent}]}` for live polling. |

### Live results
`results.js` uses `fetch` to request `results.json` every 2 to 3 seconds and updates the counts, percentages, and bar widths in place. It also shows a small "Live" indicator and keeps retrying quietly if a request fails.

### One vote per browser
Store voted poll IDs in `request.session["voted_polls"]` (a list). Check it before recording a vote.

## 6. Build plan for the agent

1. Create a virtual environment: `python -m venv venv`, then `.\venv\Scripts\Activate.ps1`.
2. `pip install Django`, then `pip freeze > requirements.txt`.
3. `django-admin startproject livepoll .`, then `python manage.py startapp polls`.
4. Register `polls` in `INSTALLED_APPS`, include `polls.urls` in the root URLs.
5. Write the models, then run `makemigrations` and `migrate`. Register the models in the admin.
6. Write a form or validation for creating polls (question plus a dynamic list of options).
7. Write the views, URLs, templates, CSS, and `results.js`.
8. Write `tests.py` covering: create poll (valid and invalid), vote, blocking a second vote, results JSON numbers, and 404 for a missing poll.
9. Run `python manage.py test`, then `python manage.py runserver`.
10. Test in the browser: create a poll, vote from two different browser sessions (normal and private/incognito), and confirm results update live in another tab.
11. Fill in the README template (section 9).
12. Add `.gitignore`. Initialize git if the student wants it.

**Stop and ask the student only for:** the official README template, if it differs from section 9, and the YouTube demo video link.

## 7. Assignment answers (final; already submitted or ready to submit)

### Q2. High-level description and how each requirement is met

I plan to build a **Live Poll web app** using **Django (Python)** with a **SQLite database**. A user creates a poll with a question and several answer options. The app then gives them a shareable link to send to others. People who open the link can vote, and the results page shows vote counts and percentage bars that update automatically as new votes come in. Every page is generated on the server: Django view functions in `views.py` read the database, prepare the data, and fill in HTML templates before sending them to the browser.

- **Uses a web app framework:** The app is built with Django. Each URL is connected to a Python function in `views.py` that handles the request and returns a page built from a template.
- **At least two dynamically generated HTML pages:** The app has three pages, all built by Python code:
  1. **Home / Create Poll page** (`/`): shows a form for creating a poll and a list of recent polls pulled from the database.
  2. **Vote page** (`/poll/<id>/`): shows the question and options for the poll matching the ID in the URL.
  3. **Results page** (`/poll/<id>/results/`): shows each option's vote count and percentage, which the view function calculates from the database.
- **Interactive, with content based on user input:** Everything on the site comes from what users enter. The polls people create decide which questions and options appear, and the votes people cast decide the results. Django processes the form data (POST requests) in the view functions.
- **Runs locally on the framework's test server:** The app runs on my computer with `python manage.py runserver` and is viewed in a web browser.
- **Additional requirement, database:** Django models (`Poll` and `Choice`) store polls, options, and vote counts in SQLite. Votes are added using Django's `F()` expressions, so votes made at the same moment are all counted correctly.
- **Additional requirement, third dynamic page:** The Results page is the third dynamically generated page.
- **Live results:** The results page runs a small JavaScript script that requests the latest counts from a Django view every few seconds and updates the bars without reloading the page.
- **Shareable link:** The vote page has a "Copy link" button so the poll's URL can be shared with others.
- **One vote per person:** Django sessions remember whether a browser has already voted in a poll, so it can't vote twice.
- **README:** The project will include the Web App README.md template, filled in with a description, setup instructions, and a link to the demo video.

### Q3. Schedule (20 hours total, 10 per week)

| Day | First Week of Sprint | Second Week of Sprint |
|---|---|---|
| **Monday** | Read the Django documentation and complete the first parts of the official tutorial (2 hrs) | Build the live results update: a Django view that returns the latest counts, plus JavaScript that refreshes the bars (2 hrs) |
| **Tuesday** | Install Django, create the project and app, and run the test server (1.5 hrs) | Add one vote per browser using sessions, form validation, and error messages (1.5 hrs) |
| **Wednesday** | Create the `Poll` and `Choice` database models and run migrations; test them in the Django admin (1.5 hrs) | Add the shareable link with the "Copy link" button and styling with CSS (2 hrs) |
| **Thursday** | Build the Home / Create Poll page with a form that saves polls to the database (2 hrs) | Test the full app in several browsers at the same time; fix bugs (1.5 hrs) |
| **Friday** | Build the Vote page that reads the poll from the database and records votes (2 hrs) | Fill in the README.md template and clean up the code (1.5 hrs) |
| **Saturday** | Build a basic Results page; test the first week's work (1 hr) | Record the demo video, push the final code to GitHub, and submit (1.5 hrs) |
| **Total** | **10 hours** | **10 hours** |

### Q4. Risks and action plans

**Risk 1: Being new to Django, especially URLs, views, templates, and models.**
Action plan: I will go through the official Django tutorial in the first week before building my own features, because it teaches the same pieces my app needs. I will build and test one page at a time instead of everything at once. If I'm stuck for more than 30 minutes, I will check the documentation, ask a classmate or the instructor, or use AI to explain the error, and then confirm the answer is correct by testing it.

**Risk 2: Not having enough time because of work, school, or family responsibilities.**
Action plan: I will set fixed time blocks on my calendar for each day in the schedule. I will finish the required features in the first week: two dynamic pages, user input, and the database. That way, if I fall behind, the app still meets the requirements and only extras like live updates and styling would be affected.

**Risk 3: The live results updates being harder than expected.**
Action plan: I will build a plain Results page first that shows the current counts when the page loads, which already meets the requirements. Then I will add the automatic updates on top. If they cause problems, a "Refresh results" button will work as a backup.

## 8. Definition of done

- [ ] `python manage.py runserver` starts with no errors, and all three pages load.
- [ ] A poll can be created. Invalid input shows clear errors.
- [ ] Voting works, and a second vote from the same browser is blocked.
- [ ] Results update live in another tab or browser within about 3 seconds.
- [ ] "Copy link" copies the vote page URL.
- [ ] A missing poll ID shows a 404.
- [ ] `python manage.py test` passes.
- [ ] README is filled in. `.gitignore` excludes `venv/` and `db.sqlite3`.

## 9. README template (BYU CSE 310 Web App style; confirm with the student)

```markdown
# Overview

{Describe your purpose for writing this software, and what it does.}

{Describe how to start the test server and open the first page of the web app.}

[Software Demo Video](http://youtube.link.goes.here)

# Web Pages

{Describe each of the web pages you created and how the web app moves between them. Describe what is created dynamically on each page.}

# Development Environment

{Describe the tools that you used to develop the software.}

{Describe the programming language and libraries that you used for the software.}

# Useful Websites

- [Django Documentation](https://docs.djangoproject.com/)
- [Web Site Name](http://url.link.goes.here)

# Future Work

- {Item 1}
- {Item 2}
```

## 10. History (for reference only)

1. Started with a list of quick web app ideas. The student chose **Live Poll**.
2. First plan: Vite with plain JavaScript, Firebase Firestore, and Vercel hosting.
3. The module requirements arrived (server-generated pages with a framework), so the plan **switched to Django with SQLite**.
4. Deployment to PythonAnywhere was considered, but the student chose to **keep it local**.
