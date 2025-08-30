# SupaHealth Backend

A modern backend API built with FastAPI, PostgreSQL, and OpenAI integration.

## Features

- FastAPI backend with async support
- PostgreSQL database integration
- OpenAI ChatGPT integration
- Secure authentication system
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

The application uses Alembic for database migrations. Migrations are automatically run when the application starts. To manually manage migrations:

```bash
# Create a new migration
docker compose exec app alembic revision --autogenerate -m "Description of changes"

# Apply migrations
docker compose exec app alembic upgrade head

# Rollback one migration
docker compose exec app alembic downgrade -1
```

### API Endpoints

The main API endpoints include:

- `POST /api/auth/signin`: User authentication
- `POST /api/auth/signup`: User registration
- `POST /api/chat`: Chat with AI assistant
- `GET /api/health`: Health check endpoint

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

## Frontend Integration

The backend serves the frontend static files from the `frontend/dist` directory. Make sure to build your frontend application and place the built files in this location before deploying.