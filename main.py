from __future__ import annotations

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from typing import Literal
from sqlalchemy import create_engine, String, ForeignKey, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, relationship


# ============================================================
# ALLOWED VALUES
# ============================================================

Category = Literal[
    "hardware",
    "software",
    "network",
    "account",
    "other",
]

Priority = Literal[
    "low",
    "medium",
    "high",
    "critical",
]

Status = Literal[
    "open",
    "assigned",
    "in_progress",
    "resolved",
    "closed",
]


# ============================================================
# PYDANTIC INPUT MODELS
# ============================================================


class UserCreate(BaseModel):
    name: str
    email: str
    department: str


class UserPatch(BaseModel):
    name: str | None = None
    email: str | None = None
    department: str | None = None


class TechnicianCreate(BaseModel):
    name: str
    specialty: str
    active: bool = True


class TechnicianPatch(BaseModel):
    name: str | None = None
    specialty: str | None = None
    active: bool | None = None


class TicketCreate(BaseModel):
    user_id: int
    title: str
    category: Category
    priority: Priority
    status: Status = "open"
    technician_id: int | None = None


class TicketPatch(BaseModel):
    user_id: int | None = None
    title: str | None = None
    category: Category | None = None
    priority: Priority | None = None
    status: Status | None = None
    technician_id: int | None = None


class CommentCreate(BaseModel):
    author: str = Field(min_length=1)
    message: str = Field(min_length=1)


# ============================================================
# PYDANTIC OUTPUT MODELS
# ============================================================


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: str
    department: str


class TechnicianOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    specialty: str
    active: bool


class TicketOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    title: str
    category: str
    priority: str
    status: str
    technician_id: int | None


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    ticket_id: int
    author: str
    message: str


class TicketDetailsOut(BaseModel):
    ticket: TicketOut
    user: UserOut
    technician: TechnicianOut | None
    comments: list[CommentOut]


# ============================================================
# SQLALCHEMY ORM MODELS
# ============================================================


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    department: Mapped[str] = mapped_column(String(255))
    age: Mapped[int | None] = mapped_column(nullable=True)
    city: Mapped[str] = mapped_column(String(100))
    Country: Mapped[str | None] = mapped_column(String(255))
    passport: Mapped[str] = mapped_column(String(255))
    tickets: Mapped[list[Ticket]] = relationship(back_populates="user")


class Technician(Base):
    __tablename__ = "technicians"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    specialty: Mapped[str] = mapped_column(String(100))
    active: Mapped[bool] = mapped_column(default=True)

    tickets: Mapped[list[Ticket]] = relationship(back_populates="technician")


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(100), default="open")
    technician_id: Mapped[int | None] = mapped_column(
        ForeignKey("technicians.id"),
        nullable=True,
    )

    user: Mapped[User] = relationship(back_populates="tickets")

    technician: Mapped[Technician | None] = relationship(back_populates="tickets")

    comments: Mapped[list[Comment]] = relationship(
        back_populates="ticket",
        cascade="all, delete-orphan",
    )


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(primary_key=True)
    ticket_id: Mapped[int] = mapped_column(ForeignKey("tickets.id"))
    author: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(String(255))

    ticket: Mapped[Ticket] = relationship(back_populates="comments")


# ============================================================
# DATABASE
# ============================================================

engine = create_engine("postgresql+psycopg://postgres@localhost:5432/postgres")

# ============================================================
# OPTIONAL INITIAL SAMPLE DATA
# Seeds only if ALL tables are empty.
# ============================================================

# def seed_database():
#     with Session(engine) as session:
#         has_users = session.scalar(select(User.id).limit(1)) is not None
#         has_technicians = session.scalar(select(Technician.id).limit(1)) is not None
#         has_tickets = session.scalar(select(Ticket.id).limit(1)) is not None
#         has_comments = session.scalar(select(Comment.id).limit(1)) is not None

#         if has_users or has_technicians or has_tickets or has_comments:
#             return

#         lucas = User(
#             name="Lucas",
#             email="lucas@acme.com",
#             department="Sales",
#         )
#         maria = User(
#             name="Maria",
#             email="maria@acme.com",
#             department="Finance",
#         )
#         sofia = User(
#             name="Sofia",
#             email="sofia@nova.com",
#             department="Engineering",
#         )

#         daniel = Technician(
#             name="Daniel",
#             specialty="hardware",
#             active=True,
#         )
#         emma = Technician(
#             name="Emma",
#             specialty="software",
#             active=True,
#         )
#         tom = Technician(
#             name="Tom",
#             specialty="network",
#             active=False,
#         )

#         session.add_all([
#             lucas,
#             maria,
#             sofia,
#             daniel,
#             emma,
#             tom,
#         ])
#         session.flush()

#         ticket1 = Ticket(
#             user_id=lucas.id,
#             title="Laptop won't start",
#             category="hardware",
#             priority="high",
#             status="open",
#             technician_id=None,
#         )

#         ticket2 = Ticket(
#             user_id=maria.id,
#             title="Excel keeps crashing",
#             category="software",
#             priority="medium",
#             status="assigned",
#             technician_id=emma.id,
#         )

#         session.add_all([ticket1, ticket2])
#         session.flush()

#         comment = Comment(
#             ticket_id=ticket2.id,
#             author="Emma",
#             message="Checking the Excel installation.",
#         )

#         session.add(comment)
#         session.commit()


# seed_database()


# ============================================================
# APP
# ============================================================

app = FastAPI()


# ============================================================
# DB FINDERS
# ============================================================


def get_user_or_404(session: Session, user_id: int) -> User:
    user = session.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found",
        )

    return user


def get_technician_or_404(
    session: Session,
    technician_id: int,
) -> Technician:
    technician = session.get(Technician, technician_id)

    if technician is None:
        raise HTTPException(
            status_code=404,
            detail="Technician not found",
        )

    return technician


def get_ticket_or_404(session: Session, ticket_id: int) -> Ticket:
    ticket = session.get(Ticket, ticket_id)

    if ticket is None:
        raise HTTPException(
            status_code=404,
            detail="Ticket not found",
        )

    return ticket


# ============================================================
# USERS
# ============================================================


@app.post("/users", response_model=UserOut, status_code=201)
def add_user(data: UserCreate):
    with Session(engine) as session:
        user = User(
            name=data.name,
            email=data.email,
            department=data.department,
        )

        session.add(user)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail="A user with that email already exists",
            )

        session.refresh(user)
        return user


@app.get("/users", response_model=list[UserOut])
def get_users():
    with Session(engine) as session:
        statement = select(User)
        users = session.scalars(statement).all()
        return users


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    with Session(engine) as session:
        return get_user_or_404(session, user_id)


@app.patch("/users/{user_id}", response_model=UserOut)
def patch_user(user_id: int, data: UserPatch):
    with Session(engine) as session:
        user = get_user_or_404(session, user_id)

        updates = data.model_dump(exclude_unset=True)

        for key, value in updates.items():
            if value is None:
                raise HTTPException(
                    status_code=422,
                    detail=f"{key} cannot be null",
                )

            setattr(user, key, value)

        try:
            session.commit()
        except IntegrityError:
            session.rollback()
            raise HTTPException(
                status_code=409,
                detail="That email is already in use",
            )

        session.refresh(user)
        return user


@app.delete("/users/{user_id}")
def delete_user(user_id: int):
    with Session(engine) as session:
        user = get_user_or_404(session, user_id)

        if user.tickets:
            raise HTTPException(
                status_code=409,
                detail="Cannot delete a user that still has tickets",
            )

        session.delete(user)
        session.commit()

        return {"message": "User deleted"}


# ============================================================
# TECHNICIANS
# ============================================================


@app.post(
    "/technicians",
    response_model=TechnicianOut,
    status_code=201,
)
def add_technician(data: TechnicianCreate):
    with Session(engine) as session:
        technician = Technician(
            name=data.name,
            specialty=data.specialty,
            active=data.active,
        )

        session.add(technician)
        session.commit()
        session.refresh(technician)

        return technician


@app.get(
    "/technicians",
    response_model=list[TechnicianOut],
)
def get_technicians():
    with Session(engine) as session:
        statement = select(Technician)
        technicians = session.scalars(statement).all()
        return technicians


@app.get(
    "/technicians/{technician_id}",
    response_model=TechnicianOut,
)
def get_technician(technician_id: int):
    with Session(engine) as session:
        return get_technician_or_404(session, technician_id)


@app.patch(
    "/technicians/{technician_id}",
    response_model=TechnicianOut,
)
def patch_technician(
    technician_id: int,
    data: TechnicianPatch,
):
    with Session(engine) as session:
        technician = get_technician_or_404(
            session,
            technician_id,
        )

        updates = data.model_dump(exclude_unset=True)

        for key, value in updates.items():
            if value is None:
                raise HTTPException(
                    status_code=422,
                    detail=f"{key} cannot be null",
                )

            setattr(technician, key, value)

        session.commit()
        session.refresh(technician)

        return technician


# ============================================================
# SPECIAL TICKET QUERIES
# ============================================================


@app.get(
    "/tickets/status/{status}",
    response_model=list[TicketOut],
)
def tickets_by_status(status: Status):
    with Session(engine) as session:
        statement = select(Ticket).where(Ticket.status == status)

        tickets = session.scalars(statement).all()
        return tickets


@app.get(
    "/users/{user_id}/tickets",
    response_model=list[TicketOut],
)
def tickets_by_user(user_id: int):
    with Session(engine) as session:
        get_user_or_404(session, user_id)

        statement = select(Ticket).where(Ticket.user_id == user_id)

        tickets = session.scalars(statement).all()
        return tickets


@app.get(
    "/technicians/{technician_id}/tickets",
    response_model=list[TicketOut],
)
def tickets_by_technician(technician_id: int):
    with Session(engine) as session:
        get_technician_or_404(session, technician_id)

        statement = select(Ticket).where(Ticket.technician_id == technician_id)

        tickets = session.scalars(statement).all()
        return tickets


# ============================================================
# TICKETS
# ============================================================


@app.post("/tickets", response_model=TicketOut, status_code=201)
def add_ticket(data: TicketCreate):
    with Session(engine) as session:
        get_user_or_404(session, data.user_id)

        if data.technician_id is not None:
            get_technician_or_404(
                session,
                data.technician_id,
            )

        ticket = Ticket(
            user_id=data.user_id,
            title=data.title,
            category=data.category,
            priority=data.priority,
            status=data.status,
            technician_id=data.technician_id,
        )

        session.add(ticket)
        session.commit()
        session.refresh(ticket)

        return ticket


@app.get("/tickets", response_model=list[TicketOut])
def get_tickets():
    with Session(engine) as session:
        statement = select(Ticket)
        tickets = session.scalars(statement).all()
        return tickets


@app.get("/tickets/{ticket_id}", response_model=TicketOut)
def get_ticket(ticket_id: int):
    with Session(engine) as session:
        return get_ticket_or_404(session, ticket_id)


@app.patch("/tickets/{ticket_id}", response_model=TicketOut)
def patch_ticket(
    ticket_id: int,
    data: TicketPatch,
):
    with Session(engine) as session:
        ticket = get_ticket_or_404(session, ticket_id)

        updates = data.model_dump(exclude_unset=True)

        if "user_id" in updates:
            if updates["user_id"] is None:
                raise HTTPException(
                    status_code=422,
                    detail="user_id cannot be null",
                )

            get_user_or_404(session, updates["user_id"])

        if "technician_id" in updates:
            technician_id = updates["technician_id"]

            if technician_id is not None:
                get_technician_or_404(
                    session,
                    technician_id,
                )

        for key, value in updates.items():
            if key != "technician_id" and value is None:
                raise HTTPException(
                    status_code=422,
                    detail=f"{key} cannot be null",
                )

            setattr(ticket, key, value)

        session.commit()
        session.refresh(ticket)

        return ticket


@app.delete("/tickets/{ticket_id}")
def delete_ticket(ticket_id: int):
    with Session(engine) as session:
        ticket = get_ticket_or_404(session, ticket_id)

        session.delete(ticket)
        session.commit()

        return {"message": "Ticket deleted"}


# ============================================================
# ASSIGN TECHNICIAN
# ============================================================


@app.patch(
    "/tickets/{ticket_id}/assign/{technician_id}",
    response_model=TicketOut,
)
def assign_technician(
    ticket_id: int,
    technician_id: int,
):
    with Session(engine) as session:
        ticket = get_ticket_or_404(session, ticket_id)
        technician = get_technician_or_404(
            session,
            technician_id,
        )

        if not technician.active:
            raise HTTPException(
                status_code=409,
                detail="Cannot assign an inactive technician",
            )

        ticket.technician_id = technician.id
        ticket.status = "assigned"

        session.commit()
        session.refresh(ticket)

        return ticket


# ============================================================
# RESOLVE TICKET
# ============================================================


@app.patch(
    "/tickets/{ticket_id}/resolve",
    response_model=TicketOut,
)
def resolve_ticket(ticket_id: int):
    with Session(engine) as session:
        ticket = get_ticket_or_404(session, ticket_id)

        ticket.status = "resolved"

        session.commit()
        session.refresh(ticket)

        return ticket


# ============================================================
# COMMENTS
# ============================================================


@app.post(
    "/tickets/{ticket_id}/comments",
    response_model=CommentOut,
    status_code=201,
)
def add_comment(
    ticket_id: int,
    data: CommentCreate,
):
    with Session(engine) as session:
        get_ticket_or_404(session, ticket_id)

        comment = Comment(
            ticket_id=ticket_id,
            author=data.author,
            message=data.message,
        )

        session.add(comment)
        session.commit()
        session.refresh(comment)

        return comment


@app.get(
    "/tickets/{ticket_id}/comments",
    response_model=list[CommentOut],
)
def get_comments(ticket_id: int):
    with Session(engine) as session:
        get_ticket_or_404(session, ticket_id)

        statement = select(Comment).where(Comment.ticket_id == ticket_id)

        comments = session.scalars(statement).all()
        return comments


# ============================================================
# COMPLETE TICKET DETAILS
# ============================================================


@app.get(
    "/tickets/{ticket_id}/details",
    response_model=TicketDetailsOut,
)
def ticket_details(ticket_id: int):
    with Session(engine) as session:
        ticket = get_ticket_or_404(session, ticket_id)
        user = get_user_or_404(session, ticket.user_id)

        technician = None

        if ticket.technician_id is not None:
            technician = get_technician_or_404(
                session,
                ticket.technician_id,
            )

        statement = select(Comment).where(Comment.ticket_id == ticket_id)

        comments = session.scalars(statement).all()

        return {
            "ticket": ticket,
            "user": user,
            "technician": technician,
            "comments": comments,
        }
