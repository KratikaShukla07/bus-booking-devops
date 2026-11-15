from datetime import date, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database import Base, get_db
from app.seed import seed

engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(bind=engine)
db = TestingSession()
seed(db)
db.close()

def override_db():
    session = TestingSession()
    try: yield session
    finally: session.close()

app.dependency_overrides[get_db] = override_db
client = TestClient(app)

def test_health():
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").json()["status"] == "ready"

def test_trip_seat_booking_and_duplicate_protection():
    trip = client.get("/trips").json()[0]
    payload = {"trip_id": trip["id"], "seat_no": 1, "travel_date": trip["travel_date"],
               "boarding_stop": trip["stops"][0], "drop_stop": trip["stops"][-1],
               "passenger": {"name": "Test Passenger", "email": "test@example.com"}}
    first = client.post("/bookings", json=payload)
    assert first.status_code == 201
    assert first.json()["pnr"].startswith("BB")
    second = client.post("/bookings", json=payload)
    assert second.status_code == 409
    seats = client.get(f"/trips/{trip['id']}/seats").json()["seats"]
    assert seats[0]["status"] == "BOOKED"

def test_cancel_releases_seat():
    trip = client.get("/trips").json()[1]
    payload = {"trip_id": trip["id"], "seat_no": 2, "travel_date": trip["travel_date"],
               "boarding_stop": trip["stops"][0], "drop_stop": trip["stops"][-1],
               "passenger": {"name": "Second Passenger", "email": "second@example.com"}}
    created = client.post("/bookings", json=payload)
    assert created.status_code == 201
    pnr = created.json()["pnr"]
    assert client.post(f"/bookings/{pnr}/cancel").json()["status"] == "CANCELLED"
    assert client.post("/bookings", json=payload).status_code == 201
