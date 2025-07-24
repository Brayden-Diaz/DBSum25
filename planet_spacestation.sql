CREATE TABLE planet (
    planet_name VARCHAR(50) NOT NULL,
    size BIGINT NOT NULL,
    population BIGINT NOT NULL,
    PRIMARY KEY (planet_name),
)

CREATE TABLE spacestation (
    station_name VARCHAR(50) NOT NULL,
    planet_associated VARCHAR(50) DEFAULT NULL,
    capacity_limit INT NOT NULL,
    PRIMARY KEY (station_name),
    CONSTRAINT fk_planet
        FOREIGN KEY (planet_associated) REFERENCES planet(planet_name)
)

CREATE TABLE spaceport (
    port_name VARCHAR(50) NOT NULL,
    planet_associated VARCHAR(50) DEFAULT NULL,
    spacestation_name VARCHAR(50) DEFAULT NULL,
    fee INT NOT NULL,
    capacity INT NOT NULL, 
    PRIMARY KEY (planet_associated, port_name),
    CONSTRAINT fk_spacestation
        FOREIGN KEY (spacestation_name) REFERENCES spacestation(station_name),
)