"""Update nutrition tables

Revision ID: 87ea85d37f8d
Revises: 3753f108ec9a
Create Date: 2025-11-03 04:09:06.328949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '87ea85d37f8d'
down_revision: Union[str, Sequence[str], None] = '3753f108ec9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Update food_preferences table
    op.add_column('food_preferences', sa.Column('notes', sa.Text(), nullable=True))
    
    # Update foods table
    op.add_column('foods', sa.Column('serving_unit', sa.String(), nullable=True))
    op.add_column('foods', sa.Column('serving_size', sa.Numeric(precision=10, scale=2), nullable=True))
    op.drop_index(op.f('ix_foods_user_id'), table_name='foods')
    op.drop_constraint(op.f('foods_user_id_fkey'), 'foods', type_='foreignkey')
    op.drop_column('foods', 'is_saved')
    op.drop_column('foods', 'user_id')
    op.drop_column('foods', 'notes')
    
    # Update nutrition_macros table (add food_name as nullable first, migrate data, then make required)
    op.add_column('nutrition_macros', sa.Column('food_name', sa.String(), nullable=True))
    op.execute("UPDATE nutrition_macros SET food_name = COALESCE(meal_name, '') WHERE food_name IS NULL")
    op.alter_column('nutrition_macros', 'food_name', nullable=False)
    op.add_column('nutrition_macros', sa.Column('is_saved', sa.Boolean(), nullable=False, server_default='false'))
    # Ensure no NULL calories before making it required
    op.execute("UPDATE nutrition_macros SET calories = 0 WHERE calories IS NULL")
    op.alter_column('nutrition_macros', 'calories',
               existing_type=sa.NUMERIC(),
               nullable=False)
    op.drop_column('nutrition_macros', 'meal_name')


def downgrade() -> None:
    """Downgrade schema."""
    # Revert nutrition_macros changes
    op.add_column('nutrition_macros', sa.Column('meal_name', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.execute("UPDATE nutrition_macros SET meal_name = food_name WHERE food_name IS NOT NULL")
    op.alter_column('nutrition_macros', 'calories',
               existing_type=sa.NUMERIC(),
               nullable=True)
    op.drop_column('nutrition_macros', 'is_saved')
    op.drop_column('nutrition_macros', 'food_name')
    
    # Revert foods table changes
    op.add_column('foods', sa.Column('notes', sa.TEXT(), autoincrement=False, nullable=True))
    op.add_column('foods', sa.Column('user_id', sa.VARCHAR(), autoincrement=False, nullable=True))
    op.add_column('foods', sa.Column('is_saved', sa.BOOLEAN(), autoincrement=False, nullable=False, server_default='false'))
    op.create_foreign_key(op.f('foods_user_id_fkey'), 'foods', 'auth_users', ['user_id'], ['id'])
    op.create_index(op.f('ix_foods_user_id'), 'foods', ['user_id'], unique=False)
    op.drop_column('foods', 'serving_size')
    op.drop_column('foods', 'serving_unit')
    
    # Revert food_preferences table changes
    op.drop_column('food_preferences', 'notes')
