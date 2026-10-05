# 🧗 ClimbingGeeks

**A social network for Bulgaria's climbing community.** Climbers can share posts, join clubs and sign up for competitions in one place.

![Python](https://img.shields.io/badge/Python-3.9-3776ab?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2-092e20?style=flat-square&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-database-336791?style=flat-square&logo=postgresql&logoColor=white)
![HTML/CSS/JS](https://img.shields.io/badge/Frontend-HTML%20%C2%B7%20CSS%20%C2%B7%20JS-e34f26?style=flat-square&logo=html5&logoColor=white)

<!-- Add screenshots to docs/screenshots/ and uncomment:
<p align="center">
  <img src="docs/screenshots/home.png" width="48%" alt="Home page" />
  <img src="docs/screenshots/clubs.png" width="48%" alt="Clubs page" />
</p>
-->

## About

I'm a climber myself, and the local scene is spread across club Facebook pages, group chats and posters. ClimbingGeeks puts it in one app: a feed for posts, pages for clubs, and a competition list people can register for.

It started as my final project at SoftUni and my high school diploma project, and it's built with Django using separate apps for each part of the site.

## Features

**Everyone**
- Browse posts, clubs and competitions
- Search and filter content

**Registered members**
- Sign up, log in and keep a personal profile
- Create, edit and delete their own posts
- Join clubs
- Register for competitions

**Staff / administrators**
- Create and manage clubs and competitions
- Moderate posts and manage user accounts through the Django admin

## Tech stack

| Layer | Technology |
|---|---|
| Backend | Python 3.9, Django 4.2 |
| Database | PostgreSQL (`psycopg2`) |
| Frontend | Django templates, HTML, CSS, JavaScript |
| Images | Pillow |
| Config | `python-decouple` (settings read from a `.env` file) |

## Getting started

### Prerequisites
- Python 3.9+
- PostgreSQL running locally

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/KristiyanGorinov/ClimbingGeeks.git
cd ClimbingGeeks

# 2. Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate          # Windows
source venv/bin/activate       # macOS / Linux

# 3. Install dependencies
pip install -r requirements.txt
```

### Database

Create an empty PostgreSQL database:

```sql
CREATE DATABASE climbinggeeks_db;
```

### Environment variables

Copy the example file and fill in your own values:

```bash
cp .env.example .env
```

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key. Generate your own, and never reuse or commit one |
| `DEBUG` | `True` for local development, `False` in production |
| `ALLOWED_HOSTS` | Comma-separated hosts, e.g. `localhost,127.0.0.1` |
| `DB_NAME` | Database name (`climbinggeeks_db`) |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `DB_HOST` | Usually `localhost` |
| `DB_PORT` | Usually `5432` |

To generate a secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key as k; print(k())"
```

### Run it

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

- App: http://localhost:8000
- Admin panel: http://localhost:8000/admin

## Project structure

```
ClimbingGeeks/
├── SoftUniFinalExam/   # Project configuration (settings, urls, wsgi)
├── users/              # Accounts and profiles
├── posts/              # Publications
├── clubs/              # Climbing clubs
├── competitions/       # Competitions
├── registration/       # Competition registration
├── templates/          # HTML templates
├── static/             # CSS, JS, images
├── manage.py
└── requirements.txt
```

## Try it out

| I want to... | How |
|---|---|
| Create an account | Click **Join** |
| Write a post | Go to **Posts** (logged in) |
| Create a club or competition | Log in as a staff user, then use **Clubs** or **Competitions** |
| Moderate content | Log in to `/admin` with your superuser account |

## Roadmap

- [ ] Real-time chat between members
- [ ] Notification system
- [ ] Climber ratings
- [ ] External calendar integration
- [ ] Mobile app

## Author

**Kristiyan Gorinov**, backend developer and climber from Varna, Bulgaria.
[Portfolio](https://kgorinov.com) · [GitHub](https://github.com/KristiyanGorinov)

Originally built under the supervision of Eng. Pavlina Linova at the Professional High School for Computer Modeling and Systems "Acad. Blagovest Sendov", Varna.

## License

Built for educational purposes. All rights reserved by the author unless a license file says otherwise.
