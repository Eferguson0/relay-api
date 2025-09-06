"""Update existing tables to match current models

Revision ID: d499573f447c
Revises: 21bdc888bd06
Create Date: 2025-09-05 20:03:33.561184

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d499573f447c"
down_revision: Union[str, Sequence[str], None] = "21bdc888bd06"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add notes column to weight table
    op.add_column("weight", sa.Column("notes", sa.String(), nullable=True))

    # Update diet table: change id from integer to string
    # First, drop the existing primary key and index
    op.drop_constraint("diet_pkey", "diet", type_="primary")
    op.drop_index("ix_diet_id", table_name="diet")

    # Change the id column type from integer to string
    op.alter_column(
        "diet",
        "id",
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=False,
    )

    # Recreate the primary key and index
    op.create_primary_key("diet_pkey", "diet", ["id"])
    op.create_index("ix_diet_id", "diet", ["id"], unique=False)

    # Update goal tables: change from string id to user_email as primary key
    # Goal Weight table
    op.drop_constraint("goal_weight_pkey", "goal_weight", type_="primary")
    op.drop_index("ix_goal_weight_id", table_name="goal_weight")
    op.drop_column("goal_weight", "id")
    op.create_primary_key("goal_weight_pkey", "goal_weight", ["user_email"])

    # Goal Daily Diet table
    op.drop_constraint("goal_daily_diet_pkey", "goal_daily_diet", type_="primary")
    op.drop_index("ix_goal_daily_diet_id", table_name="goal_daily_diet")
    op.drop_column("goal_daily_diet", "id")
    op.create_primary_key("goal_daily_diet_pkey", "goal_daily_diet", ["user_email"])

    # Goal Message table
    op.drop_constraint("goal_message_pkey", "goal_message", type_="primary")
    op.drop_index("ix_goal_message_id", table_name="goal_message")
    op.drop_column("goal_message", "id")
    op.create_primary_key("goal_message_pkey", "goal_message", ["user_email"])


def downgrade() -> None:
    """Downgrade schema."""
    # Remove notes column from weight table
    op.drop_column("weight", "notes")

    # Revert diet table: change id from string to integer
    op.drop_constraint("diet_pkey", "diet", type_="primary")
    op.drop_index("ix_diet_id", table_name="diet")
    op.alter_column(
        "diet",
        "id",
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=False,
    )
    op.create_primary_key("diet_pkey", "diet", ["id"])
    op.create_index("ix_diet_id", "diet", ["id"], unique=False)

    # Revert goal tables: add back string id columns
    # Goal Weight table
    op.drop_constraint("goal_weight_pkey", "goal_weight", type_="primary")
    op.add_column("goal_weight", sa.Column("id", sa.VARCHAR(), nullable=False))
    op.create_primary_key("goal_weight_pkey", "goal_weight", ["id"])
    op.create_index("ix_goal_weight_id", "goal_weight", ["id"], unique=False)

    # Goal Daily Diet table
    op.drop_constraint("goal_daily_diet_pkey", "goal_daily_diet", type_="primary")
    op.add_column("goal_daily_diet", sa.Column("id", sa.VARCHAR(), nullable=False))
    op.create_primary_key("goal_daily_diet_pkey", "goal_daily_diet", ["id"])
    op.create_index("ix_goal_daily_diet_id", "goal_daily_diet", ["id"], unique=False)

    # Goal Message table
    op.drop_constraint("goal_message_pkey", "goal_message", type_="primary")
    op.add_column("goal_message", sa.Column("id", sa.VARCHAR(), nullable=False))
    op.create_primary_key("goal_message_pkey", "goal_message", ["id"])
    op.create_index("ix_goal_message_id", "goal_message", ["id"], unique=False)
