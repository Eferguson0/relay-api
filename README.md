# SupaHealth Backend

A modern backend API built with FastAPI, PostgreSQL, and OpenAI integration.

## Features

- FastAPI backend with async support
- PostgreSQL database integration
- OpenAI ChatGPT integration
- JWT-based authentication with bearer tokens (1-day expiration)
- Secure password hashing with bcrypt
- Protected API endpoints
- Docker containerization
- Database migrations with Alembic
- UV package manager for faster dependency installation
- Static file serving for frontend

## Prerequisites

- Docker and Docker Compose installed
- OpenAI API key
- Git (for version control)

## Quick Start

1. Clone the repository:
```bash
git clone <repository-url>
cd SupaHealth-Server
```

2. Set up the Python environment:
```bash
# Create and activate virtual environment
uv venv
source .venv/bin/activate

# Install dependencies
uv pip install -e .
```

3. Create a `.env` file in the project root:
```bash
# Create .env file
touch .env
```

Add the following content to your `.env` file (replace the placeholder values):
```env
# Database Configuration
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/supahealth

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here

# Security
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=11520

# Application Settings
PROJECT_NAME=SupaHealth
VERSION=1.0.0

# CORS Settings (for development)
BACKEND_CORS_ORIGINS=["*"]  # Update with specific origins in production
```

4. Start the application:
```bash
# Build and start the containers
docker compose up --build
```

5. Access the application:
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Database: localhost:5432

### IDE Setup

For the best development experience, configure your IDE to use the virtual environment:

**VS Code/Cursor:**
- Press `Cmd+Shift+P` (Mac) or `Ctrl+Shift+P` (Windows/Linux)
- Type "Python: Select Interpreter"
- Choose `.venv/bin/python` from the list

**PyCharm:**
- Go to Settings > Project > Python Interpreter
- Add Interpreter > Existing Environment
- Browse to `.venv/bin/python`

## Development

### Project Structure
```
.
├── app/
│   ├── core/
│   │   └── config.py
│   ├── db/
│   │   ├── session.py
│   │   └── init_db.py
│   ├── models/
│   ├── schemas/
│   │   └── auth.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── openai_service.py
│   ├── static/
│   ├── templates/
│   └── main.py
├── alembic/
│   └── versions/
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
├── docker-compose.prod.yml
├── Dockerfile
├── pyproject.toml
└── README.md
```

### Package Management with UV

This project uses UV, a new Python package manager that offers significant performance improvements over pip. UV is automatically installed in the Docker container, but you can also use it locally:

```bash
# Install UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies
uv pip install --system -r pyproject.toml

# Add a new dependency
uv pip install package_name
```

### Docker Commands

```bash
# Start the application
docker compose up

# Start in detached mode
docker compose up -d

# View logs for all services
docker compose logs -f

# View logs specifically for the backend app service
docker compose logs -f app

# Stop the application
docker compose down

# Rebuild and start
docker compose up --build

# Remove all data (including database)
docker compose down -v

# For production deployment
docker compose -f docker-compose.prod.yml up --build -d
```

### Database Migrations

The application uses Alembic for database migrations. Migrations are automatically run when the application starts.

#### Local Development (Outside Docker)

For local development, you can run Alembic commands directly:

```bash
# Set the database URL for local development
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/supahealth"

# Create a new migration
uv run alembic revision --autogenerate -m "Description of changes"

# Apply migrations
uv run alembic upgrade head

# Check current migration status
uv run alembic current

# Rollback one migration
uv run alembic downgrade -1

# Rollback to a specific revision
uv run alembic downgrade <revision_id>

# Rollback to base (remove all migrations)
uv run alembic downgrade base
```

#### Docker Environment

```bash
# Create a new migration
docker compose exec app alembic revision --autogenerate -m "Description of changes"

# Apply migrations
docker compose exec app alembic upgrade head

# Check current migration status
docker compose exec app alembic current

# Rollback one migration
docker compose exec app alembic downgrade -1
```

#### Handling Deleted Migration Files

If you delete a migration file and the database still references it, you'll get an error like:
```
ERROR [alembic.util.messaging] Can't locate revision identified by 'abc123def456'
```


**Solution 1: Fresh Database (Deletes All Data)**
```bash
# Stop and remove everything including volumes
docker compose down -v

# Start fresh
docker compose up -d postgres

# Apply migrations
uv run alembic upgrade head
```

**Solution 2: Downgrade to Known Good Revision**
```bash
# Downgrade to the last known good revision
uv run alembic downgrade <known_good_revision_id>

# Then create new migration
uv run alembic revision --autogenerate -m "new_migration"
uv run alembic upgrade head
```

#### Migration Best Practices

1. **Always backup your database** before running migrations in production
2. **Test migrations** on a copy of your production data first
3. **Review generated migrations** before applying them
4. **Use descriptive migration names** that explain what changed
5. **Never delete migration files** that have been applied to production
6. **Keep migrations small and focused** on single changes when possible

#### Common Migration Commands

```bash
# List all migrations
uv run alembic history

# Show migration details
uv run alembic show <revision_id>

# Mark database as up-to-date without running migrations
uv run alembic stamp head

# Create empty migration (no autogenerate)
uv run alembic revision -m "manual_migration"
```

#### Wiping All Migrations and Starting Fresh

Sometimes during development, you may want to wipe all migrations and start with a clean slate. This is useful when:
- You have complex migration conflicts
- You want to clean up migration history
- You've made significant model changes and want a single clean migration

**⚠️ WARNING: This will delete all existing data in your database!**

```bash
# 1. Remove all existing migration files
rm -f alembic/versions/*.py

# 2. Reset the Alembic version table in the database
uv run python -c "
from app.db.session import engine
from sqlalchemy import text

# Drop the alembic_version table to reset migration history
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS alembic_version CASCADE'))
    conn.commit()
    print('Alembic version table dropped successfully')
"

# 3. Drop all existing tables (optional - only if you want to start completely fresh)
uv run python -c "
from app.db.session import engine
from sqlalchemy import text

# Drop all existing tables
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS hourly_heart_rate CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS users CASCADE'))
    conn.commit()
    print('All existing tables dropped successfully')
"

# 4. Create a new initial migration with current model structure
uv run alembic revision --autogenerate -m "Initial migration with email as primary key and composite heart rate key"

# 5. Apply the new initial migration
uv run alembic upgrade head
```

**Alternative: Using Docker Environment**

If you're using Docker, you can also reset everything by:

```bash
# Stop and remove everything including volumes (this deletes all data)
docker compose down -v

# Start fresh
docker compose up -d postgres

# Then follow steps 4-5 above
uv run alembic revision --autogenerate -m "Initial migration"
uv run alembic upgrade head
```

### Troubleshooting

If you encounter any issues:

1. **Port Conflicts**
   - Ensure ports 8000 and 5432 are not in use
   - Modify ports in `docker-compose.yml` if needed

2. **Database Connection Issues**
   - Check if the database container is running: `docker compose ps`
   - View database logs: `docker compose logs postgres`
   - Ensure the database URL in `.env` matches the docker-compose configuration

3. **Application Not Starting**
   - Check application logs: `docker compose logs app`
   - Verify all environment variables are set in `.env`
   - Ensure all dependencies are installed

4. **Reset Everything**
```bash
# Stop all containers and remove volumes
docker compose down -v

# Rebuild and start
docker compose up --build
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication with bearer tokens that expire after 1 day.

### Authentication Endpoints

- `POST /api/auth/signup` - Create a new user account
- `POST /api/auth/signin` - Sign in and get access token
- `GET /api/auth/me` - Get current user profile (requires authentication)
- `POST /api/auth/refresh` - Refresh access token (requires authentication)

### Using Authentication

1. **Sign up** a new user:
```bash
curl -X POST "http://localhost:8000/api/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password",
    "full_name": "Your Name"
  }'
```

2. **Sign in** to get an access token:
```bash
curl -X POST "http://localhost:8000/api/auth/signin" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=your_password"
```

3. **Use the token** for protected endpoints:
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Protected Endpoints

The following endpoints require authentication (Bearer token in Authorization header):
- `GET /api/auth/me` - Get user profile
- `POST /api/auth/refresh` - Refresh token
- `POST /api/ingest-heart-rate` - Ingest heart rate data
- `GET /api/heart-rate` - Get heart rate data
- `POST /api/ingest-diet` - Ingest diet/macro data
- `GET /api/diet` - Get diet records
- `POST /api/diet/record` - Add single diet record
- `DELETE /api/diet/record/{id}` - Delete diet record
- `GET /api/diet/daily/{date}` - Get all records for a specific day
- `GET /api/diet/aggregate` - Get aggregated records by day

### Token Details

- **Expiration**: 1 day (1440 minutes)
- **Algorithm**: HS256
- **Format**: Bearer token in Authorization header
- **Refresh**: Use `/api/auth/refresh` endpoint to get a new token

## Diet & Nutrition Tracking API

The API provides comprehensive endpoints for tracking daily nutrition and macro intake.

### Diet Endpoints

#### Add Single Diet Record
```bash
curl -X POST "http://localhost:8000/api/diet/record" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "datetime": "2024-01-01T08:00:00Z",
    "protein": 25.5,
    "carbs": 45.2,
    "fat": 12.8,
    "calories": 380,
    "meal_name": "Breakfast",
    "notes": "Oatmeal with berries"
  }'
```

#### Get All Diet Records
```bash
curl -X GET "http://localhost:8000/api/diet" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Records for Specific Day
```bash
curl -X GET "http://localhost:8000/api/diet/daily/2024-01-01" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Aggregated Records by Day
```bash
# Get all aggregations
curl -X GET "http://localhost:8000/api/diet/aggregate" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get aggregations for date range
curl -X GET "http://localhost:8000/api/diet/aggregate?start_date=2024-01-01&end_date=2024-01-07" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Delete Diet Record
```bash
curl -X DELETE "http://localhost:8000/api/diet/record/abc123def456" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Bulk Ingest Diet Data
```bash
curl -X POST "http://localhost:8000/api/ingest-diet" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {
        "datetime": "2024-01-01T08:00:00Z",
        "protein": 25.5,
        "carbs": 45.2,
        "fat": 12.8,
        "calories": 380,
        "meal_name": "Breakfast",
        "notes": "Oatmeal with berries"
      },
      {
        "datetime": "2024-01-01T13:00:00Z",
        "protein": 35.0,
        "carbs": 60.0,
        "fat": 20.0,
        "calories": 520,
        "meal_name": "Lunch",
        "notes": "Chicken salad"
      }
    ]
  }'
```

### Diet Data Structure

Each diet record contains:
- **id**: Unique random string identifier (12 characters, auto-generated)
- **user_email**: User identifier (automatically set)
- **datetime**: When the meal was consumed (ISO format)
- **protein**: Protein in grams
- **carbs**: Carbohydrates in grams
- **fat**: Fat in grams
- **calories**: Total calories
- **meal_name**: Name of the meal (e.g., "Breakfast", "Lunch", "Dinner", "Snack")
- **notes**: Additional notes about the meal

### Features

- ✅ **No duplicate restrictions** - Multiple records allowed for same user/date
- ✅ **Daily aggregation** - Get totals for specific days
- ✅ **Date range filtering** - Query records within date ranges
- ✅ **User isolation** - Users can only access their own data
- ✅ **Flexible meal tracking** - Support for any meal names and notes

## Frontend Integration

The backend serves the frontend static files from the `frontend/dist` directory. Make sure to build your frontend application and place the built files in this location before deploying.