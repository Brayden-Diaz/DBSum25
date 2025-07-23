## Entities & Attributes

1. **Planet**

   * **Primary Key:** planet_name
   * Attributes:

     * size - integer
     * population - integer

2. **SpaceStation**

   * **Primary Key:** station_id
   * Attributes:

     * station_name
     * orbits_planet - boolean
   * **Foreign Key:** planet_name -> Planet

3. **Spaceport**

   * **Primary Key:** composite - spaceport_name, planet_name for planet‑based ports, plus one special port per station
   * Attributes:

     * spaceport_name
     * daily_capacity - integer
     * seat_fee - decimal
   * **Foreign Keys:**

     * planet_name -> Planet

4. **Route**

   * **Primary Key:** composite - from_spaceport, to_spaceport
   * Attributes:

     * distance - integer
   * **Foreign Keys:**

     * from_spaceport -> Spaceport
     * to_spaceport -> Spaceport

5. **SpacecraftType**

   * **Primary Key:** type_name
   * Attributes:

     * capacity - integer
     * range - integer

6. **Flight**

   * **Primary Key:** flight_number
   * Attributes:

     * departure_time - time(24 hours)
     * duration - decimal hours
     * weekdays - set of weekdays
   * **Foreign Keys:**

     * route_id -> Route
     * type_name -> SpacecraftType



## Relationships & Cardinalities

* **Planet - owns -> SpaceStation**

  * 1 Planet : N SpaceStations
* **Planet - owns -> Spaceport** - planetary ports

  * 1 Planet : N Spaceports
* **SpaceStation - has -> Spaceport** - one per station

  * 1 SpaceStation : 1 Spaceport
* **Spaceport <-> connects via Route <-> Spaceport**

  * N Spaceports : N Spaceports through Route
* **Route - isServedBy -> Flight**

  * 1 Route : N Flights
* **SpacecraftType - isUsedBy -> Flight**

  * 1 SpacecraftType : N Flights



## Notes on Constraints

* **Route distance $\leq$ SpacecraftType.range** - enforced when inserting Flights
* **No same‑planet inter‑spaceport routes** - except orbiting‑station exceptions
* **Flights may recur on multiple weekdays**
