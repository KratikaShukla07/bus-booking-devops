# Architecture and data model

```mermaid
erDiagram
 ROUTE ||--o{ TRIP : serves
 TRIP ||--o{ BOOKING : has
 ROUTE { int id PK string origin string destination json stops }
 TRIP { int id PK int route_id FK date travel_date string departure_time int total_seats }
 BOOKING { int id PK string pnr UK int trip_id FK int seat_no string passenger_name string status }
```

A partial unique database index guarantees at most one `CONFIRMED` booking per `(trip_id, seat_no)`. The invariant is enforced in the database, not only by an application-side availability check, so concurrent requests cannot both confirm the same seat.
