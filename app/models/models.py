from sqlalchemy import Boolean, Column, Integer, String, DateTime, ForeignKey, Text, JSON, Date, Numeric, CheckConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.session import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    conversations = relationship("Conversation", back_populates="user")

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Optional metadata for AI responses
    model_used = Column(String)  # e.g., 'gpt-3.5-turbo'
    tokens_used = Column(Integer)
    extra_metadata = Column("metadata", JSON)  # For any additional metadata

    # Relationships
    conversation = relationship("Conversation", back_populates="messages")


class ActivityDaily(Base):
    __tablename__ = "activity_daily"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    steps = Column(Integer)
    move_kcal = Column(Numeric)
    exercise_min = Column(Integer)
    stand_hours = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    source = Column(Text)

    # Check constraints
    __table_args__ = (
        CheckConstraint('steps IS NULL OR steps >= 0', name='activity_daily_steps_check'),
        CheckConstraint('move_kcal IS NULL OR move_kcal >= 0', name='activity_daily_move_kcal_check'),
        CheckConstraint('exercise_min IS NULL OR exercise_min >= 0', name='activity_daily_exercise_min_check'),
        CheckConstraint('stand_hours IS NULL OR (stand_hours >= 0 AND stand_hours <= 24)', name='activity_daily_stand_hours_check'),
    )

    # Relationships
    user = relationship("User")


class NutritionDaily(Base):
    __tablename__ = "nutrition_daily"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    calories = Column(Numeric)
    protein_g = Column(Numeric)
    carbs_g = Column(Numeric)
    fats_g = Column(Numeric)
    fiber_g = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    source = Column(Text)
    sodium_mg = Column(Numeric)
    potassium_mg = Column(Numeric)
    cholesterol_mg = Column(Numeric)
    sat_fat_g = Column(Numeric)
    mono_fat_g = Column(Numeric)
    poly_fat_g = Column(Numeric)
    vitamin_c_mg = Column(Numeric)
    calcium_mg = Column(Numeric)
    iron_mg = Column(Numeric)

    # Check constraints
    __table_args__ = (
        CheckConstraint('calories IS NULL OR (calories >= 0 AND calories <= 12000)', name='nutrition_daily_calories_check'),
        CheckConstraint('protein_g IS NULL OR (protein_g >= 0 AND protein_g <= 500)', name='nutrition_daily_protein_check'),
        CheckConstraint('carbs_g IS NULL OR (carbs_g >= 0 AND carbs_g <= 1200)', name='nutrition_daily_carbs_check'),
        CheckConstraint('fats_g IS NULL OR (fats_g >= 0 AND fats_g <= 400)', name='nutrition_daily_fats_check'),
        CheckConstraint('fiber_g IS NULL OR (fiber_g >= 0 AND fiber_g <= 200)', name='nutrition_daily_fiber_check'),
    )

    # Relationships
    user = relationship("User")


class SleepDaily(Base):
    __tablename__ = "sleep_daily"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    time_asleep_min = Column(Integer)
    efficiency = Column(Numeric)
    rem_min = Column(Integer)
    deep_min = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    source = Column(Text)
    core_min = Column(Integer)
    awake_min = Column(Integer)
    in_bed_min = Column(Integer)
    sleep_start_at = Column(DateTime(timezone=True))
    sleep_end_at = Column(DateTime(timezone=True))
    in_bed_start_at = Column(DateTime(timezone=True))
    in_bed_end_at = Column(DateTime(timezone=True))

    # Check constraints
    __table_args__ = (
        CheckConstraint('time_asleep_min IS NULL OR (time_asleep_min >= 0 AND time_asleep_min <= 1200)', name='sleep_daily_time_asleep_check'),
    )

    # Relationships
    user = relationship("User")


class WeightDaily(Base):
    __tablename__ = "weight_daily"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False)
    weight_lb = Column(Numeric, nullable=False)
    source = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    lean_mass_lb = Column(Numeric)
    body_fat_pct = Column(Numeric)
    bmi = Column(Numeric)

    # Check constraints
    __table_args__ = (
        CheckConstraint('weight_lb > 0', name='weight_daily_weight_lb_check'),
    )

    # Relationships
    user = relationship("User")


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_date = Column(Date, nullable=False)
    started_at = Column(DateTime(timezone=True))
    ended_at = Column(DateTime(timezone=True))
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    workout_type = Column(Text)
    duration_sec = Column(Numeric)
    distance_mi = Column(Numeric)
    energy_kcal = Column(Numeric)
    avg_hr = Column(Integer)
    max_hr = Column(Integer)
    external_id = Column(Text)
    source = Column(Text, default='apple_health')

    # Relationships
    user = relationship("User")
    workout_sets = relationship("WorkoutSet", back_populates="session")


class WorkoutSet(Base):
    __tablename__ = "workout_sets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_id = Column(Integer, ForeignKey("workout_sessions.id"))
    ts = Column(DateTime(timezone=True))
    lift = Column(Text, nullable=False)
    set_number = Column(Integer)
    reps = Column(Integer)
    load_lb = Column(Numeric)
    rpe = Column(Numeric)
    e1rm_lb = Column(Numeric)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Check constraints
    __table_args__ = (
        CheckConstraint('reps IS NULL OR (reps >= 1 AND reps <= 50)', name='workout_sets_reps_check'),
        CheckConstraint('load_lb IS NULL OR load_lb >= 0', name='workout_sets_load_lb_check'),
        CheckConstraint('rpe IS NULL OR (rpe >= 0 AND rpe <= 10)', name='workout_sets_rpe_check'),
    )

    # Relationships
    user = relationship("User")
    session = relationship("WorkoutSession", back_populates="workout_sets")


class TestTable(Base):
    __tablename__ = "test_table"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now()) 