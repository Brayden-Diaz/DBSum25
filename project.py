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
    departure_datetime DATETIME NOT NULL,
    flight_duration DECIMAL(4,2) NOT NULL,
    CONSTRAINT fk_flight_route  FOREIGN KEY (route_id)        REFERENCES Route(origin_id),
    CONSTRAINT fk_flight_craft  FOREIGN KEY (spacecraft_type) REFERENCES spacecrafts(type_name),
    CONSTRAINT chk_flight_duration CHECK (flight_duration > 0))
    CONSTRAINT chk_overcapacity CHECK (
        (SELECT capacity FROM spacecrafts WHERE type_name = spacecraft_type) <=
        (SELECT capacity FROM routes, spaceports WHERE ...)
)
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
    cursor.execute("SELECT COUNT(*) FROM planets WHERE planet_name = %s", (planet_associated,))
    if cursor.fetchone()[0] == 0:
        messagebox.showerror("Validation Error", f"Planet '{planet_associated}' does not exist.")
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
    if planet_associated is None and spacestation_name is not None:
        if port_name != spacestation_name:
            messagebox.showerror("Validation Error", "Port name must match station name if owned by a spacestation.")
            return False
    if planet_associated and spacestation_name:
        messagebox.showerror("Validation Error", "A spaceport cannot belong to both a planet and a station.")
        return False
    if planet_associated:
        cursor.execute("SELECT COUNT(*) FROM planets WHERE planet_name = %s", (planet_associated,))
        if cursor.fetchone()[0] == 0:
            messagebox.showerror("Validation Error", f"Planet '{planet_associated}' does not exist.")
            return False

    if spacestation_name:
        cursor.execute("SELECT COUNT(*) FROM spacestations WHERE station_name = %s", (spacestation_name,))
        if cursor.fetchone()[0] == 0:
            messagebox.showerror("Validation Error", f"Station '{spacestation_name}' does not exist.")
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

    cursor.execute("""
        SELECT planet_name FROM spaceports WHERE spaceport_id = %s
    """, (origin_id,))
    planet1 = cursor.fetchone()

    cursor.execute("""
        SELECT planet_name FROM spaceports WHERE spaceport_id = %s
    """, (destination_id,))
    planet2 = cursor.fetchone()

    if planet1 and planet2 and planet1[0] and planet2[0] and planet1[0] == planet2[0]:
        messagebox.showerror("Validation Error", "Cannot create route between two spaceports on the same planet.")
        return False

    sql = """INSERT INTO routes VALUES (%s, %s, %s)"""
    values = [origin_id, destination_id, distance]
    return confirm_and_commit(cursor, sql, values)

    # return True

def enter_flight(cursor, flight_number, route_id, spacecraft_type, departure_day, departure_time, flight_duration):
    if not flight_number.strip():
        messagebox.showerror("Validation Error", "Flight number cannot be empty.")
        return False
    
    cursor.execute("SELECT COUNT(*) FROM flights WHERE flight_number = %s", (flight_number,))
    if cursor.fetchone()[0] > 0:
        messagebox.showerror("Validation Error", "Flight number already exists.")
        return False

    if not isinstance(flight_duration, (int, float)) or flight_duration <= 0:
        messagebox.showerror("Validation Error", "Flight duration must be a positive number.")
        return False

    cursor.execute("SELECT COUNT(*) FROM routes WHERE route_id = %s", (route_id,))
    if cursor.fetchone()[0] == 0:
        messagebox.showerror("Validation Error", f"Route ID {route_id} does not exist.")
        return False

    cursor.execute("SELECT COUNT(*) FROM spacecrafts WHERE type_name = %s", (spacecraft_type,))
    if cursor.fetchone()[0] == 0:
        messagebox.showerror("Validation Error", f"Spacecraft type '{spacecraft_type}' does not exist.")
        return False
    
    valid_days = {"Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"}
    if departure_day not in valid_days:
        messagebox.showerror("Validation Error", f"'{departure_day}' is not a valid weekday.")
        return False
    
    if not re.match(r"^\d{2}:\d{2}(:\d{2})?$", departure_time):
        messagebox.showerror("Validation Error", "Invalid time format.")
        return False

    sql = """INSERT INTO flights (flight_number, route_id, spacecraft_type, departure_day, departure_time, flight_duration)
            VALUES (%s, %s, %s, %s, %s, %s)"""
    values = [flight_number, route_id, spacecraft_type, departure_day, departure_time, flight_duration]
    return confirm_and_commit(cursor, sql, values)
    # return True

# Querying

# Given port name return all ports with flights that arrive or depart from the given port name
def get_port_by_port_name_with_flights(cursor, port_name):
    sql = """
        SELECT DISTINCT sp.spaceport_id, sp.port_name
        FROM spaceports sp
        JOIN routes r ON sp.spaceport_id = r.origin_id OR sp.spaceport_id = r.dest_id
        JOIN flights f ON r.route_id = f.route_id
        WHERE sp.port_name = %s
    """
    cursor.execute(sql, (port_name,))
    rows = cursor.fetchall()
    display_results(rows)

# Given a port name, and a date range from start_date to end_date, return all flights that depart from at the given port name and return the details of the flights
def get_departures_by_date_range_and_port(cursor, start_date, end_date, port_name):
    sql = """
        SELECT f.flight_number, f.departure_day, f.departure_time, f.flight_duration
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
        JOIN spaceports sp ON r.origin_id = sp.spaceport_id
        WHERE sp.port_name = %s AND f.departure_day BETWEEN %s AND %s
    """
    cursor.execute(sql, (port_name, start_date, end_date))
    rows = cursor.fetchall()
    display_results(rows)

# Given a port name, and a date range from start_date to end_date, return all flights that arrive at the given port name and return the details of the flights
def get_arrivals_by_date_range_and_port(cursor, start_date, end_date, port_name):
    sql = """
        SELECT f.flight_number, f.departure_day, f.departure_time, f.flight_duration
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
        JOIN spaceports sp ON r.dest_id = sp.spaceport_id
        WHERE sp.port_name = %s AND f.departure_day BETWEEN %s AND %s
    """
    cursor.execute(sql, (port_name, start_date, end_date))
    rows = cursor.fetchall()
    display_results(rows)

# Given a route, return all flights on that route showing details of the flights
def get_flights_by_route(cursor, origin_id, destination_id):
    sql = """
        SELECT f.flight_number, sp1.port_name AS origin, sp2.port_name AS destination, 
               r.dist, f.spacecraft_type, f.departure_day, f.departure_time, f.flight_duration
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
        JOIN spaceports sp1 ON r.origin_id = sp1.spaceport_id
        JOIN spaceports sp2 ON r.dest_id = sp2.spaceport_id
        WHERE r.origin_id = %s AND r.dest_id = %s
    """
    cursor.execute(sql, (origin_id, destination_id))
    rows = cursor.fetchall()
    display_results(rows)

#given an itinerary with a departure date, destination, origin, max travel time, and max stops, return all flights that match the criteria
def flight_finder(cursor, departure_date, origin_id, destination_id, max_travel_time, max_stops):
    sql = """
        SELECT f.flight_number, r.origin_id, r.dest_id, r.dist, f.spacecraft_type, 
               f.departure_day, f.departure_time, f.flight_duration
        FROM flights f
        JOIN routes r ON f.route_id = r.route_id
        WHERE r.origin_id = %s AND r.dest_id = %s
          AND f.departure_day = %s AND f.flight_duration <= %s
        LIMIT %s
    """
    cursor.execute(sql, (origin_id, destination_id, departure_date, max_travel_time, max_stops))
    rows = cursor.fetchall()
    display_results(rows)




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


def setup_query_tab(frame):
    tk.Button(frame, text="Find Flights by Route", command=lambda: ask_route_and_query()).pack()

def ask_route_and_query():
    origin_id = simpledialog.askinteger("Origin", "Enter origin spaceport ID:")
    if origin_id is None:
        return
    dest_id = simpledialog.askinteger("Destination", "Enter destination spaceport ID:")
    if dest_id is None:
        return
    get_flights_by_route(db.cursor(), origin_id, dest_id)


def setup_planet_form(frame):
    tk.Label(frame, text="Planet Name").grid(row=0, column=0)
    planet_name_entry = tk.Entry(frame)
    planet_name_entry.grid(row=0, column=1)

    tk.Label(frame, text="Size").grid(row=1, column=0)
    size_entry = tk.Entry(frame)
    size_entry.grid(row=1, column=1)

    tk.Label(frame, text="Population").grid(row=2, column=0)
    population_entry = tk.Entry(frame)
    population_entry.grid(row=2, column=1)

    def submit_planet():
        name = planet_name_entry.get()
        size = int(size_entry.get())
        pop = int(population_entry.get())
        enter_planet(db.cursor(), name, size, pop)

    tk.Button(frame, text="Add Planet", command=submit_planet).grid(row=3, columnspan=2)

def setup_spacestation_form(frame):
    row = 5  # adjust based on layout

    tk.Label(frame, text="Station Name").grid(row=row, column=0)
    station_entry = tk.Entry(frame)
    station_entry.grid(row=row, column=1)

    tk.Label(frame, text="Planet Associated").grid(row=row+1, column=0)
    planet_entry = tk.Entry(frame)
    planet_entry.grid(row=row+1, column=1)

    tk.Label(frame, text="Capacity Limit").grid(row=row+2, column=0)
    capacity_entry = tk.Entry(frame)
    capacity_entry.grid(row=row+2, column=1)

    def submit_station():
        name = station_entry.get()
        planet = planet_entry.get() or None
        capacity = int(capacity_entry.get())
        enter_spacestation(db.cursor(), name, None, planet, capacity)

    tk.Button(frame, text="Add Spacestation", command=submit_station).grid(row=row+3, columnspan=2, pady=(5,10))

def setup_spaceport_form(frame):
    row = 10  # adjust to avoid overlap

    tk.Label(frame, text="Port Name").grid(row=row, column=0)
    port_entry = tk.Entry(frame)
    port_entry.grid(row=row, column=1)

    tk.Label(frame, text="Planet Associated").grid(row=row+1, column=0)
    planet_entry = tk.Entry(frame)
    planet_entry.grid(row=row+1, column=1)

    tk.Label(frame, text="Spacestation Name").grid(row=row+2, column=0)
    station_entry = tk.Entry(frame)
    station_entry.grid(row=row+2, column=1)

    tk.Label(frame, text="Fee").grid(row=row+3, column=0)
    fee_entry = tk.Entry(frame)
    fee_entry.grid(row=row+3, column=1)

    tk.Label(frame, text="Capacity").grid(row=row+4, column=0)
    capacity_entry = tk.Entry(frame)
    capacity_entry.grid(row=row+4, column=1)

    def submit_spaceport():
        port = port_entry.get()
        planet = planet_entry.get() or None
        station = station_entry.get() or None
        fee = int(fee_entry.get())
        capacity = int(capacity_entry.get())
        enter_spaceport(db.cursor(), port, planet, station, fee, capacity)

    tk.Button(frame, text="Add Spaceport", command=submit_spaceport).grid(row=row+5, columnspan=2, pady=(5,10))

def setup_spacecraft_form(frame):
    row = 15

    tk.Label(frame, text="Type Name").grid(row=row, column=0)
    type_entry = tk.Entry(frame)
    type_entry.grid(row=row, column=1)

    tk.Label(frame, text="Capacity").grid(row=row+1, column=0)
    capacity_entry = tk.Entry(frame)
    capacity_entry.grid(row=row+1, column=1)

    tk.Label(frame, text="Range").grid(row=row+2, column=0)
    range_entry = tk.Entry(frame)
    range_entry.grid(row=row+2, column=1)

    def submit_spacecraft():
        type_name = type_entry.get()
        capacity = int(capacity_entry.get())
        range_val = int(range_entry.get())
        enter_spacecraft(db.cursor(), type_name, capacity, range_val)

    tk.Button(frame, text="Add Spacecraft", command=submit_spacecraft).grid(row=row+3, columnspan=2, pady=(5,10))

def setup_route_form(frame):
    row = 20

    tk.Label(frame, text="Origin Port ID").grid(row=row, column=0)
    origin_entry = tk.Entry(frame)
    origin_entry.grid(row=row, column=1)

    tk.Label(frame, text="Destination Port ID").grid(row=row+1, column=0)
    dest_entry = tk.Entry(frame)
    dest_entry.grid(row=row+1, column=1)

    tk.Label(frame, text="Distance").grid(row=row+2, column=0)
    distance_entry = tk.Entry(frame)
    distance_entry.grid(row=row+2, column=1)

    def submit_route():
        origin_id = int(origin_entry.get())
        dest_id = int(dest_entry.get())
        distance = int(distance_entry.get())
        enter_route(db.cursor(), origin_id, dest_id, distance)

    tk.Button(frame, text="Add Route", command=submit_route).grid(row=row+3, columnspan=2, pady=(5,10))

def setup_flight_form(frame):
    tk.Label(frame, text="Flight Number").grid(row=0, column=0)
    flight_number_entry = tk.Entry(frame)
    flight_number_entry.grid(row=0, column=1)

    tk.Label(frame, text="Route ID").grid(row=1, column=0)
    route_id_entry = tk.Entry(frame)
    route_id_entry.grid(row=1, column=1)

    tk.Label(frame, text="Spacecraft Type").grid(row=2, column=0)
    spacecraft_type_entry = tk.Entry(frame)
    spacecraft_type_entry.grid(row=2, column=1)

    tk.Label(frame, text="Departure Day").grid(row=3, column=0)
    day_entry = tk.Entry(frame)
    day_entry.grid(row=3, column=1)

    tk.Label(frame, text="Departure Time (HH:MM)").grid(row=4, column=0)
    time_entry = tk.Entry(frame)
    time_entry.grid(row=4, column=1)

    tk.Label(frame, text="Flight Duration").grid(row=5, column=0)
    duration_entry = tk.Entry(frame)
    duration_entry.grid(row=5, column=1)

    def submit_flight():
        flight_number = flight_number_entry.get()
        route_id = int(route_id_entry.get())
        spacecraft_type = spacecraft_type_entry.get()
        day = day_entry.get()
        time = time_entry.get()
        duration = float(duration_entry.get())

        enter_flight(db.cursor(), flight_number, route_id, spacecraft_type, day, time, duration)

    tk.Button(frame, text="Add Flight", command=submit_flight).grid(row=6, columnspan=2)


notebook = ttk.Notebook(root)
notebook.pack(expand=1, fill="both")

insert_tab = ttk.Frame(notebook)
query_tab = ttk.Frame(notebook)

notebook.add(insert_tab, text="Insert Data")
notebook.add(query_tab, text="Queries")

frame = tk.Frame(root)
frame.pack(pady=10)

tk.Label(frame, text="Query Functions", font=("Arial", 14)).pack()

tk.Button(frame, text="Find Ports with Flights (by Name)",
          command=lambda: get_port_by_port_name_with_flights(db.cursor(), simpledialog.askstring("Port", "Enter port name:"))
).pack(pady=2)

tk.Button(frame, text="Departures by Port + Date Range",
          command=lambda: get_departures_by_date_range_and_port(
              db.cursor(),
              simpledialog.askstring("Start Day", "Enter start day (e.g., Monday):"),
              simpledialog.askstring("End Day", "Enter end day (e.g., Friday):"),
              simpledialog.askstring("Port", "Enter port name:")
          )
).pack(pady=2)

tk.Button(frame, text="Arrivals by Port + Date Range",
          command=lambda: get_arrivals_by_date_range_and_port(
              db.cursor(),
              simpledialog.askstring("Start Day", "Enter start day (e.g., Monday):"),
              simpledialog.askstring("End Day", "Enter end day (e.g., Friday):"),
              simpledialog.askstring("Port", "Enter port name:")
          )
).pack(pady=2)

tk.Button(frame, text="Flights Between Ports",
          command=lambda: get_flights_by_route(
              db.cursor(),
              simpledialog.askinteger("Origin ID", "Enter origin spaceport ID:"),
              simpledialog.askinteger("Destination ID", "Enter destination spaceport ID:")
          )
).pack(pady=2)

tk.Button(frame, text="Flight Finder",
          command=lambda: flight_finder(
              db.cursor(),
              simpledialog.askstring("Departure Day", "Enter departure day:"),
              simpledialog.askinteger("Origin ID", "Enter origin ID:"),
              simpledialog.askinteger("Destination ID", "Enter destination ID:"),
              simpledialog.askfloat("Max Duration", "Enter max travel time (hours):"),
              simpledialog.askinteger("Max Stops", "Enter max number of stops:")
          )
).pack(pady=2)

setup_planet_form(insert_tab)
setup_spacestation_form(insert_tab)
setup_spaceport_form(insert_tab)
setup_spacecraft_form(insert_tab)
setup_route_form(insert_tab)
setup_flight_form(insert_tab)
setup_query_tab(query_tab)


root.mainloop()