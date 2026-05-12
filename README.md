# UniSchedule AI

UniSchedule AI is a Flask web application for managing university timetables with a student-facing AI assistant.

## Setup on Windows

Create a virtual environment:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, run:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

Then activate the virtual environment again.

## Install Dependencies

```powershell
pip install -r requirements.txt
```

## Environment File

Copy the example environment file:

```powershell
copy .env.example .env
```

Edit `.env` if needed. If `GEMINI_API_KEY` is not set, the AI assistant will return a helpful fallback message instead of calling Gemini.

## Seed the Database

This resets the SQLite database and loads demo data:

```powershell
python seed.py
```

Demo logins:

- Admin: `admin` / `admin123`
- Student: `student` / `student123`

## Run the App

```powershell
python app.py
```

Open the local URL shown in the terminal, usually:

```text
http://127.0.0.1:5000
```
