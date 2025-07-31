import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
import json
import re

with open("credentials.json", "r") as file:
    credentials = json.load(file)

db = mysql.connector.connect(
    host="localhost",
    user=credentials["user"],
    password=credentials["password"],
    database="dbproject"
)

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
        apacity INT NOT NULL,
        fee INT NOT NULL,
        FOREIGN KEY (planet_name) REFERENCES planets(planet_name),
        FOREIGN KEY (station_name) REFERENCES spacestations(station_name),
        CONSTRAINT chk_spaceport_owner CHECK (
            (planet_name IS NOT NULL AND station_name IS NULL) OR
            (planet_name IS NULL AND station_name IS NOT NULL AND port_name = station_name)
        ),
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

def create_flight_table(cursor):
    cursor.execute("""
    CREATE TABLE flights (
    flight_number   VARCHAR(20) PRIMARY KEY,
    route_id        INT NOT NULL,
    spacecraft_type VARCHAR(100) NOT NULL,
    departure_time  TIME NOT NULL,
    depart_hour     TINYINT UNSIGNED GENERATED ALWAYS AS (HOUR(departure_time)) STORED,
    flight_duration DECIMAL(4,2) NOT NULL,
    CONSTRAINT fk_flight_route  FOREIGN KEY (route_id)        REFERENCES Route(route_id),
    CONSTRAINT fk_flight_craft  FOREIGN KEY (spacecraft_type) REFERENCES SpacecraftType(type_name),
    CONSTRAINT chk_flight_duration CHECK (flight_duration > 0)
    )
    """)
    db.commit()


# Data Entry

def enter_planet(cursor, planet_name, size, population):
    sql="""
    INSERT INTO planets VALUES (%s, %s, %s)
    """
    values=[planet_name, size, population]
    complete = execute_query(cursor, sql, values)
    if complete is False:
        return False
    
    db.commit()
    return True

def enter_spacestation(cursor, station_name, has_spaceport, planet_associated, capacity_limit):
    sql = """
    INSERT INTO spacestations VALUES (%s, %s, %s, %s)
    """
    values = [station_name, has_spaceport, planet_associated, capacity_limit]
    complete = execute_query(cursor, sql, values)
    if complete is False:
        return False
    db.commit()
    return True

def enter_spaceport(cursor, port_name, planet_associated, spacestation_name, fee, capacity):

    if spacestation_name is None:
        spacestation_name = "NULL"
    if planet_associated is None:
        planet_associated = "NULL"

    sql = """
    INSERT INTO spaceports VALUES (%s, %s, %s, %s, %s)
    """
    values = [port_name, planet_associated, spacestation_name, fee, capacity]
    complete = execute_query(cursor, sql, values)
    if complete is False:
        return False
    db.commit()
    return True

def enter_spacecraft(cursor, type_name, capacity, range):
    sql = """
    INSERT INTO spacecrafts VALUES (%s, %s, %s)
    """
    values = [type_name, capacity, range]
    complete = execute_query(cursor, sql, values)
    if complete is False:
        return False
    db.commit()
    return True

def enter_route(cursor, origin_name, destination_name, distance):
    sql = """
    INSERT INTO routes VALUES (%s, %s, %s)
    """
    values = [origin_name, destination_name, distance]
    complete = execute_query(cursor, sql, values)
    if complete is False:
        return False
    db.commit()
    return True

def enter_flight(cursor, flight_number, route_id, spacecraft_type, departure_time, flight_duration):
    sql = """
    INSERT INTO flights VALUES (%s, %s, %s, %s, %s)
    """
    values = [flight_number, route_id, spacecraft_type, departure_time, flight_duration]
    complete = execute_query(cursor, sql, values)
    if complete is False:
        return False
    db.commit()
    return True