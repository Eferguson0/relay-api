from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import settings after environment variables are loaded
from app.core.config import settings
from app.db.session import Base
from app.models.auth.user import AuthUser

# Import models to ensure they are registered with Base.metadata
from app.models.enums import DataSource
from app.models.goal.general import GoalGeneral
from app.models.goal.macros import GoalMacros
from app.models.goal.weight import GoalWeight
from app.models.metric.activity.miles import ActivityMiles
from app.models.metric.activity.steps import ActivitySteps
from app.models.metric.activity.workouts import ActivityWorkouts
from app.models.metric.body.composition import BodyComposition
from app.models.metric.body.heartrate import BodyHeartRate
from app.models.metric.calories.active import CaloriesActive
from app.models.metric.calories.baseline import CaloriesBaseline
from app.models.metric.sleep.daily import SleepDaily
from app.models.nutrition.macros import NutritionMacros

_ = [
    AuthUser,
    DataSource,
    GoalGeneral,
    GoalMacros,
    GoalWeight,
    BodyComposition,
    BodyHeartRate,
    ActivitySteps,
    ActivityMiles,
    ActivityWorkouts,
    CaloriesBaseline,
    CaloriesActive,
    SleepDaily,
    NutritionMacros,
]

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Override sqlalchemy.url with our database URL
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def get_url():
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
