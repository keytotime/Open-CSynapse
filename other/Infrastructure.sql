USE csynapse;
CREATE TABLE Algorithms (identifier VARCHAR(10) NOT NULL, description VARCHAR(100), PRIMARY KEY(identifier));
CREATE TABLE Active (identifier VARCHAR(10), FOREIGN KEY (identifier) REFERENCES Algorithms(identifier));
CREATE TABLE Requests (identifier CHAR(32) NOT NULL, algorithm VARCHAR(10) NOT NULL, computing BOOLEAN DEFAULT 0, complete BOOLEAN DEFAULT 0, return_object LONGTEXT, last_update TIMESTAMP, PRIMARY KEY (identifier, algorithm), FOREIGN KEY (algorithm) REFERENCES Algorithms(identifier));
CREATE TABLE RequestDescription (identifier CHAR(32) NOT NULL, description VARCHAR(200) NOT NULL, PRIMARY KEY (identifier), FOREIGN KEY (identifier) REFERENCES Requests(identifier));