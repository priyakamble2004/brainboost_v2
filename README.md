# 🧠 Brain Boost V2 — Backend

Flask + MySQL backend for the Brain Boost V2 quiz application.

---

## Quick Start

```bash
# 1 — Create the MySQL database
mysql -u root -p
CREATE DATABASE brainboost_v2 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit

# 2 — Copy and fill in env variables
cp .env.example .env
# Edit .env — set MYSQL_PASSWORD to your root password

# 3 — Create virtual environment and install packages
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt

# 4 — Place the frontend file in this folder
#     brain-boost-v2-connected.html

# 5 — Start the server
python app.py
```

Open **http://localhost:5000** in your browser.  
On first run the server auto-creates all tables and seeds **350 questions** across 7 sections.

---

## Project Structure

```
brainboost_v2/
├── app.py                          ← Flask entry point
├── config.py                       ← DB + JWT configuration
├── database.py                     ← SQLAlchemy instance
├── models.py                       ← All database models
├── seed.py                         ← 350 questions auto-seeded on first run
├── requirements.txt                ← Python packages
├── .env.example                    ← Env variable template
├── brain-boost-v2-connected.html   ← Frontend (place here after download)
├── routes/
│   ├── auth.py                     ← Register / Login / JWT
│   ├── sections.py                 ← Sections + image upload
│   ├── questions.py                ← Questions CRUD
│   ├── quiz.py                     ← Quiz submit + progress
│   ├── psychometric.py             ← Psychometric test
│   └── leaderboard.py              ← Global + section leaderboards
├── uploads/                        ← Section images (auto-created)
└── static/                         ← Reserved for static files
```

---

## API Reference

All endpoints are prefixed with `/api`.  
Protected routes require: `Authorization: Bearer <token>`

### Auth — `/api/auth`

| Method | Endpoint    | Auth | Body / Params                          | Returns          |
|--------|-------------|------|----------------------------------------|------------------|
| POST   | /register   | —    | `{username, password, email?}`         | `{token, user}`  |
| POST   | /login      | —    | `{username, password}`                 | `{token, user}`  |
| GET    | /me         | ✅   | —                                      | `{user}`         |
| POST   | /logout     | ✅   | —                                      | `{message}`      |

### Sections — `/api/sections`

| Method | Endpoint            | Auth | Description                   |
|--------|---------------------|------|-------------------------------|
| GET    | /                   | —    | All sections with levels      |
| GET    | /<id>               | —    | Single section                |
| GET    | /<id>/image         | —    | Serve section image           |
| POST   | /<id>/image         | ✅   | Upload section image (form)   |

### Questions — `/api/questions`

| Method | Endpoint         | Auth | Description                              |
|--------|------------------|------|------------------------------------------|
| GET    | /level/<id>      | ✅   | 10 random questions (no correct answers) |
| POST   | /                | ✅   | Add single question                      |
| POST   | /bulk            | ✅   | Add many questions                       |
| PUT    | /<id>            | ✅   | Update a question                        |
| DELETE | /<id>            | ✅   | Delete a question                        |

### Quiz — `/api/quiz`

| Method | Endpoint                    | Auth | Description                        |
|--------|-----------------------------|------|------------------------------------|
| POST   | /submit                     | ✅   | Submit quiz, validate, save result |
| GET    | /progress                   | ✅   | All level progress for user        |
| GET    | /progress/section/<id>      | ✅   | Progress + unlock status           |
| GET    | /history/level/<id>         | ✅   | Last 10 attempts for a level       |

**Submit body:**
```json
{
  "level_id": 1,
  "time_taken": 120,
  "answers": [
    { "question_id": 5, "selected_option": 2, "time_taken": 8 },
    ...
  ]
}
```

**Submit response:**
```json
{
  "score": 8,
  "stars": 4,
  "is_perfect": false,
  "next_level_unlocked": false,
  "message": "🌟 So close! ...",
  "correct_map": {
    "5": { "is_correct": true,  "correct_option": 2 },
    "6": { "is_correct": false, "correct_option": 0 }
  }
}
```

### Psychometric — `/api/psychometric`

| Method | Endpoint   | Auth | Description                        |
|--------|------------|------|------------------------------------|
| POST   | /submit    | ✅   | Save scores, get career profile    |
| GET    | /history   | ✅   | Last 5 results                     |
| GET    | /latest    | ✅   | Most recent result + profile       |

### Leaderboard — `/api/leaderboard`

| Method | Endpoint          | Auth | Description           |
|--------|-------------------|------|-----------------------|
| GET    | /global           | —    | Top 20 all sections   |
| GET    | /section/<id>     | —    | Top 20 one section    |

---

## Level Locking Rules

- **Level 1**: Always unlocked
- **Levels 2–5**: Require the previous level to have `is_perfect = True` (score 10/10)
- The `is_perfect` flag in `level_progress` never goes back to False once set
- Lock status is computed server-side in `/api/quiz/progress/section/<id>`

---

## Database Models

| Table                  | Purpose                                   |
|------------------------|-------------------------------------------|
| `users`                | Registered players                        |
| `sections`             | Quiz categories (IKS, Computer, etc.)     |
| `levels`               | 5 levels per section (Beginner → Expert)  |
| `questions`            | 10 questions per level (350 total)        |
| `quiz_attempts`        | Every quiz play session                   |
| `attempt_answers`      | Per-question answer for each attempt      |
| `level_progress`       | Best score, stars, perfect flag per level |
| `psychometric_results` | Career test results                       |

---

## Sections & Questions

| Section        | Icon | Questions |
|----------------|------|-----------|
| IKS            | 📜   | 50        |
| Computer       | 💻   | 50        |
| English        | 📖   | 50        |
| Environment    | 🌿   | 50        |
| Indian Culture | 🪔   | 50        |
| Sports         | ⚽   | 50        |
| Sociopolitical | 🏛️   | 50        |
| **Total**      |      | **350**   |
