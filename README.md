![CI](https://github.com/<SaintKH>/<python-job-prep-api>/actions/workflows/ci.yml/badge.svg)

# Python Job Prep API

A FastAPI project built to practice backend fundamentals, database integration, and automated testing as part of technical interview preparation.

## Features

- RESTful CRUD API for managing tasks  
- SQLite database using SQLAlchemy ORM  
- Environment-based configuration  
- Automated test suite with pytest  
- Input validation using Pydantic  
- Case-insensitive duplicate title checking  

## Tech Stack

- Python  
- FastAPI  
- SQLAlchemy  
- SQLite  
- Pydantic  
- pytest  

## Setup

1. Clone the repository:

```bash
git clone <your-repo-url>
cd python-job-prep-api
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root:

```
DATABASE_URL=sqlite:///./tasks.db
```

## Running the API

Start the FastAPI server:

```bash
uvicorn main:app --reload
```

Open API documentation:

- Swagger UI: http://127.0.0.1:8000/docs  
- ReDoc: http://127.0.0.1:8000/redoc  

## Running Tests

To run the automated test suite:

```bash
python -m pytest
```

Tests use a temporary test database and do not affect your local data.

## Project Structure

```
python-job-prep-api/
├── app/
│   ├── routers/
│   │   └── tasks.py
│   ├── models.py
│   ├── schemas.py
│   ├── database.py
│   ├── config.py
│   └── main.py
├── tests/
│   ├── conftest.py
│   └── test_tasks.py
├── .env
├── requirements.txt
└── README.md
```

## Future Improvements

- User authentication (JWT)  
- Task ownership per user  
- Database migrations with Alembic  
- Docker deployment  
- CI pipeline for automated testing  
