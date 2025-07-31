import tkinter as tk
from tkinter import ttk
from tkinter import messagebox, simpledialog, Toplevel, Text
import mysql.connector
import json
import re

try:
    with open("credentials.json", "r") as file:
        credentials = json.load(file)

    db = mysql.connector.connect(
        host="localhost",
        user=credentials["user"],
        password=credentials["password"],
        database="dbproject"
    )
except Exception as e:
    import tkinter.messagebox as mbox
    mbox.showerror("Connection Error", f"Failed to connect to database:\n{e}")
    exit()


root = tk.Tk()
root.title("Space Travel Database")

# Tables   
def create_planet_table(cursor):
    cursor.execute("""
    CREATE TABLE planets (
    planet_name VARCHAR(50) NOT NULL UNIQUE,
    size BIGINT NOT NULL,
    population BIGINT NOT NULL,
    PRIMARY KEY (planet_name)
    )
    """)
    db.commit()


def create_spacestation_table(cursor):
    cursor.execute("""
    CREATE TABLE spacestations (
    station_name VARCHAR(50) NOT NULL UNIQUE,
    planet_associated VARCHAR(50) DEFAULT NULL,
    capacity_limit INT NOT NULL,
    PRIMARY KEY (station_name),
    CONSTRAINT fk_planet
        FOREIGN KEY (planet_associated) REFERENCES planet(planet_name)
    )
    """)
    db.commit()

def create_spaceports_table(cursor):
    cursor.execute("""
    CREATE TABLE spaceports (
        spaceport_id INT PRIMARY KEY AUTO_INCREMENT,
        port_name VARCHAR(100) NOT NULL,
        planet_name VARCHAR(50) NULL,
        station_name VARCHAR(100) NULL,
        capacity INT NOT NULL,
        fee INT NOT NULL,
        FOREIGN KEY (planet_name) REFERENCES planets(planet_name),
        FOREIGN KEY (station_name) REFERENCES spacestations(station_name),
        CONSTRAINT chk_spaceport_owner CHECK (
            (planet_name IS NOT NULL AND station_name IS NULL) OR
            (planet_name IS NULL AND station_name IS NOT NULL AND port_name = station_name)
        )
        CONSTRAINT chk_spaceport_capacity CHECK (capacity > 0),
        CONSTRAINT chk_spaceport_fee CHECK (fee >= 0)
    )
    """)
    db.commit()

def create_spacecrafts_table(cursor):
    cursor.execute("""
    CREATE TABLE spacecrafts (
    type_name VARCHAR(100) PRIMARY KEY,
    capacity  INT NOT NULL,
    range     INT NOT NULL,
    CONSTRAINT chk_sc_capacity CHECK (capacity > 0),
    CONSTRAINT chk_sc_range    CHECK (range > 0)
    )
    """)
    db.commit()

def create_routes_table(cursor):
    cursor.execute("""
    CREATE TABLE routes (
        origin_id INT NOT NULL,
        dest_id INT NOT NULL,
        dist INT NOT NULL,
        PRIMARY KEY (origin_id, dest_id),
        FOREIGN KEY (origin_id) REFERENCES spaceports(spaceport_id),
        FOREIGN KEY (dest_id) REFERENCES spaceports(spaceport_id),
        CONSTRAINT chk_not_interplanet CHECK (
            (SELECT COUNT(planet_name) FROM spaceports WHERE (spaceport_id = origin_id or spaceport_id = dest_id) AND planet_name IS NOT NULL) != 2
            OR (SELECT planet_name FROM spaceports WHERE spaceport_id = origin_id) != (SELECT planet_name FROM spaceports WHERE spaceport_id = dest_id)
        )
    )
    """)
    db.commit()
    
def create_indexes(cursor):
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_route_origin ON routes(origin_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_flight_type ON flights(spacecraft_type)")
    db.commit()

def create_flight_table(cursor):
    cursor.execute("""
    CREATE TABLE flights (
    flight_number   VARCHAR(20) PRIMARY KEY,
    route_id        INT NOT NULL,
    spacecraft_type VARCHAR(100) NOT NULL,
    departure_day  ENUM("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday") NOT NULL,
    departure_time  TIME NOT NULL,
    depart_hour     TINYINT UNSIGNED GENERATED ALWAYS AS (HOUR(departure_time)) STORED,
    flight_duration DECIMAL(4,2) NOT NULL,
    CONSTRAINT fk_flight_route  FOREIGN KEY (route_id)        REFERENCES Route(origin_id),
    CONSTRAINT fk_flight_craft  FOREIGN KEY (spacecraft_type) REFERENCES spacecrafts(type_name),
    CONSTRAINT chk_flight_duration CHECK (flight_duration > 0))
    )
    """)
    db.commit()

# Data Entry


def enter_planet(cursor, planet_name, size, population):
    if not planet_name.strip():
        messagebox.showerror("Validation Error", "Planet name cannot be empty.")
        return False
    if not isinstance(size, int) or size <= 0:
        messagebox.showerror("Validation Error", "Planet size must be a positive integer.")
        return False
    if not isinstance(population, int) or population < 0:
        messagebox.showerror("Validation Error", "Population must be a non-negative integer.")
        return False

    sql = """INSERT INTO planets VALUES (%s, %s, %s)"""
    values = [planet_name, size, population]
    return confirm_and_commit(cursor, sql, values)
    # return True

def enter_spacestation(cursor, station_name, has_spaceport, planet_associated, capacity_limit):
    if not station_name.strip():
        messagebox.showerror("Validation Error", "Station name cannot be empty.")
        return False
    if planet_associated and not planet_associated.strip():
        messagebox.showerror("Validation Error", "Planet associated must be a valid string or NULL.")
        return False
    if not isinstance(capacity_limit, int) or capacity_limit <= 0:
        messagebox.showerror("Validation Error", "Capacity must be a positive integer.")
        return False

    sql = """INSERT INTO spacestations VALUES (%s, %s, %s, %s)"""
    values = [station_name, has_spaceport, planet_associated, capacity_limit]
    return confirm_and_commit(cursor, sql, values)
    # return True

def enter_spaceport(cursor, port_name, planet_associated, spacestation_name, fee, capacity):
    if not port_name.strip():
        messagebox.showerror("Validation Error", "Port name cannot be empty.")
        return False
    if planet_associated is None and spacestation_name is None:
        messagebox.showerror("Validation Error", "Must be owned by either a planet or a spacestation.")
        return False
    if not isinstance(fee, int) or fee < 0:
        messagebox.showerror("Validation Error", "Fee must be a non-negative integer.")
        return False
    if not isinstance(capacity, int) or capacity <= 0:
        messagebox.showerror("Validation Error", "Capacity must be a positive integer.")
        return False

    sql = """INSERT INTO spaceports (port_name, planet_name, station_name, fee, capacity) VALUES (%s, %s, %s, %s, %s)"""
    values = [port_name, planet_associated, spacestation_name, fee, capacity]
    return confirm_and_commit(cursor, sql, values)
    # return True

def enter_spacecraft(cursor, type_name, capacity, range):
    if not type_name.strip():
        messagebox.showerror("Validation Error", "Type name cannot be empty.")
        return False
    if not isinstance(capacity, int) or capacity <= 0:
        messagebox.showerror("Validation Error", "Capacity must be a positive integer.")
        return False
    if not isinstance(range, int) or range <= 0:
        messagebox.showerror("Validation Error", "Range must be a positive integer.")
        return False

    sql = """INSERT INTO spacecrafts VALUES (%s, %s, %s)"""
    values = [type_name, capacity, range]
    return confirm_and_commit(cursor, sql, values)
    # return True

def enter_route(cursor, origin_id, destination_id, distance):
    if origin_id == destination_id:
        messagebox.showerror("Validation Error", "Origin and destination cannot be the same.")
        return False
    if not isinstance(distance, int) or distance <= 0:
        messagebox.showerror("Validation Error", "Distance must be a positive integer.")
        return False

    sql = """INSERT INTO routes VALUES (%s, %s, %s)"""
    values = [origin_id, destination_id, distance]
    return confirm_and_commit(cursor, sql, values)
    # return True

def enter_flight(cursor, flight_number, route_id, spacecraft_type, departure_time, flight_duration):
    if not flight_number.strip():
        messagebox.showerror("Validation Error", "Flight number cannot be empty.")
        return False
    if not isinstance(flight_duration, (int, float)) or flight_duration <= 0:
        messagebox.showerror("Validation Error", "Flight duration must be a positive number.")
        return False

    sql = """INSERT INTO flights (flight_number, route_id, spacecraft_type, departure_time, flight_duration)
             VALUES (%s, %s, %s, %s, %s)"""
    values = [flight_number, route_id, spacecraft_type, departure_time, flight_duration]
    return confirm_and_commit(cursor, sql, values)
    # return True

# Querying

# Given port name return all ports with flights that arrive or depart from the given port name
def get_port_by_port_name_with_flights(cursor, port_name):
    pass

# Given a port name, and a date range from start_date to end_date, return all flights that depart from at the given port name and return the details of the flights
def get_departures_by_date_range_and_port(cursor, start_date, end_date, port_name):
    pass

# Given a port name, and a date range from start_date to end_date, return all flights that arrive at the given port name and return the details of the flights
def get_arrivals_by_date_range_and_port(cursor, start_date, end_date, port_name):
    pass

# Given a route, return all flights on that route showing details of the flights
def get_flights_by_route(cursor, origin_id, destination_id):
    pass

#given an itinerary with a departure date, destination, origin, max travel time, and max stops, return all flights that match the criteria
def flight_finder(cursor, departure_date, origin_id, destination_id, max_travel_time, max_stops):
    pass




# Helper Functions

def execute_query(cursor, sql, values):
    try:
        cursor.execute(sql, values)
        return True
    except mysql.connector.Error as err:
        messagebox.showerror("Database Error", f"Error: {err}")
        return False

def confirm_and_commit(cursor, sql, values):
    complete = execute_query(cursor, sql, values)
    if complete is False:
        return False
    if messagebox.askyesno("Confirm", "Do you want to save this entry?"):
        db.commit()
        return True
    else:
        db.rollback()
        return False
    
def table_exists(cursor, table):
    table_name = table.lower()
    cursor.execute("SHOW TABLES")
    existing_tables = cursor.fetchall()
    existing_tables = [x[0] for x in existing_tables]
    return table_name in existing_tables

def display_results(rows):
    result_win = Toplevel()
    result_win.title("Query Results")

    text_widget = Text(result_win, wrap='none', height=25, width=100)
    text_widget.pack(expand=True, fill='both')

    for row in rows:
        line = "\t".join(str(col) for col in row)
        text_widget.insert("end", line + "\n")

# create each table if they don't exist
def create_nonexisting_tables(cursor):
    if not table_exists(cursor, "planets"):
        create_planet_table(cursor)
    if not table_exists(cursor, "spacestations"):
        create_spacestation_table(cursor)
    if not table_exists(cursor, "spaceports"):
        create_spaceports_table(cursor)
    if not table_exists(cursor, "spacecrafts"):
        create_spacecrafts_table(cursor)
    if not table_exists(cursor, "routes"):
        create_routes_table(cursor)
    if not table_exists(cursor, "flights"):
        create_flight_table(cursor)

root.mainloop()