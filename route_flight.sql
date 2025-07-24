-- 1) SPACECRAFTTYPE
CREATE TABLE SpacecraftType (
    type_name VARCHAR(100) PRIMARY KEY,
    capacity  INT NOT NULL,
    range     INT NOT NULL,
    CONSTRAINT chk_sc_capacity CHECK (capacity > 0),
    CONSTRAINT chk_sc_range    CHECK (range > 0)
);

-- 2) ROUTE
CREATE TABLE Route (
    route_id        INT AUTO_INCREMENT PRIMARY KEY,
    origin_id       INT NOT NULL,
    destination_id  INT NOT NULL,
    distance        INT NOT NULL,
    CONSTRAINT fk_route_origin   FOREIGN KEY (origin_id)      REFERENCES Spaceport(spaceport_id),
    CONSTRAINT fk_route_dest     FOREIGN KEY (destination_id) REFERENCES Spaceport(spaceport_id),
    CONSTRAINT chk_route_distance CHECK (distance > 0),
    CONSTRAINT chk_route_not_same CHECK (origin_id <> destination_id),
    CONSTRAINT uq_route_pair      UNIQUE (origin_id, destination_id)
);

-- 3) FLIGHT
CREATE TABLE Flight (
    flight_number   VARCHAR(20) PRIMARY KEY,
    route_id        INT NOT NULL,
    spacecraft_type VARCHAR(100) NOT NULL,
    departure_time  TIME NOT NULL,
    depart_hour     TINYINT UNSIGNED AS (HOUR(departure_time)) STORED,  -- or store manually if you prefer
    flight_duration DECIMAL(4,2) NOT NULL,
    CONSTRAINT fk_flight_route  FOREIGN KEY (route_id)        REFERENCES Route(route_id),
    CONSTRAINT fk_flight_craft  FOREIGN KEY (spacecraft_type) REFERENCES SpacecraftType(type_name),
    CONSTRAINT chk_flight_duration CHECK (flight_duration > 0)
);

CREATE TABLE FlightSchedule (
    flight_number VARCHAR(20),
    day_of_week ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
    
    PRIMARY KEY (flight_number, day_of_week),
    FOREIGN KEY (flight_number) REFERENCES Flight(flight_number)
);
