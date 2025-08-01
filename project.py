import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                               QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, 
                               QLineEdit, QPushButton, QMessageBox, QInputDialog,
                               QTextEdit, QScrollArea, QFrame, QGroupBox)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QPalette, QColor
import mysql.connector
import json
import re

class SpaceTravelDB(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_database()
        self.init_ui()
        
    def init_database(self):
        """Initialize database connection"""
        try:
            with open("credentials.json", "r") as file:
                credentials = json.load(file)

            self.db = mysql.connector.connect(
                host="localhost",
                user=credentials["user"],
                password=credentials["password"],
                database="dbproject"
            )
            self.create_nonexisting_tables()
        except Exception as e:
            QMessageBox.critical(None, "Connection Error", f"Failed to connect to database:\n{e}")
            sys.exit()

    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Space Travel Database")
        self.setMinimumSize(800, 600)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QTabWidget::pane {
                border: 1px solid #c0c0c0;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e0e0e0;
                padding: 8px 16px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #0078d4;
            }
            QPushButton {
                background-color: #0078d4;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #106ebe;
            }
            QPushButton:pressed {
                background-color: #005a9e;
            }
            QLineEdit {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        central_widget_layout = QVBoxLayout(central_widget)
        central_widget_layout.addWidget(self.tab_widget)
        
        # Create tabs
        self.create_insert_tab()
        self.create_query_tab()
        
    def create_insert_tab(self):
        """Create the data insertion tab"""
        insert_tab = QWidget()
        self.tab_widget.addTab(insert_tab, "Insert Data")
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll.setWidget(scroll_widget)
        
        layout = QVBoxLayout(insert_tab)
        layout.addWidget(scroll)
        
        main_layout = QVBoxLayout(scroll_widget)
        
        # Create forms for each entity
        self.create_planet_form(main_layout)
        self.create_spacestation_form(main_layout)
        self.create_spaceport_form(main_layout)
        self.create_spacecraft_form(main_layout)
        self.create_route_form(main_layout)
        self.create_flight_form(main_layout)
        
        main_layout.addStretch()
        
    def create_query_tab(self):
        """Create the query tab"""
        query_tab = QWidget()
        self.tab_widget.addTab(query_tab, "Queries")
        
        layout = QVBoxLayout(query_tab)
        
        # Title
        title = QLabel("Query Functions")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Query buttons
        buttons_layout = QVBoxLayout()
        
        btn1 = QPushButton("Find Ports with Flights (by Name)")
        btn1.clicked.connect(self.query_ports_with_flights)
        buttons_layout.addWidget(btn1)
        
        btn2 = QPushButton("Departures by Port + Date Range")
        btn2.clicked.connect(self.query_departures_by_date_range)
        buttons_layout.addWidget(btn2)
        
        btn3 = QPushButton("Arrivals by Port + Date Range")
        btn3.clicked.connect(self.query_arrivals_by_date_range)
        buttons_layout.addWidget(btn3)
        
        btn4 = QPushButton("Flights Between Ports")
        btn4.clicked.connect(self.query_flights_by_route)
        buttons_layout.addWidget(btn4)
        
        btn5 = QPushButton("Flight Finder")
        btn5.clicked.connect(self.query_flight_finder)
        buttons_layout.addWidget(btn5)
        
        layout.addLayout(buttons_layout)
        layout.addStretch()

    def create_planet_form(self, parent_layout):
        """Create planet input form"""
        group = QGroupBox("Add Planet")
        layout = QGridLayout(group)
        
        layout.addWidget(QLabel("Planet Name:"), 0, 0)
        self.planet_name_entry = QLineEdit()
        layout.addWidget(self.planet_name_entry, 0, 1)
        
        layout.addWidget(QLabel("Size:"), 1, 0)
        self.planet_size_entry = QLineEdit()
        layout.addWidget(self.planet_size_entry, 1, 1)
        
        layout.addWidget(QLabel("Population:"), 2, 0)
        self.planet_population_entry = QLineEdit()
        layout.addWidget(self.planet_population_entry, 2, 1)
        
        submit_btn = QPushButton("Add Planet")
        submit_btn.clicked.connect(self.submit_planet)
        layout.addWidget(submit_btn, 3, 0, 1, 2)
        
        parent_layout.addWidget(group)

    def create_spacestation_form(self, parent_layout):
        """Create spacestation input form"""
        group = QGroupBox("Add Space Station")
        layout = QGridLayout(group)
        
        layout.addWidget(QLabel("Station Name:"), 0, 0)
        self.station_name_entry = QLineEdit()
        layout.addWidget(self.station_name_entry, 0, 1)
        
        layout.addWidget(QLabel("Planet Associated:"), 1, 0)
        self.station_planet_entry = QLineEdit()
        layout.addWidget(self.station_planet_entry, 1, 1)
        
        layout.addWidget(QLabel("Capacity Limit:"), 2, 0)
        self.station_capacity_entry = QLineEdit()
        layout.addWidget(self.station_capacity_entry, 2, 1)
        
        submit_btn = QPushButton("Add Space Station")
        submit_btn.clicked.connect(self.submit_spacestation)
        layout.addWidget(submit_btn, 3, 0, 1, 2)
        
        parent_layout.addWidget(group)

    def create_spaceport_form(self, parent_layout):
        """Create spaceport input form"""
        group = QGroupBox("Add Spaceport")
        layout = QGridLayout(group)
        
        layout.addWidget(QLabel("Port Name:"), 0, 0)
        self.port_name_entry = QLineEdit()
        layout.addWidget(self.port_name_entry, 0, 1)
        
        layout.addWidget(QLabel("Planet Associated:"), 1, 0)
        self.port_planet_entry = QLineEdit()
        layout.addWidget(self.port_planet_entry, 1, 1)
        
        layout.addWidget(QLabel("Station Name:"), 2, 0)
        self.port_station_entry = QLineEdit()
        layout.addWidget(self.port_station_entry, 2, 1)
        
        layout.addWidget(QLabel("Fee:"), 3, 0)
        self.port_fee_entry = QLineEdit()
        layout.addWidget(self.port_fee_entry, 3, 1)
        
        layout.addWidget(QLabel("Capacity:"), 4, 0)
        self.port_capacity_entry = QLineEdit()
        layout.addWidget(self.port_capacity_entry, 4, 1)
        
        submit_btn = QPushButton("Add Spaceport")
        submit_btn.clicked.connect(self.submit_spaceport)
        layout.addWidget(submit_btn, 5, 0, 1, 2)
        
        parent_layout.addWidget(group)

    def create_spacecraft_form(self, parent_layout):
        """Create spacecraft input form"""
        group = QGroupBox("Add Spacecraft")
        layout = QGridLayout(group)
        
        layout.addWidget(QLabel("Type Name:"), 0, 0)
        self.craft_type_entry = QLineEdit()
        layout.addWidget(self.craft_type_entry, 0, 1)
        
        layout.addWidget(QLabel("Capacity:"), 1, 0)
        self.craft_capacity_entry = QLineEdit()
        layout.addWidget(self.craft_capacity_entry, 1, 1)
        
        layout.addWidget(QLabel("Range:"), 2, 0)
        self.craft_range_entry = QLineEdit()
        layout.addWidget(self.craft_range_entry, 2, 1)
        
        submit_btn = QPushButton("Add Spacecraft")
        submit_btn.clicked.connect(self.submit_spacecraft)
        layout.addWidget(submit_btn, 3, 0, 1, 2)
        
        parent_layout.addWidget(group)

    def create_route_form(self, parent_layout):
        """Create route input form"""
        group = QGroupBox("Add Route")
        layout = QGridLayout(group)
        
        layout.addWidget(QLabel("Origin Port ID:"), 0, 0)
        self.route_origin_entry = QLineEdit()
        layout.addWidget(self.route_origin_entry, 0, 1)
        
        layout.addWidget(QLabel("Destination Port ID:"), 1, 0)
        self.route_dest_entry = QLineEdit()
        layout.addWidget(self.route_dest_entry, 1, 1)
        
        layout.addWidget(QLabel("Distance:"), 2, 0)
        self.route_distance_entry = QLineEdit()
        layout.addWidget(self.route_distance_entry, 2, 1)
        
        submit_btn = QPushButton("Add Route")
        submit_btn.clicked.connect(self.submit_route)
        layout.addWidget(submit_btn, 3, 0, 1, 2)
        
        parent_layout.addWidget(group)

    def create_flight_form(self, parent_layout):
        """Create flight input form"""
        group = QGroupBox("Add Flight")
        layout = QGridLayout(group)
        
        layout.addWidget(QLabel("Flight Number:"), 0, 0)
        self.flight_number_entry = QLineEdit()
        layout.addWidget(self.flight_number_entry, 0, 1)
        
        layout.addWidget(QLabel("Route ID:"), 1, 0)
        self.flight_route_entry = QLineEdit()
        layout.addWidget(self.flight_route_entry, 1, 1)
        
        layout.addWidget(QLabel("Spacecraft Type:"), 2, 0)
        self.flight_craft_entry = QLineEdit()
        layout.addWidget(self.flight_craft_entry, 2, 1)
        
        layout.addWidget(QLabel("Departure Day:"), 3, 0)
        self.flight_day_entry = QLineEdit()
        layout.addWidget(self.flight_day_entry, 3, 1)
        
        layout.addWidget(QLabel("Departure Time (HH:MM):"), 4, 0)
        self.flight_time_entry = QLineEdit()
        layout.addWidget(self.flight_time_entry, 4, 1)
        
        layout.addWidget(QLabel("Flight Duration:"), 5, 0)
        self.flight_duration_entry = QLineEdit()
        layout.addWidget(self.flight_duration_entry, 5, 1)
        
        submit_btn = QPushButton("Add Flight")
        submit_btn.clicked.connect(self.submit_flight)
        layout.addWidget(submit_btn, 6, 0, 1, 2)
        
        parent_layout.addWidget(group)

    # Submit methods
    def submit_planet(self):
        try:
            name = self.planet_name_entry.text()
            size = int(self.planet_size_entry.text())
            population = int(self.planet_population_entry.text())
            
            if self.enter_planet(name, size, population):
                self.clear_planet_form()
                QMessageBox.information(self, "Success", "Planet added successfully!")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values.")

    def submit_spacestation(self):
        try:
            name = self.station_name_entry.text()
            planet = self.station_planet_entry.text() or None
            capacity = int(self.station_capacity_entry.text())
            
            if self.enter_spacestation(name, None, planet, capacity):
                self.clear_spacestation_form()
                QMessageBox.information(self, "Success", "Space station added successfully!")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values.")

    def submit_spaceport(self):
        try:
            name = self.port_name_entry.text()
            planet = self.port_planet_entry.text() or None
            station = self.port_station_entry.text() or None
            fee = int(self.port_fee_entry.text())
            capacity = int(self.port_capacity_entry.text())
            
            if self.enter_spaceport(name, planet, station, fee, capacity):
                self.clear_spaceport_form()
                QMessageBox.information(self, "Success", "Spaceport added successfully!")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values.")

    def submit_spacecraft(self):
        try:
            type_name = self.craft_type_entry.text()
            capacity = int(self.craft_capacity_entry.text())
            range_val = int(self.craft_range_entry.text())
            
            if self.enter_spacecraft(type_name, capacity, range_val):
                self.clear_spacecraft_form()
                QMessageBox.information(self, "Success", "Spacecraft added successfully!")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values.")

    def submit_route(self):
        try:
            origin = int(self.route_origin_entry.text())
            dest = int(self.route_dest_entry.text())
            distance = int(self.route_distance_entry.text())
            
            if self.enter_route(origin, dest, distance):
                self.clear_route_form()
                QMessageBox.information(self, "Success", "Route added successfully!")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values.")

    def submit_flight(self):
        try:
            number = self.flight_number_entry.text()
            route_id = int(self.flight_route_entry.text())
            craft_type = self.flight_craft_entry.text()
            days_raw = self.flight_day_entry.text()
            time = self.flight_time_entry.text()
            duration = float(self.flight_duration_entry.text())

            raw_time = self.flight_time_entry.text().strip()
            try:
                mysql_time = self.parse_time(raw_time)
            except ValueError as e:
                QMessageBox.critical(self, "Invalid Time", str(e))
                return
            # pass mysql_time into enter_flight instead of raw_time
            if self.enter_flight(number, route_id, craft_type, days_raw, mysql_time, duration):
                self.clear_flight_form()
                QMessageBox.information(self, "Success", "Flight added successfully!")
        except ValueError:
            QMessageBox.warning(self, "Invalid Input", "Please enter valid numeric values.")

    # Clear form methods
    def clear_planet_form(self):
        self.planet_name_entry.clear()
        self.planet_size_entry.clear()
        self.planet_population_entry.clear()

    def clear_spacestation_form(self):
        self.station_name_entry.clear()
        self.station_planet_entry.clear()
        self.station_capacity_entry.clear()

    def clear_spaceport_form(self):
        self.port_name_entry.clear()
        self.port_planet_entry.clear()
        self.port_station_entry.clear()
        self.port_fee_entry.clear()
        self.port_capacity_entry.clear()

    def clear_spacecraft_form(self):
        self.craft_type_entry.clear()
        self.craft_capacity_entry.clear()
        self.craft_range_entry.clear()

    def clear_route_form(self):
        self.route_origin_entry.clear()
        self.route_dest_entry.clear()
        self.route_distance_entry.clear()

    def clear_flight_form(self):
        self.flight_number_entry.clear()
        self.flight_route_entry.clear()
        self.flight_craft_entry.clear()
        self.flight_day_entry.clear()
        self.flight_time_entry.clear()
        self.flight_duration_entry.clear()

    # Query methods
    def query_ports_with_flights(self):
        port_name, ok = QInputDialog.getText(self, "Query", "Enter port name:")
        if ok and port_name:
            self.get_port_by_port_name_with_flights(port_name)

    def query_departures_by_date_range(self):
        start_day, ok1 = QInputDialog.getText(self, "Query", "Enter start day (e.g., Monday):")
        if not ok1: return
        end_day, ok2 = QInputDialog.getText(self, "Query", "Enter end day (e.g., Friday):")
        if not ok2: return
        port_name, ok3 = QInputDialog.getText(self, "Query", "Enter port name:")
        if ok3 and all([start_day, end_day, port_name]):
            self.get_departures_by_date_range_and_port(start_day, end_day, port_name)

    def query_arrivals_by_date_range(self):
        start_day, ok1 = QInputDialog.getText(self, "Query", "Enter start day (e.g., Monday):")
        if not ok1: return
        end_day, ok2 = QInputDialog.getText(self, "Query", "Enter end day (e.g., Friday):")
        if not ok2: return
        port_name, ok3 = QInputDialog.getText(self, "Query", "Enter port name:")
        if ok3 and all([start_day, end_day, port_name]):
            self.get_arrivals_by_date_range_and_port(start_day, end_day, port_name)

    def query_flights_by_route(self):
        origin_id, ok1 = QInputDialog.getInt(self, "Query", "Enter origin spaceport ID:")
        if not ok1: return
        dest_id, ok2 = QInputDialog.getInt(self, "Query", "Enter destination spaceport ID:")
        if ok2:
            self.get_flights_by_route(origin_id, dest_id)

    def query_flight_finder(self):
        dep_day, ok1 = QInputDialog.getText(self, "Query", "Enter departure day:")
        if not ok1: return
        origin_id, ok2 = QInputDialog.getInt(self, "Query", "Enter origin ID:")
        if not ok2: return
        dest_id, ok3 = QInputDialog.getInt(self, "Query", "Enter destination ID:")
        if not ok3: return
        max_time, ok4 = QInputDialog.getDouble(self, "Query", "Enter max travel time (hours):")
        if not ok4: return
        max_stops, ok5 = QInputDialog.getInt(self, "Query", "Enter max number of stops:")
        if ok5:
            self.flight_finder(dep_day, origin_id, dest_id, max_time, max_stops)

    # Database methods (keeping the original logic)
    def create_planet_table(self, cursor):
        cursor.execute("""
        CREATE TABLE planets (
        planet_name VARCHAR(50) NOT NULL UNIQUE,
        size BIGINT NOT NULL,
        population BIGINT NOT NULL,
        PRIMARY KEY (planet_name)
        )
        """)
        self.db.commit()

    def create_spacestation_table(self, cursor):
        cursor.execute("""
        CREATE TABLE spacestations (
            station_name VARCHAR(50) NOT NULL PRIMARY KEY,
            planet_associated VARCHAR(50) DEFAULT NULL,
            capacity_limit INT NOT NULL,
                FOREIGN KEY (planet_associated) REFERENCES planets(planet_name)
        )
        """)
        self.db.commit()

    def create_spaceports_table(self, cursor):
        cursor.execute("""
        CREATE TABLE spaceports (
            spaceport_id INT PRIMARY KEY AUTO_INCREMENT,
            port_name VARCHAR(100) NOT NULL,
            planet_name VARCHAR(50) NULL,
            station_name VARCHAR(50) NULL,
            capacity INT NOT NULL,
            fee INT NOT NULL,
            FOREIGN KEY (planet_name) REFERENCES planets(planet_name),
            FOREIGN KEY (station_name) REFERENCES spacestations(station_name),
            UNIQUE KEY uq_station (station_name),
            UNIQUE KEY uq_planet_port (planet_name, port_name),
            CONSTRAINT chk_spaceport_capacity CHECK (capacity > 0),
            CONSTRAINT chk_spaceport_fee CHECK (fee >= 0)
        )
        """)
        self.db.commit()

    def create_spacecrafts_table(self, cursor):
        cursor.execute("""
        CREATE TABLE spacecrafts (
        type_name VARCHAR(100) PRIMARY KEY,
        capacity  INT NOT NULL,
        max_range     INT NOT NULL,
        CONSTRAINT chk_sc_capacity CHECK (capacity > 0),
        CONSTRAINT chk_sc_range    CHECK (max_range > 0)
        )
        """)
        self.db.commit()

    def create_routes_table(self, cursor):
        cursor.execute("""
        CREATE TABLE routes (
            route_id INT PRIMARY KEY AUTO_INCREMENT,
            origin_id INT NOT NULL,
            dest_id INT NOT NULL,
            dist INT NOT NULL,
            FOREIGN KEY (origin_id) REFERENCES spaceports(spaceport_id),
            FOREIGN KEY (dest_id) REFERENCES spaceports(spaceport_id),
            CONSTRAINT chk_route_distance CHECK (dist > 0)
        )
        """)
        self.db.commit()

    def create_flight_table(self, cursor):
        cursor.execute("""
        CREATE TABLE flights (
        flight_number   VARCHAR(20) PRIMARY KEY,
        route_id        INT NOT NULL,
        spacecraft_type VARCHAR(100) NOT NULL,
        departure_time TIME NOT NULL,
        flight_duration DECIMAL(4,2) NOT NULL,
        FOREIGN KEY (route_id) REFERENCES routes(route_id),
        FOREIGN KEY (spacecraft_type) REFERENCES spacecrafts(type_name),
        CONSTRAINT chk_flight_duration CHECK (flight_duration > 0)
        )
        """)
        self.db.commit()

    def create_flight_schedule_table(self, cursor):
        cursor.execute("""
        CREATE TABLE flight_schedule (
            flight_number VARCHAR(20) NOT NULL,
            day_of_week   ENUM(
                'Monday','Tuesday','Wednesday',
                'Thursday','Friday','Saturday','Sunday'
            ) NOT NULL,
            PRIMARY KEY (flight_number, day_of_week),
            FOREIGN KEY (flight_number) REFERENCES flights(flight_number)
        )
        """)
        self.db.commit()

    def parse_time(self, time_str):
        """
        Accepts 'HH:MM' or 'HH:MM:SS' (or even 'YYYY-MM-DD HH:MM:SS').
        Returns a string 'HH:MM:SS' suitable for MySQL TIME.
        """
        # strip date if present
        if ' ' in time_str:
            time_part = time_str.split(' ')[1]
        else:
            time_part = time_str

        parts = time_part.split(':')
        if len(parts) == 2:
            hh, mm = parts
            ss = '00'
        elif len(parts) == 3:
            hh, mm, ss = parts
        else:
            raise ValueError(f"Unrecognized time format: {time_str}")

        # zero-pad and validate ranges
        hh, mm, ss = hh.zfill(2), mm.zfill(2), ss.zfill(2)
        return f"{hh}:{mm}:{ss}"


    def enter_planet(self, planet_name, size, population):
        if not planet_name.strip():
            QMessageBox.critical(self, "Validation Error", "Planet name cannot be empty.")
            return False
        if not isinstance(size, int) or size <= 0:
            QMessageBox.critical(self, "Validation Error", "Planet size must be a positive integer.")
            return False
        if not isinstance(population, int) or population < 0:
            QMessageBox.critical(self, "Validation Error", "Population must be a non-negative integer.")
            return False

        sql = """INSERT INTO planets VALUES (%s, %s, %s)"""
        values = [planet_name, size, population]
        return self.confirm_and_commit(sql, values)

    def enter_spacestation(self, station_name, has_spaceport, planet_associated, capacity_limit):
        if not station_name.strip():
            QMessageBox.critical(self, "Validation Error", "Station name cannot be empty.")
            return False
        if planet_associated and not planet_associated.strip():
            QMessageBox.critical(self, "Validation Error", "Planet associated must be a valid string or NULL.")
            return False
        if not isinstance(capacity_limit, int) or capacity_limit <= 0:
            QMessageBox.critical(self, "Validation Error", "Capacity must be a positive integer.")
            return False
        
        cursor = self.db.cursor()
        cursor.execute("SELECT COUNT(*) FROM planets WHERE planet_name = %s", (planet_associated,))

        if planet_associated:
            cursor = self.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM planets WHERE planet_name = %s", (planet_associated,))
            if cursor.fetchone()[0] == 0:
                QMessageBox.critical(self, "Validation Error", f"Planet '{planet_associated}' does not exist.")
                return False

        sql = """INSERT INTO spacestations VALUES (%s, %s, %s)"""
        values = [station_name, planet_associated, capacity_limit]
        return self.confirm_and_commit(sql, values)

    def enter_spaceport(self, port_name, planet_associated, spacestation_name, fee, capacity):
        if not port_name.strip():
            QMessageBox.critical(self, "Validation Error", "Port name cannot be empty.")
            return False
        if planet_associated is None and spacestation_name is None:
            QMessageBox.critical(self, "Validation Error", "Must be owned by either a planet or a spacestation.")
            return False
        if not isinstance(fee, int) or fee < 0:
            QMessageBox.critical(self, "Validation Error", "Fee must be a non-negative integer.")
            return False
        if not isinstance(capacity, int) or capacity <= 0:
            QMessageBox.critical(self, "Validation Error", "Capacity must be a positive integer.")
            return False
        if planet_associated is None and spacestation_name is not None:
            if port_name != spacestation_name:
                QMessageBox.critical(self, "Validation Error", "Port name must match station name if owned by a spacestation.")
                return False
        if planet_associated and spacestation_name:
            QMessageBox.critical(self, "Validation Error", "A spaceport cannot belong to both a planet and a station.")
            return False

        cursor = self.db.cursor()
        if planet_associated:
            cursor.execute("SELECT COUNT(*) FROM planets WHERE planet_name = %s", (planet_associated,))
            if cursor.fetchone()[0] == 0:
                QMessageBox.critical(self, "Validation Error", f"Planet '{planet_associated}' does not exist.")
                return False

        if spacestation_name:
            cursor.execute("SELECT COUNT(*) FROM spacestations WHERE station_name = %s", (spacestation_name,))
            if cursor.fetchone()[0] == 0:
                QMessageBox.critical(self, "Validation Error", f"Station '{spacestation_name}' does not exist.")
                return False

        sql = """INSERT INTO spaceports (port_name, planet_name, station_name, fee, capacity) VALUES (%s, %s, %s, %s, %s)"""
        values = [port_name, planet_associated, spacestation_name, fee, capacity]
        return self.confirm_and_commit(sql, values)

    def enter_spacecraft(self, type_name, capacity, range):
        if not type_name.strip():
            QMessageBox.critical(self, "Validation Error", "Type name cannot be empty.")
            return False
        if not isinstance(capacity, int) or capacity <= 0:
            QMessageBox.critical(self, "Validation Error", "Capacity must be a positive integer.")
            return False
        if not isinstance(range, int) or range <= 0:
            QMessageBox.critical(self, "Validation Error", "Range must be a positive integer.")
            return False

        sql = """INSERT INTO spacecrafts VALUES (%s, %s, %s)"""
        values = [type_name, capacity, range]
        return self.confirm_and_commit(sql, values)

    def enter_flight(self, flight_number, route_id, spacecraft_type, days_raw, departure_time, flight_duration):
        # Validate flight number
        if not flight_number.strip():
            QMessageBox.critical(self, "Validation Error", "Flight number cannot be empty.")
            return False

        # Validate duration
        try:
            duration_val = float(flight_duration)
            if duration_val <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.critical(self, "Validation Error", "Flight duration must be a positive number.")
            return False

        cursor = self.db.cursor()
        # Validate route exists
        cursor.execute("SELECT COUNT(*) FROM routes WHERE route_id = %s", (route_id,))
        if cursor.fetchone()[0] == 0:
            QMessageBox.critical(self, "Validation Error", f"Route ID {route_id} does not exist.")
            return False

        # Validate spacecraft type exists
        cursor.execute("SELECT COUNT(*) FROM spacecrafts WHERE type_name = %s", (spacecraft_type,))
        if cursor.fetchone()[0] == 0:
            QMessageBox.critical(self, "Validation Error", f"Spacecraft type '{spacecraft_type}' does not exist.")
            return False

        # Validate time format
        if not re.match(r"^\d{2}:\d{2}(:\d{2})?$", departure_time):
            QMessageBox.critical(self, "Validation Error", "Invalid time format.")
            return False

        # Insert base flight record
        sql_flight = (
            "INSERT INTO flights"
            "(flight_number, route_id, spacecraft_type, departure_time, flight_duration)"
            " VALUES (%s, %s, %s, %s, %s)"
        )
        flight_vals = [flight_number, route_id, spacecraft_type, departure_time, duration_val]
        if not self.confirm_and_commit(sql_flight, flight_vals):
            return False

        # Parse and insert schedule entries
        days = [d.strip() for d in days_raw.split(',')]
        valid_days = {"Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"}
        try:
            for day in days:
                if day not in valid_days:
                    raise ValueError(f"Invalid day: {day}")
                cursor.execute(
                    "INSERT INTO flight_schedule (flight_number, day_of_week) VALUES (%s, %s)",
                    (flight_number, day)
                )
            self.db.commit()
        except ValueError as ve:
            QMessageBox.critical(self, "Validation Error", str(ve))
            self.db.rollback()
            return False
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error scheduling days: {err}")
            self.db.rollback()
            return False

        return True


    # Query methods
    def get_port_by_port_name_with_flights(self, port_name):
        cursor = self.db.cursor()
        sql = """
            SELECT DISTINCT
                CASE WHEN r.origin_id = sp.spaceport_id THEN r.dest_id ELSE r.origin_id END AS other_port_id,
                sp2.port_name AS other_port_name
            FROM spaceports sp
            JOIN routes r ON sp.spaceport_id IN (r.origin_id, r.dest_id)
            JOIN spaceports sp2
            ON sp2.spaceport_id = CASE WHEN r.origin_id = sp.spaceport_id
                                        THEN r.dest_id
                                        ELSE r.origin_id END
            WHERE sp.port_name = %s;
        """
        cursor.execute(sql, (port_name,))
        rows = cursor.fetchall()
        self.display_results(rows, "Connected Ports")

    def get_departures_by_date_range_and_port(self, start_date, end_date, port_name):
        cursor = self.db.cursor()
        sql = """
            SELECT f.flight_number, fs.day_of_week, f.departure_time, f.flight_duration
            FROM flights f
            JOIN flight_schedule fs
            ON f.flight_number = fs.flight_number
            JOIN routes r
            ON f.route_id = r.route_id
            JOIN spaceports sp
            ON r.origin_id = sp.spaceport_id
            WHERE sp.port_name = %s
            AND fs.day_of_week BETWEEN %s AND %s
            ORDER BY
            FIELD(fs.day_of_week,
                    'Monday','Tuesday','Wednesday','Thursday',
                    'Friday','Saturday','Sunday'),
            f.departure_time;
        """
        cursor.execute(sql, (port_name, start_date, end_date))
        rows = cursor.fetchall()
        self.display_results(rows, "Departures")

    def get_arrivals_by_date_range_and_port(self, start_date, end_date, port_name):
        cursor = self.db.cursor()
        sql = """
            SELECT f.flight_number, fs.day_of_week, f.departure_time, f.flight_duration
            FROM flights f
            JOIN flight_schedule fs ON f.flight_number = fs.flight_number
            JOIN routes r ON f.route_id = r.route_id
            JOIN spaceports sp ON r.dest_id = sp.spaceport_id
            WHERE sp.port_name = %s
            AND fs.day_of_week BETWEEN %s AND %s
            ORDER BY
            FIELD(fs.day_of_week,
                    'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'),
            f.departure_time;
        """
        cursor.execute(sql, (port_name, start_date, end_date))
        rows = cursor.fetchall()
        self.display_results(rows, "Arrivals")

    def get_flights_by_route(self, origin_id, destination_id):
        cursor = self.db.cursor()
        sql = """
            SELECT f.flight_number, fs.day_of_week, f.departure_time, f.flight_duration, 
                   sp1.port_name AS origin, sp2.port_name AS destination, r.dist, f.spacecraft_type
            FROM flights f
            JOIN flight_schedule fs ON f.flight_number = fs.flight_number
            JOIN routes r ON f.route_id = r.route_id
            JOIN spaceports sp1 ON r.origin_id = sp1.spaceport_id
            JOIN spaceports sp2 ON r.dest_id   = sp2.spaceport_id
            WHERE r.origin_id = %s AND r.dest_id = %s
            ORDER BY
            FIELD(fs.day_of_week,
                    'Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'),
            f.departure_time;
        """
        cursor.execute(sql, (origin_id, destination_id))
        rows = cursor.fetchall()
        self.display_results(rows, "Flights by Route")

    def flight_finder(self, departure_date, origin_id, destination_id, max_travel_time, max_stops):
        cursor = self.db.cursor()
        sql = """
            SELECT f.flight_number, fs.day_of_week, f.departure_time, f.flight_duration, r.origin_id, r.dest_id, r.dist, f.spacecraft_type
            FROM flights f
            JOIN flight_schedule fs ON f.flight_number = fs.flight_number
            JOIN routes r ON f.route_id = r.route_id
            WHERE r.origin_id       = %s
            AND r.dest_id         = %s
            AND fs.day_of_week    = %s
            AND f.departure_time >= %s
            AND f.departure_time <= ADDTIME(%s, '03:00')
            LIMIT %s;
        """
        cursor.execute(sql, (origin_id, destination_id, departure_date, max_travel_time, max_stops))
        rows = cursor.fetchall()
        self.display_results(rows, "Flight Finder Results")

    def display_results(self, rows, title):
        """Display query results in a new window"""
        result_window = QWidget()
        result_window.setWindowTitle(title)
        result_window.setMinimumSize(600, 400)
        
        layout = QVBoxLayout(result_window)
        
        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Results text area
        text_area = QTextEdit()
        text_area.setReadOnly(True)
        text_area.setFont(QFont("Courier", 10))
        
        if rows:
            for row in rows:
                line = "\t".join(str(col) for col in row)
                text_area.append(line)
        else:
            text_area.append("No results found.")
        
        layout.addWidget(text_area)
        
        # Close button
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(result_window.close)
        layout.addWidget(close_btn)
        
        result_window.show()
        
        # Keep reference to prevent garbage collection
        if not hasattr(self, 'result_windows'):
            self.result_windows = []
        self.result_windows.append(result_window)

    def confirm_and_commit(self, sql, values):
        """Execute query with confirmation"""
        try:
            cursor = self.db.cursor()
            cursor.execute(sql, values)
            
            reply = QMessageBox.question(self, "Confirm", "Do you want to save this entry?",
                                       QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.db.commit()
                return True
            else:
                self.db.rollback()
                return False
                
        except mysql.connector.Error as err:
            QMessageBox.critical(self, "Database Error", f"Error: {err}")
            self.db.rollback()
            return False

    def table_exists(self, cursor, table):
        """Check if table exists"""
        table_name = table.lower()
        cursor.execute("SHOW TABLES")
        existing_tables = cursor.fetchall()
        existing_tables = [x[0] for x in existing_tables]
        return table_name in existing_tables

    def create_nonexisting_tables(self):
        """Create tables if they don't exist"""
        cursor = self.db.cursor()
        
        if not self.table_exists(cursor, "planets"):
            self.create_planet_table(cursor)
        if not self.table_exists(cursor, "spacestations"):
            self.create_spacestation_table(cursor)
        if not self.table_exists(cursor, "spaceports"):
            self.create_spaceports_table(cursor)
        if not self.table_exists(cursor, "spacecrafts"):
            self.create_spacecrafts_table(cursor)
        if not self.table_exists(cursor, "routes"):
            self.create_routes_table(cursor)
        if not self.table_exists(cursor, "flights"):
            self.create_flight_table(cursor)
        if not self.table_exists(cursor, "flight_schedule"):
            self.create_flight_schedule_table(cursor)


    def closeEvent(self, event):
        """Handle application close event"""
        if hasattr(self, 'db'):
            self.db.close()
        event.accept()


def main():
    app = QApplication(sys.argv)
    
    # Set application style
    app.setStyle('Fusion')
    
    # Create and show main window
    window = SpaceTravelDB()
    window.show()
    
    sys.exit(app.exec())


if __name__ == "__main__":
    main()