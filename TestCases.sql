-- 1. Insert Planet
INSERT INTO planet VALUES ('Earth', 12742000, 8000000000);

-- 2. Insert Spacestation
INSERT INTO spacestation VALUES ('ISS', 'Earth', 100);

-- 3. Insert Spaceport
INSERT INTO spaceport (port_name, planet_associated, spacestation_name, fee, capacity)
VALUES ('AlphaPort', 'Earth', 'ISS', 5000, 250);

-- 4. Insert second Spaceport for routing
INSERT INTO spaceport (port_name, planet_associated, spacestation_name, fee, capacity)
VALUES ('BetaPort', 'Earth', 'ISS', 5000, 250);

-- 5. Get the auto-generated spaceport IDs:
SELECT * FROM spaceport;

-- Once you get the IDs, plug them in below:
-- Let's assume AlphaPort = 1, BetaPort = 2
INSERT INTO Route (origin_id, destination_id, distance)
VALUES (1, 2, 384000);

-- 6. Insert a Flight
INSERT INTO SpacecraftType (type_name, capacity, `range`)
VALUES ('D-X', 250, 400000);
INSERT INTO Flight (flight_number, route_id, spacecraft_type, departure_time, flight_duration)
VALUES ('FL001', 1, 'Dragon-X', '08:00:00', 99.00);

-- 7. Insert into Schedule Table
INSERT INTO flightSchedule (flight_number, day_of_week)
VALUES ('FL001', 'Monday');


SELECT r.origin_id, o.port_name AS origin_name,
       r.destination_id, d.port_name AS dest_name
FROM Route r
JOIN spaceport o ON r.origin_id = o.spaceport_id
JOIN spaceport d ON r.destination_id = d.spaceport_id;


SELECT f.flight_number, f.departure_time, f.depart_hour, fs.day_of_week
FROM Flight f
JOIN flightSchedule fs ON f.flight_number = fs.flight_number;


-- Should fail: origin = destination
INSERT INTO Route (origin_id, destination_id, distance)
VALUES (1, 1, 100);

-- Should fail: duplicate route pair (already exists)
INSERT INTO Route (origin_id, destination_id, distance)
VALUES (1, 2, 384000);

-- Should fail: distance < 0
INSERT INTO Route (origin_id, destination_id, distance)
VALUES (1, 2, -100);

-- Should fail: duration <= 0
INSERT INTO Flight (flight_number, route_id, spacecraft_type, departure_time, flight_duration)
VALUES ('FL_BAD', 1, 'Dragon-X', '10:00:00', -5);

-- Should fail: spacecraft_type does not exist
INSERT INTO Flight (flight_number, route_id, spacecraft_type, departure_time, flight_duration)
VALUES ('FL_NO_TYPE', 1, 'NonExistentCraft', '10:00:00', 60);

-- Should fail: same flight + day combo already exists
INSERT INTO flightSchedule (flight_number, day_of_week)
VALUES ('FL001', 'Monday');

-- Should fail: unknown planet
INSERT INTO spacestation VALUES ('MoonBase', 'Pluto', 50);

-- Should fail: negative capacity
INSERT INTO spaceport (port_name, planet_associated, spacestation_name, fee, capacity)
VALUES ('BadPort', 'Earth', 'ISS', 5000, -10);

-- Should fail: missing capacity and range
INSERT INTO SpacecraftType (type_name)
VALUES ('Ghost-X');



-- List planets
SELECT * FROM planet;

-- List spacecraft types
SELECT * FROM SpacecraftType;

-- List spaceports
SELECT * FROM spaceport;

-- List routes
SELECT * FROM Route;

-- List flights
SELECT * FROM Flight;

-- List flight schedules
SELECT * FROM FlightSchedule;






