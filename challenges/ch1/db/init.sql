CREATE TABLE IF NOT EXISTS employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(64) NOT NULL UNIQUE,
    password_hash CHAR(64) NOT NULL   -- SHA2-256 hex digest
);

-- Dummy accounts only - purely to make the login form behave like a real
-- application. None of these are required to reach the flag.
INSERT INTO employees (username, password_hash) VALUES
    ('jsmith',  SHA2('CorrectHorseBattery1', 256)),
    ('mchen',   SHA2('SummerRain2024!', 256)),
    ('svance',  SHA2('NovaGrid#Ops9', 256));
