from sqlalchemy import String, Integer, Date, DateTime, ForeignKey, JSON, Index, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime, timezone
from .database import Base

class Route(Base):
    __tablename__ = "routes"
    id: Mapped[int] = mapped_column(primary_key=True)
    origin: Mapped[str] = mapped_column(String(80), nullable=False)
    destination: Mapped[str] = mapped_column(String(80), nullable=False)
    stops: Mapped[list] = mapped_column(JSON, nullable=False, default=list)

class Trip(Base):
    __tablename__ = "trips"
    id: Mapped[int] = mapped_column(primary_key=True)
    route_id: Mapped[int] = mapped_column(ForeignKey("routes.id"), nullable=False)
    travel_date: Mapped[object] = mapped_column(Date, nullable=False)
    departure_time: Mapped[str] = mapped_column(String(5), nullable=False)
    bus_number: Mapped[str] = mapped_column(String(20), nullable=False)
    total_seats: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    route: Mapped[Route] = relationship()

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(primary_key=True)
    pnr: Mapped[str] = mapped_column(String(16), unique=True, nullable=False)
    trip_id: Mapped[int] = mapped_column(ForeignKey("trips.id"), nullable=False)
    seat_no: Mapped[int] = mapped_column(Integer, nullable=False)
    passenger_name: Mapped[str] = mapped_column(String(100), nullable=False)
    passenger_email: Mapped[str] = mapped_column(String(160), nullable=False)
    boarding_stop: Mapped[str] = mapped_column(String(80), nullable=False)
    drop_stop: Mapped[str] = mapped_column(String(80), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="CONFIRMED")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

Index(
    "uq_active_trip_seat", Booking.trip_id, Booking.seat_no, unique=True,
    sqlite_where=text("status = 'CONFIRMED'"),
    postgresql_where=text("status = 'CONFIRMED'")
)
