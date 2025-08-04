# Logic Differences: Python + MySQL → TS/React/Vite/Node/Express

---

## 🔧 Adding Data: Logic Differences

| Entity           | Old (Python + MySQL)                              | New (TS/Express + MySQL)                                      |
|------------------|---------------------------------------------------|---------------------------------------------------------------|
| **Planets**       | Direct SQL inserts using raw input               | REST POST `/api/planets` with validation and JSON body        |
| **Spacestations** | Basic insert with foreign key to planet          | REST POST, adds `planet_owner`, uses named FK constraints     |
| **Spaceports**    | Insert via script, manual fee/capacity logic     | REST POST, includes `fee` and `capacity` validation, ties to either a spacestation or planet |
| **Spacecrafts**   | Inserted via test scripts                        | Structured API endpoint with body validation                  |
| **Routes**        | Assumed spaceports exist, no range validation    | REST POST validates distance; backend checks spacecraft compatibility |
| **Flights**       | Simple insert, user selects all values manually  | REST POST verifies route + spacecraft; validates all required fields |

The web version abstracts DB logic behind a typed API layer and performs **input validation**, improving reliability and reusability.

---

## Query Features: Logic Differences

| Feature           | Old Python Version                               | New Web Version                                              |
|------------------|---------------------------------------------------|-------------------------------------------------------------|
| **RouteQuery**    | CLI input for source & destination ports         | API `/api/query/routeQuery`: queries routes using `origin_port_name` and `destination_port_name` |
| **SpaceportQuery**| SQL script with hardcoded filters                | API `/api/query/spaceportQuery`: returns flights arriving/departing from a spaceport + filters by day |
| **FlightFinder**  | Limited logic, brute-force queries               | Complex route-finding algorithm with:<br>• max stops<br>• layover windows (1–6 hrs)<br>• total travel time<br>• departure window |
| **FlightCreator** | Manual insert with no validation                 | Interactive flow:<br>1. Pick spaceports<br>2. Check if route exists<br>3. Choose valid spacecraft<br>4. Compute fee<br>5. Confirm before insert<br>6. Abort without changes if needed |

`FlightFinder` and `FlightCreator` now encapsulate **dynamic logic** that was not possible (or very clunky) in a procedural script.

---

## Key Improvements in New Logic

- **Backend Separation**: Routes modularized by functionality (`/api/query`, `/api/planets`, etc.)
- **Validation Layers**: Every POST endpoint checks for missing/invalid data
- **Flight Creation Logic**:
  - Dynamically creates route if it doesn't exist
  - Checks spacecraft range before allowing selection
  - Calculates fee and confirms user intent before DB mutation
- **Flight Finder Algorithm**:
  - Implements route-chaining and stop validation using timestamps
  - Honors constraints on layover durations, time bounds, and stop limits

---

## Summary

| Area           | Python (Old)                      | TypeScript Web App (New)                  |
|----------------|-----------------------------------|-------------------------------------------|
| Stack          | Python + MySQL                   | React + Vite + Node + Express + MySQL     |
| Interface      | Command-line/manual SQL           | Full web UI + REST APIs                   |
| Validation     | None                              | Robust input validation & error handling  |
| Querying       | Hardcoded / single-layer          | Modular, reusable API logic               |
| Complexity     | Basic business logic              | Real-time multi-step flows with constraints |
| UX             | Manual trial-and-error            | Interactive, error-guarded flow           |

---

# Database Schema Differences

## New Additions in `schema.sql` (DBSummer25):
- **Database Declaration**:
  ```sql
  CREATE DATABASE dbproject;
  USE dbproject;
  ```

- **`spacestations` Table**:
  - New column: `planet_owner`
  - New indexes:
    ```sql
    KEY planet_associated (planet_associated),
    KEY planet_owner (planet_owner)
    ```
  - New foreign key constraints:
    ```sql
    CONSTRAINT spacestations_ibfk_1 FOREIGN KEY (planet_associated) REFERENCES planets (planet_name),
    CONSTRAINT spacestations_ibfk_2 FOREIGN KEY (planet_owner) REFERENCES planets (planet_name)
    ```

- **`spaceports` Table**:
  - Now includes:
    ```sql
    CHECK (capacity > 0)
    ```
