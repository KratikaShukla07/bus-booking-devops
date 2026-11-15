import logging, secrets, string
from datetime import date
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError
from .database import Base, engine, get_db
from .models import Route, Trip, Booking
from .schemas import BookingCreate, BookingOut
from .seed import seed

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("bus-booking")
app = FastAPI(title="Bus Booking Trip & Seat API", version="1.0.0")

@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    from .database import SessionLocal
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()

@app.get("/health/live")
def liveness():
    return {"status": "alive"}

@app.get("/health/ready")
def readiness(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception:
        log.exception("Readiness database check failed")
        raise HTTPException(status_code=503, detail="database unavailable")

@app.get("/routes")
def list_routes(db: Session = Depends(get_db)):
    return db.query(Route).all()

@app.get("/trips")
def list_trips(travel_date: date | None = None, db: Session = Depends(get_db)):
    q = db.query(Trip)
    if travel_date:
        q = q.filter(Trip.travel_date == travel_date)
    return [{"id": t.id, "route_id": t.route_id, "origin": t.route.origin,
             "destination": t.route.destination, "stops": t.route.stops,
             "travel_date": t.travel_date, "departure_time": t.departure_time,
             "bus_number": t.bus_number, "total_seats": t.total_seats} for t in q.all()]

@app.get("/trips/{trip_id}/seats")
def seat_map(trip_id: int, db: Session = Depends(get_db)):
    trip = db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(404, "trip not found")
    booked = {b.seat_no for b in db.query(Booking).filter_by(trip_id=trip_id, status="CONFIRMED").all()}
    return {"trip_id": trip_id, "seats": [{"seat_no": n, "status": "BOOKED" if n in booked else "AVAILABLE"}
                                           for n in range(1, trip.total_seats + 1)]}

@app.post("/bookings", response_model=BookingOut, status_code=201)
def create_booking(payload: BookingCreate, db: Session = Depends(get_db)):
    trip = db.get(Trip, payload.trip_id)
    if not trip:
        raise HTTPException(404, "trip not found")
    if payload.travel_date != trip.travel_date or payload.travel_date < date.today():
        raise HTTPException(400, "travel date must match the trip and cannot be in the past")
    if payload.seat_no > trip.total_seats:
        raise HTTPException(400, "seat number is outside this bus")
    stops = trip.route.stops
    if payload.boarding_stop not in stops or payload.drop_stop not in stops:
        raise HTTPException(400, "boarding and drop stops must belong to this route")
    if stops.index(payload.boarding_stop) >= stops.index(payload.drop_stop):
        raise HTTPException(400, "drop stop must occur after boarding stop")
    alphabet = string.ascii_uppercase + string.digits
    pnr = "BB" + "".join(secrets.choice(alphabet) for _ in range(8))
    booking = Booking(pnr=pnr, trip_id=trip.id, seat_no=payload.seat_no,
                      passenger_name=payload.passenger.name, passenger_email=str(payload.passenger.email),
                      boarding_stop=payload.boarding_stop, drop_stop=payload.drop_stop, status="CONFIRMED")
    db.add(booking)
    try:
        db.commit()
        db.refresh(booking)
    except IntegrityError:
        db.rollback()
        log.warning("Seat conflict trip_id=%s seat_no=%s", trip.id, payload.seat_no)
        raise HTTPException(409, "seat is already confirmed for this trip")
    log.info("booking_created pnr=%s trip_id=%s seat=%s", booking.pnr, trip.id, booking.seat_no)
    return booking

@app.get("/bookings/{pnr}", response_model=BookingOut)
def get_booking(pnr: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter_by(pnr=pnr).first()
    if not booking:
        raise HTTPException(404, "booking not found")
    return booking

@app.post("/bookings/{pnr}/cancel", response_model=BookingOut)
def cancel_booking(pnr: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter_by(pnr=pnr).first()
    if not booking:
        raise HTTPException(404, "booking not found")
    if booking.status == "CANCELLED":
        raise HTTPException(409, "booking is already cancelled")
    booking.status = "CANCELLED"
    db.commit()
    db.refresh(booking)
    log.info("booking_cancelled pnr=%s", pnr)
    return booking
