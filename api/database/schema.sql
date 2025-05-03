PRAGMA foreign_keys = ON;

-- Table : cars
CREATE TABLE IF NOT EXISTS CARS (
    id INTEGER PRIMARY KEY,
    car_name TEXT NOT NULL,
    strengths TEXT NOT NULL,
    description TEXT NOT NULL,
    full_description TEXT NOT NULL
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_cars_id ON cars (id);
CREATE INDEX IF NOT EXISTS idx_cars_name ON cars (car_name);
