from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text, create_engine
from sqlalchemy.orm import declarative_base, relationship, sessionmaker

DATABASE_URL = "sqlite:///./fitbuddy.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, index=True, nullable=False)
    username = Column(String(100), nullable=False)
    age = Column(Integer, nullable=False)
    weight = Column(Float, nullable=False)
    goal = Column(String(100), nullable=False)
    intensity = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    plans = relationship(
        "Plan",
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        String(100),
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    original_plan = Column(Text, nullable=False)
    updated_plan = Column(Text, nullable=True)
    nutrition_tip = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="plans")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def save_user(db, user_id, username, age, weight, goal, intensity):
    user = User(
        user_id=user_id,
        username=username,
        age=age,
        weight=weight,
        goal=goal,
        intensity=intensity
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def save_plan(db, user_id, original_plan, nutrition_tip):
    plan = Plan(
        user_id=user_id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    return plan


def update_plan(db, user_id, updated_plan, nutrition_tip=None):
    plan = (
        db.query(Plan)
        .filter(Plan.user_id == user_id)
        .order_by(Plan.id.desc())
        .first()
    )

    if plan:
        plan.updated_plan = updated_plan
        if nutrition_tip is not None:
            plan.nutrition_tip = nutrition_tip
        plan.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(plan)

    return plan


def get_user(db, user_id):
    return db.query(User).filter(User.user_id == user_id).first()


def get_original_plan(db, user_id):
    plan = (
        db.query(Plan)
        .filter(Plan.user_id == user_id)
        .order_by(Plan.id.desc())
        .first()
    )
    return plan.original_plan if plan else None


def get_user_plan(db, user_id):
    return (
        db.query(Plan)
        .filter(Plan.user_id == user_id)
        .order_by(Plan.id.desc())
        .first()
    )


def get_all_users(db):
    return db.query(User).order_by(User.id.desc()).all()


def delete_user(db, user_id):
    user = get_user(db, user_id)
    if user:
        db.delete(user)
        db.commit()
        return True
    return False
