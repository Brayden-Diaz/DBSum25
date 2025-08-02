-- Insert SpacecraftType --

-- Valid insertion
INSERT INTO SpacecraftTypes (type_name, capacity, `range`)
VALUES ('StarRunner', 150, 500000);

-- Should fail: negative range
INSERT INTO SpacecraftTypes (type_name, capacity, `range`)
VALUES ('BadRunner', 150, -100);

-- Should fail: missing capacity
INSERT INTO SpacecraftTypes (type_name, `range`)
VALUES ('MissingCapacityRunner', 300000);



-- Insert Planet --

-- Valid insertion
INSERT INTO planets VALUES ('Mars', 6779000, 500000000);

-- Should fail: duplicate planet
INSERT INTO planets VALUES ('Mars', 6779000, 500000000);



-- Insert Spacestation--

-- Valid insertion
INSERT INTO spacestations VALUES ('RedBase', 'Mars', 200);

-- Should fail: invalid planet reference
INSERT INTO spacestations VALUES ('GhostBase', 'Neptune', 150);



-- Insert Spaceport --

-- Valid insertion
INSERT INTO spaceports (port_name, planet_associated, spacestation_name, fee, capacity)
VALUES ('MarsPort1', 'Mars', 'RedBase', 4500, 300);

-- Should fail: negative fee
INSERT INTO spaceports (port_name, planet_associated, spacestation_name, fee, capacity)
VALUES ('MarsPort2', 'Mars', 'RedBase', -100, 300);

-- Should fail: bad capacity
INSERT INTO spaceports (port_name, planet_associated, spacestation_name, fee, capacity)
VALUES ('MarsPort3', 'Mars', 'RedBase', 4500, -50);

-- Insert Route --

-- First, get correct IDs:
SELECT * FROM spaceports;

-- Valid route (update IDs as needed)
INSERT INTO Routes (origin_id, destination_id, distance)
VALUES (1, 2, 600000);

-- Should fail: same origin and destination
INSERT INTO Routes (origin_id, destination_id, distance)
VALUES (3, 3, 100);

-- Should fail: duplicate route
INSERT INTO Routes (origin_id, destination_id, distance)
VALUES (1, 2, 600000);

-- Should fail: negative distance
INSERT INTO Routes (origin_id, destination_id, distance)
VALUES (3, 4, -200);


--  Insert Flight --

-- Valid flight (route_id = 2, for example)
INSERT INTO Flights (flight_number, route_id, spacecraft_type, departure_time, flight_duration)
VALUES ('FL_M2', 2, 'StarRunner', '14:30:00', 80.50);

-- Should fail: invalid spacecraft_type
INSERT INTO Flights (flight_number, route_id, spacecraft_type, departure_time, flight_duration)
VALUES ('FL_BADTYPE', 2, 'FakeCraft', '14:30:00', 80.50);

-- Should fail: duration 0
INSERT INTO Flights (flight_number, route_id, spacecraft_type, departure_time, flight_duration)
VALUES ('FL_ZERODUR', 2, 'StarRunner', '14:30:00', 0.00);



-- Insert FlightSchedule --

-- Valid schedule
INSERT INTO FlightSchedule (flight_number, day_of_week)
VALUES ('FL_M2', 'Wednesday');

-- Should fail: invalid day
INSERT INTO FlightSchedule (flight_number, day_of_week)
VALUES ('FL_M2', 'Funday');

-- Should fail: duplicate schedule
INSERT INTO FlightSchedule (flight_number, day_of_week)
VALUES ('FL_M2', 'Wednesday');



-- 1. View all planets
SELECT * FROM planets;

-- 2. View all spacestations
SELECT * FROM spacestations;

-- 3. View all spaceports
SELECT * FROM spaceports;

-- 4. View all spacecraft types
SELECT * FROM SpacecraftTypes;

-- 5. View all routes
SELECT * FROM Routes;

-- 6. View all flights
SELECT * FROM Flights;

-- 7. View all flight schedules
SELECT * FROM FlightSchedule;


-- Test: get_flights_by_route (should return FL001)
SELECT f.flight_number, r.origin_id, r.destination_id, r.distance,
       f.spacecraft_type, f.departure_time, f.flight_duration
FROM flights f
JOIN routes r ON f.route_id = r.route_id
WHERE r.origin_id = 1 AND r.destination_id = 2;


-- Test: flight_finder (valid: Monday, AlphaPort to BetaPort, duration <= 100, stops = 0)
SELECT f.flight_number, fs.day_of_week, sp1.port_name AS origin, sp2.port_name AS destination,
       f.flight_duration
FROM flights f
JOIN routes r ON f.route_id = r.route_id
JOIN flightSchedule fs ON f.flight_number = fs.flight_number
JOIN spaceports sp1 ON r.origin_id = sp1.spaceport_id
JOIN spaceports sp2 ON r.destination_id = sp2.spaceport_id
WHERE fs.day_of_week = 'Monday'
  AND r.origin_id = 1
  AND r.destination_id = 2
  AND f.flight_duration <= 100;


-- Test: flight_finder (fail: max stops = 0, but no direct route exists)
-- Simulate by querying with a nonexistent direct route
SELECT f.flight_number
FROM flights f
JOIN routes r ON f.route_id = r.route_id
JOIN flightSchedule fs ON f.flight_number = fs.flight_number
WHERE r.origin_id = 3 AND r.destination_id = 4
  AND fs.day_of_week = 'Monday';


-- Test: get_port_by_port_name_with_flights (should return FL001 if AlphaPort exists)
SELECT f.flight_number, sp.port_name
FROM flights f
JOIN routes r ON f.route_id = r.route_id
JOIN spaceports sp ON r.origin_id = sp.spaceport_id
WHERE sp.port_name = 'AlphaPort';

-- Test: departures between Monday and Friday from AlphaPort
SELECT fs.flight_number, fs.day_of_week, sp.port_name
FROM flightSchedule fs
JOIN flights f ON fs.flight_number = f.flight_number
JOIN routes r ON f.route_id = r.route_id
JOIN spaceports sp ON r.origin_id = sp.spaceport_id
WHERE fs.day_of_week BETWEEN 'Monday' AND 'Friday'
  AND sp.port_name = 'AlphaPort';

-- Test: arrivals between Monday and Friday to BetaPort
SELECT fs.flight_number, fs.day_of_week, sp.port_name
FROM flightSchedule fs
JOIN flights f ON fs.flight_number = f.flight_number
JOIN routes r ON f.route_id = r.route_id
JOIN spaceports sp ON r.destination_id = sp.spaceport_id
WHERE fs.day_of_week BETWEEN 'Monday' AND 'Friday'
  AND sp.port_name = 'BetaPort';

