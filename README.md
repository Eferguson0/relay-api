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
│   │   └── v1/                # API version 1
│   │       ├── auth/          # Authentication endpoints
│   │       │   ├── login.py   # Login endpoints
│   │       │   └── user.py    # User management
│   │       ├── chat/          # OpenAI chat endpoints
│   │       ├── goal/          # User goals management
│   │       │   ├── general.py # General goals
│   │       │   ├── macros.py  # Macro goals
│   │       │   └── weight.py  # Weight goals
│   │       ├── metric/        # Health metrics
│   │       │   ├── activity/  # Activity metrics
│   │       │   │   ├── miles.py    # Miles tracking
│   │       │   │   ├── steps.py    # Steps tracking
│   │       │   │   └── workouts.py # Workout tracking
│   │       │   ├── body/      # Body composition
│   │       │   │   ├── composition.py # Body composition
│   │       │   │   └── heartrate.py   # Heart rate tracking
│   │       │   ├── calories/  # Calorie tracking
│   │       │   │   ├── active.py     # Active calories
│   │       │   │   └── baseline.py   # Baseline calories
│   │       │   └── sleep/     # Sleep tracking
│   │       │       └── daily.py     # Daily sleep data
│   │       ├── nutrition/     # Nutrition tracking
│   │       │   └── macros.py  # Macro nutrition
│   │       └── system/        # System health endpoints
│   ├── core/
│   │   ├── config.py          # Application configuration
│   │   └── rid.py             # RID (Resource ID) utilities
│   ├── db/
│   │   ├── session.py         # Database session management
│   │   └── init_db.py         # Database initialization
│   ├── models/                # SQLAlchemy database models
│   │   ├── auth/              # Authentication models
│   │   │   └── user.py        # AuthUser model
│   │   ├── goal/              # Goal models
│   │   │   ├── general.py     # General goals
│   │   │   ├── macros.py      # Macro goals
│   │   │   └── weight.py      # Weight goals
│   │   ├── metric/            # Health metric models
│   │   │   ├── activity/      # Activity models
│   │   │   │   ├── miles.py       # ActivityMiles
│   │   │   │   ├── steps.py       # ActivitySteps
│   │   │   │   └── workouts.py    # ActivityWorkouts
│   │   │   ├── body/          # Body composition models
│   │   │   │   ├── composition.py # BodyComposition
│   │   │   │   └── heartrate.py   # BodyHeartRate
│   │   │   ├── calories/      # Calorie models
│   │   │   │   ├── active.py      # CaloriesActive
│   │   │   │   └── baseline.py    # CaloriesBaseline
│   │   │   └── sleep/         # Sleep models
│   │   │       └── daily.py       # SleepDaily
│   │   ├── nutrition/         # Nutrition models
│   │   │   └── macros.py      # NutritionMacros
│   │   ├── enums.py           # Data source enums
│   │   └── __init__.py        # Model imports
│   ├── schemas/               # Pydantic data schemas
│   │   ├── auth/              # Authentication schemas
│   │   │   └── user.py        # User schemas
│   │   ├── goal/              # Goal schemas
│   │   │   ├── general.py     # General goal schemas
│   │   │   ├── macros.py      # Macro goal schemas
│   │   │   └── weight.py      # Weight goal schemas
│   │   ├── metric/            # Health metric schemas
│   │   │   ├── activity/      # Activity schemas
│   │   │   ├── body/          # Body composition schemas
│   │   │   ├── calories/      # Calorie schemas
│   │   │   └── sleep/         # Sleep schemas
│   │   ├── nutrition/         # Nutrition schemas
│   │   │   └── macros.py      # Macro nutrition schemas
│   │   └── __init__.py        # Schema imports
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

user_id = generate_rid("auth", "user")           # auth..user.abc123def456
nutrition_id = generate_rid("nutrition", "macros")  # nutrition..macros.xyz789ghi012
activity_id = generate_rid("metric", "activity")    # metric..activity.def456ghi789
goal_id = generate_rid("goal", "weight")            # goal..weight.jkl012mno345
```

## Authentication

The API uses JWT (JSON Web Tokens) for authentication with bearer tokens that expire after 1 day.

### Authentication Endpoints

- `POST /api/v1/auth/signup` - Create a new user account
- `POST /api/v1/auth/signin` - Sign in and get access token
- `GET /api/v1/auth/me` - Get current user profile (requires authentication)
- `POST /api/v1/auth/refresh` - Refresh access token (requires authentication)

### Using Authentication

1. **Sign up** a new user:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "your_password",
    "full_name": "Your Name"
  }'
```

2. **Sign in** to get an access token:
```bash
curl -X POST "http://localhost:8000/api/v1/auth/signin" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=user@example.com&password=your_password"
```

3. **Use the token** for protected endpoints:
```bash
curl -X GET "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Protected Endpoints

The following endpoints require authentication (Bearer token in Authorization header):

**Authentication:**
- `GET /api/v1/auth/me` - Get user profile
- `POST /api/v1/auth/refresh` - Refresh token

**Activity Metrics:**
- `GET /api/v1/metric/activity/steps` - Get steps data
- `POST /api/v1/metric/activity/steps` - Ingest steps data
- `GET /api/v1/metric/activity/miles` - Get miles data
- `POST /api/v1/metric/activity/miles` - Ingest miles data
- `GET /api/v1/metric/activity/workouts` - Get workout data
- `POST /api/v1/metric/activity/workouts` - Ingest workout data

**Body Metrics:**
- `GET /api/v1/metric/body/heartrate` - Get heart rate data
- `POST /api/v1/metric/body/heartrate` - Ingest heart rate data
- `GET /api/v1/metric/body/composition` - Get body composition data
- `POST /api/v1/metric/body/composition` - Ingest body composition data

**Calorie Metrics:**
- `GET /api/v1/metric/calories/active` - Get active calories data
- `POST /api/v1/metric/calories/active` - Ingest active calories data
- `GET /api/v1/metric/calories/baseline` - Get baseline calories data
- `POST /api/v1/metric/calories/baseline` - Ingest baseline calories data

**Sleep Metrics:**
- `GET /api/v1/metric/sleep/daily` - Get sleep data
- `POST /api/v1/metric/sleep/daily` - Ingest sleep data

**Nutrition:**
- `GET /api/v1/nutrition/macros` - Get nutrition macro data
- `POST /api/v1/nutrition/macros` - Ingest nutrition macro data

**Goals:**
- `GET /api/v1/goal/weight` - Get weight goals
- `POST /api/v1/goal/weight` - Create weight goal
- `PUT /api/v1/goal/weight/{id}` - Update weight goal
- `DELETE /api/v1/goal/weight/{id}` - Delete weight goal
- `GET /api/v1/goal/macros` - Get macro goals
- `POST /api/v1/goal/macros` - Create macro goal
- `GET /api/v1/goal/general` - Get general goals
- `POST /api/v1/goal/general` - Create general goal

### Token Details

- **Expiration**: 1 day (1440 minutes)
- **Algorithm**: HS256
- **Format**: Bearer token in Authorization header
- **Refresh**: Use `/api/v1/auth/refresh` endpoint to get a new token

## Nutrition & Macro Tracking API

The API provides comprehensive endpoints for tracking daily nutrition and macro intake.

### Nutrition Endpoints

#### Add Single Nutrition Record
```bash
curl -X POST "http://localhost:8000/api/v1/nutrition/macros/record" \
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

#### Get All Nutrition Records
```bash
curl -X GET "http://localhost:8000/api/v1/nutrition/macros" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Records for Specific Day
```bash
curl -X GET "http://localhost:8000/api/v1/nutrition/macros/daily/2024-01-01" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Get Aggregated Records by Day
```bash
# Get all aggregations
curl -X GET "http://localhost:8000/api/v1/nutrition/macros/aggregate" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"

# Get aggregations for date range
curl -X GET "http://localhost:8000/api/v1/nutrition/macros/aggregate?start_date=2024-01-01&end_date=2024-01-07" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Delete Nutrition Record
```bash
curl -X DELETE "http://localhost:8000/api/v1/nutrition/macros/record/nutrition..abc123def456" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Bulk Ingest Nutrition Data
```bash
curl -X POST "http://localhost:8000/api/v1/nutrition/macros" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "record": {
      "data": {
        "metrics": [
          {
            "name": "nutrition_macros",
            "data": [
              {
                "date": "2024-01-01T08:00:00Z",
                "protein": 25.5,
                "carbs": 45.2,
                "fat": 12.8,
                "calories": 380,
                "meal_name": "Breakfast",
                "notes": "Oatmeal with berries",
                "source": "manual"
              },
              {
                "date": "2024-01-01T13:00:00Z",
                "protein": 35.0,
                "carbs": 60.0,
                "fat": 20.0,
                "calories": 520,
                "meal_name": "Lunch",
                "notes": "Chicken salad",
                "source": "manual"
              }
            ]
          }
        ]
      }
    }
  }'
```

### Nutrition Data Structure

Each nutrition record contains:
- **id**: RID identifier (format: `nutrition..<random-string>`)
- **user_id**: User RID identifier (format: `auth..user.<random-string>`)
- **datetime**: When the meal was consumed (ISO format)
- **protein**: Protein in grams
- **carbs**: Carbohydrates in grams
- **fat**: Fat in grams
- **calories**: Total calories
- **meal_name**: Name of the meal (e.g., "Breakfast", "Lunch", "Dinner", "Snack")
- **notes**: Additional notes about the meal
- **source**: Data source (e.g., "manual", "apple_watch", "fitbit")

### Features

- ✅ **No duplicate restrictions** - Multiple records allowed for same user/date
- ✅ **Daily aggregation** - Get totals for specific days
- ✅ **Date range filtering** - Query records within date ranges
- ✅ **User isolation** - Users can only access their own data
- ✅ **Flexible meal tracking** - Support for any meal names and notes

## Body Composition Tracking API

The API provides endpoints for tracking body composition measurements including weight, body fat, and muscle mass.

### Body Composition Endpoints

#### Add Body Composition Measurement
```bash
curl -X POST "http://localhost:8000/api/v1/metric/body/composition" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "measurement_date": "2024-01-01T08:00:00Z",
    "weight": 70.5,
    "body_fat_percentage": 15.2,
    "muscle_mass_percentage": 45.8,
    "bone_density": 1.2,
    "notes": "Morning measurement"
  }'
```

#### Get All Body Composition Records
```bash
curl -X GET "http://localhost:8000/api/v1/metric/body/composition" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update Body Composition Record
```bash
curl -X PUT "http://localhost:8000/api/v1/metric/body/composition/metric..abc123def456" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 70.0,
    "notes": "Updated measurement"
  }'
```

#### Delete Body Composition Record
```bash
curl -X DELETE "http://localhost:8000/api/v1/metric/body/composition/metric..abc123def456" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Body Composition Data Structure

Each body composition record contains:
- **id**: RID identifier (format: `metric..<random-string>`)
- **user_id**: User RID identifier (format: `auth..user.<random-string>`)
- **measurement_date**: Date and time of measurement (ISO format)
- **weight**: Weight measurement in kg or lbs
- **body_fat_percentage**: Body fat percentage (0-100)
- **muscle_mass_percentage**: Muscle mass percentage (0-100)
- **bone_density**: Bone density measurement
- **notes**: Additional notes about the measurement
- **created_at**: Timestamp when record was created
- **updated_at**: Timestamp when record was last updated

## Goals API

The API provides endpoints for managing user goals including weight, macro, and general goals.

### Goals Endpoints

#### Create Weight Goal
```bash
curl -X POST "http://localhost:8000/api/v1/goal/weight" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date_hour": "2024-01-01T00:00:00Z",
    "weight": 65.0,
    "body_fat_percentage": 12.0,
    "muscle_mass_percentage": 48.0
  }'
```

#### Get Weight Goals
```bash
curl -X GET "http://localhost:8000/api/v1/goal/weight" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Update Weight Goal
```bash
curl -X PUT "http://localhost:8000/api/v1/goal/weight/goal..abc123def456" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "weight": 63.0,
    "body_fat_percentage": 10.0
  }'
```

#### Delete Weight Goal
```bash
curl -X DELETE "http://localhost:8000/api/v1/goal/weight/goal..abc123def456" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

#### Create Macro Goal
```bash
curl -X POST "http://localhost:8000/api/v1/goal/macros" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "date_hour": "2024-01-01T00:00:00Z",
    "calories": 2000,
    "protein": 150.0,
    "carbs": 200.0,
    "fat": 80.0
  }'
```

#### Create General Goal
```bash
curl -X POST "http://localhost:8000/api/v1/goal/general" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "goal_description": "Run a 5K marathon",
    "target_date": "2024-06-01T00:00:00Z"
  }'
```

### Goals Data Structure

**Weight Goals:**
- **id**: RID identifier (format: `goal..<random-string>`)
- **user_id**: User RID identifier (format: `auth..user.<random-string>`)
- **date_hour**: Target date and hour for the goal
- **weight**: Target weight in kg or lbs
- **body_fat_percentage**: Target body fat percentage
- **muscle_mass_percentage**: Target muscle mass percentage
- **created_at**: Timestamp when goal was created
- **updated_at**: Timestamp when goal was last updated

**Macro Goals:**
- **id**: RID identifier (format: `goal..<random-string>`)
- **user_id**: User RID identifier (format: `auth..user.<random-string>`)
- **date_hour**: Target date and hour for the goal
- **calories**: Target daily calories
- **protein**: Target protein in grams
- **carbs**: Target carbohydrates in grams
- **fat**: Target fat in grams
- **created_at**: Timestamp when goal was created
- **updated_at**: Timestamp when goal was last updated

**General Goals:**
- **id**: RID identifier (format: `goal..<random-string>`)
- **user_id**: User RID identifier (format: `auth..user.<random-string>`)
- **goal_description**: Description of the general goal
- **target_date**: Optional target date for completion
- **created_at**: Timestamp when goal was created
- **updated_at**: Timestamp when goal was last updated

## Frontend Integration

The backend serves the frontend static files from the `frontend/dist` directory. Make sure to build your frontend application and place the built files in this location before deploying.