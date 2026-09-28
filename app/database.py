from collections.abc import Generator
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    Float,
    Text,
    DateTime,
    ForeignKey,
    select,
)

from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    sessionmaker,
    Session,
)

from .config import DATABASE_URL


connect_args = {}

if DATABASE_URL.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    DATABASE_URL,
    connect_args=connect_args
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        index=True
    )

    name: Mapped[str] = mapped_column(
        String(120)
    )

    age: Mapped[int] = mapped_column(
        Integer
    )

    weight: Mapped[float] = mapped_column(
        Float
    )

    goal: Mapped[str] = mapped_column(
        String(80)
    )

    intensity: Mapped[str] = mapped_column(
        String(20)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    plans: Mapped[list["Plan"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )


class Plan(Base):
    __tablename__ = "plans"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    original_plan: Mapped[str] = mapped_column(
        Text
    )

    updated_plan: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    nutrition_tip: Mapped[str] = mapped_column(
        Text
    )

    feedback: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc)
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    user: Mapped[User] = relationship(
        back_populates="plans"
    )


def init_db():
    Base.metadata.create_all(
        bind=engine
    )


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def get_user(
    db: Session,
    public_user_id: str
):
    return db.scalar(
        select(User).where(
            User.user_id == public_user_id
        )
    )


def get_all_users(db: Session):
    return list(
        db.scalars(
            select(User).order_by(
                User.created_at.desc()
            )
        ).all()
    )


def get_latest_plan(
    db: Session,
    user: User
):
    return db.scalar(
        select(Plan)
        .where(Plan.user_id == user.id)
        .order_by(Plan.created_at.desc())
    )


def save_user(
    db: Session,
    data: dict
):
    user = get_user(
        db,
        data["user_id"]
    )

    if user is None:
        user = User(**data)
        db.add(user)
    else:
        for key, value in data.items():
            setattr(user, key, value)

    db.commit()
    db.refresh(user)

    return user


def save_plan(
    db: Session,
    user: User,
    original_plan: str,
    nutrition_tip: str
):
    plan = Plan(
        user_id=user.id,
        original_plan=original_plan,
        nutrition_tip=nutrition_tip
    )

    db.add(plan)
    db.commit()
    db.refresh(plan)

    return plan


def update_plan(
    db: Session,
    plan: Plan,
    updated_plan: str,
    feedback: str
):
    plan.updated_plan = updated_plan
    plan.feedback = feedback

    db.commit()
    db.refresh(plan)

    return plan