# AI Song Domain – Exercise 3

Django domain layer implementation for the AI Song platform.

## Domain Entities

| Entity | Description |
|---|---|
| `Genre` | A music genre (e.g. Pop, Rock, Jazz) |
| `Artist` | A music artist or band, associated with one or more genres |
| `Album` | A collection of songs released by an artist |
| `Song` | A single track, linked to an artist, album, and genre |
| `Playlist` | A user-curated ordered list of songs |
| `PlaylistEntry` | Through-model connecting a Playlist and a Song with an ordering position |

### Relationships

```
Genre  ──< Artist >── (M2M)
Artist ──< Album
Artist ──< Song
Album  ──< Song
Genre  ──< Song
Playlist >──< Song  (via PlaylistEntry)
```

## Requirements

- Python 3.11+
- Django 5.1.7 (installed via `requirements.txt`)

## Local Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd ai-song-domain
```

### 2. Create and activate a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate      # macOS / Linux
venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply database migrations

```bash
python manage.py migrate
```

### 5. (Optional) Create a superuser to access the admin panel

```bash
python manage.py createsuperuser
```

### 6. Run the development server

```bash
python manage.py runserver
```

The application will be available at [http://127.0.0.1:8000](http://127.0.0.1:8000).  
The admin panel is at [http://127.0.0.1:8000/admin](http://127.0.0.1:8000/admin).

## Project Structure

```
ai-song-domain/
├── config/               # Django project settings, URLs, WSGI
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── songs/                # Core domain app
│   ├── migrations/       # Auto-generated database migrations
│   ├── admin.py          # Admin panel configuration
│   ├── apps.py
│   ├── models.py         # Domain entities
│   ├── tests.py
│   └── views.py
├── manage.py
├── requirements.txt
└── README.md
```

## Running Tests

```bash
python manage.py test
```
