# Dynamic Reports Builder

A powerful dynamic reporting system built with FastAPI, SQL Server, and modern UI components.

## Features

- Dynamic report generation
- Multiple chart types support
- SQL query generation and execution
- Report workflow management
- Measurement definitions
- Export functionality

## Tech Stack

- Backend: FastAPI (Python)
- Database: SQL Server
- ORM: SQLAlchemy
- Frontend: React (coming soon)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure database connection in `app/core/database.py`

3. Run the application:
```bash
uvicorn app.main:app --reload
```

## API Documentation

Once the application is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
/app
  /api
    /v1
      /reports
      /charts
      /sessions
      /workflows
      /measurements
  /core
    /config
    /database
    /models
    /schemas
  /services
    /report_generator
    /chart_generator
    /sql_generator
```

## License

MIT 