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
- **RID-based resource identification** (Resource IDs with format `type..randomstring`)
- **Comprehensive linting** with ruff, black, and isort
- **Health tracking APIs** for heart rate, diet, weight, and goals

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
│   ├── api/                    # API route handlers
│   │   ├── auth.py            # Authentication endpoints
│   │   ├── chat.py            # OpenAI chat endpoints
│   │   ├── diet.py            # Diet/nutrition tracking
│   │   ├── goals.py           # User goals management
│   │   ├── heart_rate.py      # Heart rate data ingestion
│   │   ├── system.py          # System health endpoints
│   │   └── weight.py          # Weight tracking
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   └── rid.py             # RID (Resource ID) utilities
│   ├── db/
│   │   ├── session.py         # Database session management
│   │   └── init_db.py         # Database initialization
│   ├── models/                # SQLAlchemy database models
│   │   ├── diet.py            # Diet/nutrition model
│   │   ├── goals.py           # Goals models
│   │   ├── heart_rate.py      # Heart rate model
│   │   ├── models.py          # Model imports
│   │   ├── user.py            # User model
│   │   └── weight.py          # Weight model
│   ├── schemas/               # Pydantic data schemas
│   │   ├── diet.py            # Diet schemas
│   │   ├── goals.py           # Goals schemas
│   │   ├── heart_rate.py      # Heart rate schemas
│   │   ├── user.py            # User schemas
│   │   └── weight.py          # Weight schemas
│   ├── services/              # Business logic services
│   │   ├── auth_service.py    # Authentication service
│   │   └── openai_service.py  # OpenAI integration
│   └── main.py                # FastAPI application entry point
├── scripts/                   # Utility scripts
│   ├── lint.py               # Linting script
│   └── reset_db.py           # Database reset script
├── alembic/                   # Database migrations
│   └── versions/
├── .env
├── .gitignore
├── alembic.ini
├── docker-compose.yml
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
uv sync

# Add a new dependency
uv add package_name
```

### Development Commands

The project includes several convenient `uv` commands for development:

```bash
# Database management
uv run reset-db              # Wipe database and create fresh migration

# Code quality
uv run lint                  # Check code quality (isort, black, ruff)
uv run lint-fix              # Auto-fix code quality issues

# Database migrations
uv run alembic revision --autogenerate -m "Description"
uv run alembic upgrade head
uv run alembic current
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


**Fresh Database (Deletes All Data)**
```bash
# Stop and remove everything including volumes
docker compose down -v

# Start fresh
docker compose up -d postgres

# Apply migrations
uv run alembic upgrade head
```

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

**Easy Method (Recommended):**
```bash
# Use the built-in reset command
uv run reset-db
```

This command will:
1. Drop all existing tables
2. Remove all migration files
3. Create a fresh initial migration
4. Apply the migration
5. Create initial admin and test users

**Manual Method:**
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

# 3. Drop all existing tables
uv run python -c "
from app.db.session import engine
from sqlalchemy import text

# Drop all existing tables
with engine.connect() as conn:
    conn.execute(text('DROP TABLE IF EXISTS hourly_heart_rate CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS diet CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS weight CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS goal_weight CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS goal_daily_diet CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS goal_message CASCADE'))
    conn.execute(text('DROP TABLE IF EXISTS users CASCADE'))
    conn.commit()
    print('All existing tables dropped successfully')
"

# 4. Create a new initial migration with current model structure
uv run alembic revision --autogenerate -m "Initial migration with RID-based IDs"

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

## Resource Identification (RID) System

The API uses RIDs (Resource IDs) for all resource identification instead of auto-incrementing integers. This provides better scalability and security.

### RID Format
- **Format**: `<type>..<random-string>`
- **Examples**: 
  - User: `user..test123456`
  - Diet: `diet..m8ssli7xr41u`
  - Weight: `weight..kw3cgkg7f08g`

### Benefits
- **No sequential IDs** - Prevents enumeration attacks
- **Type identification** - Easy to identify resource type from ID
- **Distributed-friendly** - No coordination needed for ID generation
- **URL-safe** - Can be used directly in URLs and APIs

### RID Generation
RIDs are automatically generated using the `generate_rid()` function:
```python
from app.core.rid import generate_rid

user_id = generate_rid("auth", "user")      # auth..user.abc123def456
diet_id = generate_rid("nutrition", "macros")  # nutrition..macros.xyz789ghi012
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

**Authentication:**
- `GET /api/auth/me` - Get user profile
- `POST /api/auth/refresh` - Refresh token

**Heart Rate:**
- `POST /api/ingest-heart-rate` - Ingest heart rate data
- `GET /api/heart-rate` - Get heart rate data

**Diet & Nutrition:**
- `POST /api/ingest-diet` - Ingest diet/macro data
- `GET /api/diet` - Get all diet records
- `POST /api/diet/record` - Add single diet record
- `DELETE /api/diet/record/{id}` - Delete diet record
- `GET /api/diet/daily/{date}` - Get all records for a specific day
- `GET /api/diet/aggregate` - Get aggregated records by day

**Weight Tracking:**
- `POST /api/weight` - Add weight measurement
- `GET /api/weight` - Get all weight records
- `PUT /api/weight/{id}` - Update weight record
- `DELETE /api/weight/{id}` - Delete weight record

**Goals:**
- `POST /api/goals/weight` - Create weight goal
- `GET /api/goals/weight` - Get weight goal
- `PUT /api/goals/weight` - Update weight goal
- `DELETE /api/goals/weight` - Delete weight goal

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
- **id**: RID identifier (format: `diet..<random-string>`)
- **user_id**: User RID identifier (format: `user..<random-string>`)
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

## Weight Tracking API

The API provides endpoints for tracking weight measurements and body composition.

### Weight Endpoints

#### Add Weight Measurement
```bash
curl -X POST "http://localhost:8000/api/weight" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 70.5,
    "body_fat_percentage": 15.2,
    "muscle_mass_percentage": 45.8,
    "notes": "Morning weight measurement"
  }'
```

#### Get All Weight Records
```bash
curl -X GET "http://localhost:8000/api/weight" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update Weight Record
```bash
curl -X PUT "http://localhost:8000/api/weight/weight..abc123def456" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 70.0,
    "notes": "Updated measurement"
  }'
```

#### Delete Weight Record
```bash
curl -X DELETE "http://localhost:8000/api/weight/weight..abc123def456" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Weight Data Structure

Each weight record contains:
- **id**: RID identifier (format: `weight..<random-string>`)
- **user_id**: User RID identifier (format: `user..<random-string>`)
- **weight**: Weight measurement in kg or lbs
- **body_fat_percentage**: Body fat percentage (0-100)
- **muscle_mass_percentage**: Muscle mass percentage (0-100)
- **notes**: Additional notes about the measurement
- **created_at**: Timestamp when record was created
- **updated_at**: Timestamp when record was last updated

## Goals API

The API provides endpoints for managing user goals (weight, diet, and motivational messages).

### Goals Endpoints

#### Create Weight Goal
```bash
curl -X POST "http://localhost:8000/api/goals/weight" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 65.0,
    "body_fat_percentage": 12.0,
    "muscle_mass_percentage": 48.0
  }'
```

#### Get Weight Goal
```bash
curl -X GET "http://localhost:8000/api/goals/weight" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update Weight Goal
```bash
curl -X PUT "http://localhost:8000/api/goals/weight" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 63.0,
    "body_fat_percentage": 10.0
  }'
```

#### Delete Weight Goal
```bash
curl -X DELETE "http://localhost:8000/api/goals/weight" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Goals Data Structure

**Weight Goals:**
- **user_id**: User RID identifier (format: `user..<random-string>`) - Primary key
- **weight**: Target weight in kg or lbs
- **body_fat_percentage**: Target body fat percentage
- **muscle_mass_percentage**: Target muscle mass percentage
- **created_at**: Timestamp when goal was created
- **updated_at**: Timestamp when goal was last updated

## Frontend Integration

The backend serves the frontend static files from the `frontend/dist` directory. Make sure to build your frontend application and place the built files in this location before deploying.