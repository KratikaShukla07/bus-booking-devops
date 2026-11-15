from datetime import date, timedelta
from sqlalchemy.orm import Session
from .models import Route, Trip

def seed(db: Session):
    if db.query(Route).count():
        return
    routes = [
        Route(origin="Delhi", destination="Jaipur", stops=["Delhi", "Gurugram", "Neemrana", "Jaipur"]),
        Route(origin="Lucknow", destination="Kanpur", stops=["Lucknow", "Unnao", "Kanpur"]),
    ]
    db.add_all(routes)
    db.flush()
    tomorrow = date.today() + timedelta(days=1)
    db.add_all([
        Trip(route_id=routes[0].id, travel_date=tomorrow, departure_time="08:30", bus_number="DL-JP-101", total_seats=20),
        Trip(route_id=routes[1].id, travel_date=tomorrow, departure_time="10:00", bus_number="UP-KN-202", total_seats=16),
    ])
    db.commit()
