CREATE DATABASE IF NOT EXISTS soilsense_db;
USE soilsense_db;

DROP TABLE IF EXISTS pump_operations;
DROP TABLE IF EXISTS nozzles;
DROP TABLE IF EXISTS pumps;
DROP TABLE IF EXISTS pump_models;
DROP TABLE IF EXISTS sensor_readings;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS sensor_models;
DROP TABLE IF EXISTS zones;
DROP TABLE IF EXISTS irrigation_systems;
DROP TABLE IF EXISTS client_payment_details;
DROP TABLE IF EXISTS clients;

-- Таблиця клієнтів
CREATE TABLE clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(20),
    registration_date DATE NOT NULL
) ENGINE = INNODB;

-- Таблиця платіжних реквізитів клієнтів (зв'язок 1:1 з clients)
CREATE TABLE client_payment_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT UNIQUE NOT NULL,
    company_name VARCHAR(100),
    tax_id VARCHAR(20) NOT NULL UNIQUE,
    iban VARCHAR(34) NOT NULL UNIQUE,
    bank_name VARCHAR(100) NOT NULL,
    billing_address VARCHAR(255) NOT NULL,
    vat_payer BOOLEAN DEFAULT FALSE,
    CONSTRAINT fk_payment_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
) ENGINE = INNODB;

-- Таблиця систем автополиву
CREATE TABLE irrigation_systems (
    id INT AUTO_INCREMENT PRIMARY KEY,
    client_id INT NOT NULL,
    system_name VARCHAR(100) NOT NULL,
    status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
    CONSTRAINT fk_system_client FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE
) ENGINE = INNODB;

-- Таблиця зон (ділянок) поливу
CREATE TABLE zones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    system_id INT NOT NULL,
    zone_name VARCHAR(100) NOT NULL,
    area_sq_meters DECIMAL(10,2),
    CONSTRAINT fk_zone_system FOREIGN KEY (system_id) REFERENCES irrigation_systems(id) ON DELETE CASCADE
) ENGINE = INNODB;

-- Довідник моделей сенсорів
CREATE TABLE sensor_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer VARCHAR(50) NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    connection_type VARCHAR(20)
) ENGINE = INNODB;

-- Таблиця встановлених сенсорів
CREATE TABLE sensors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_id INT NOT NULL,
    model_id INT NOT NULL,
    gps_lat DECIMAL(10,8) NOT NULL,
    gps_lon DECIMAL(10,8) NOT NULL,
    installation_date DATE,
    CONSTRAINT fk_sensor_zone FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE,
    CONSTRAINT fk_sensor_model FOREIGN KEY (model_id) REFERENCES sensor_models(id)
) ENGINE = INNODB;

-- Журнал показників сенсорів
CREATE TABLE sensor_readings (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    sensor_id INT NOT NULL,
    reading_timestamp DATETIME NOT NULL,
    humidity_percent DECIMAL(5,2),
    temperature_c DECIMAL(5,2),
    light_lux INT,
    CONSTRAINT fk_reading_sensor FOREIGN KEY (sensor_id) REFERENCES sensors(id) ON DELETE CASCADE
) ENGINE = INNODB;

-- Довідник моделей насосів
CREATE TABLE pump_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    manufacturer VARCHAR(50) NOT NULL,
    model_name VARCHAR(50) NOT NULL,
    max_power_kw DECIMAL(5,2)
) ENGINE = INNODB;

-- Таблиця насосів на ділянках
CREATE TABLE pumps (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_id INT NOT NULL,
    model_id INT NOT NULL,
    status ENUM('online', 'offline', 'error') DEFAULT 'online',
    CONSTRAINT fk_pump_zone FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE,
    CONSTRAINT fk_pump_model FOREIGN KEY (model_id) REFERENCES pump_models(id)
) ENGINE = INNODB;

-- Таблиця сопел (спринклерів)
CREATE TABLE nozzles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    zone_id INT NOT NULL,
    gps_lat DECIMAL(10,8) NOT NULL,
    gps_lon DECIMAL(10,8) NOT NULL,
    max_flow_liters_per_hour DECIMAL(8,2) NOT NULL,
    CONSTRAINT fk_nozzle_zone FOREIGN KEY (zone_id) REFERENCES zones(id) ON DELETE CASCADE
) ENGINE = INNODB;

-- Журнал роботи насосів
CREATE TABLE pump_operations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pump_id INT NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME,
    water_pumped_liters DECIMAL(10,2),
    CONSTRAINT fk_operation_pump FOREIGN KEY (pump_id) REFERENCES pumps(id) ON DELETE CASCADE
) ENGINE = INNODB;

-- Додаткові індекси для оптимізації вибірки за часом та координатами
CREATE INDEX idx_sensor_readings_time ON sensor_readings(reading_timestamp);
CREATE INDEX idx_pump_operations_start ON pump_operations(start_time);
CREATE INDEX idx_sensors_location ON sensors(gps_lat, gps_lon);

-- Заповнення таблиць даними з дотриманням порядку зовнішніх ключів
INSERT INTO clients (first_name, last_name, email, phone, registration_date) VALUES
('Олег', 'Петренко', 'oleg.p@example.com', '+380501234567', '2025-05-10'),
('Марія', 'Коваль', 'maria.k@example.com', '+380671234567', '2025-06-15'),
('Іван', 'Бойко', 'ivan.b@example.com', '+380631234567', '2025-07-20'),
('Анна', 'Шевченко', 'anna.sh@example.com', '+380991234567', '2025-08-05'),
('Сергій', 'Мельник', 'serg.m@example.com', '+380981234567', '2025-09-01'),
('Дмитро', 'Ткаченко', 'dmytro.t@example.com', '+380502345678', '2025-09-18'),
('Оксана', 'Кравченко', 'oksana.kr@example.com', '+380672345678', '2025-10-03'),
('Василь', 'Олійник', 'vasyl.o@example.com', '+380632345678', '2025-10-22'),
('Наталія', 'Лисенко', 'natalia.l@example.com', '+380992345678', '2025-11-11'),
('Андрій', 'Савченко', 'andrii.s@example.com', '+380972345678', '2025-12-01');

INSERT INTO client_payment_details (client_id, company_name, tax_id, iban, bank_name, billing_address, vat_payer) VALUES
(1, 'ФГ "Агро-Поділля"', '31245678', 'UA213052990000026001234567890', 'АТ КБ "ПриватБанк"', 'м. Львів, вул. Городоцька, 120', TRUE),
(2, NULL, '2948571632', 'UA843223130000026209876543210', 'АТ "Укрексімбанк"', 'м. Київ, вул. Хрещатик, 24, кв. 15', FALSE),
(3, 'ТОВ "Зерно-Холдинг"', '42398125', 'UA563808050000026007654321098', 'АТ "Райффайзен Банк"', 'м. Полтава, вул. Європейська, 55', TRUE),
(4, 'ФОП Шевченко А. М.', '3312984571', 'UA123253650000026004321098765', 'АТ "Ощадбанк"', 'м. Дніпро, пр. Гагаріна, 12', FALSE),
(5, 'ФГ "Виноградники Закарпаття"', '38912450', 'UA903007110000026009871234560', 'АТ "ПУМБ"', 'м. Ужгород, вул. Собранецька, 88', TRUE),
(6, 'ТОВ "ГрінТек Агро"', '40123987', 'UA443052990000026005556667771', 'АТ КБ "ПриватБанк"', 'м. Вінниця, вул. Келецька, 41', TRUE),
(7, 'ФОП Кравченко О. І.', '3154879620', 'UA673226690000026008889990002', 'АТ "Ощадбанк"', 'м. Тернопіль, вул. Руська, 19', FALSE),
(8, 'ФГ "Сонячний Лан"', '36789123', 'UA193808050000026001112223334', 'АТ "Райффайзен Банк"', 'м. Черкаси, бул. Шевченка, 205', TRUE),
(9, NULL, '3421568974', 'UA733007110000026204445556668', 'АТ "ПУМБ"', 'м. Івано-Франківськ, вул. Галицька, 67', FALSE),
(10, 'ТОВ "АгроСмарт Полив"', '44891236', 'UA353253650000026007778889995', 'АТ "Укрсиббанк"', 'м. Луцьк, пр. Волі, 14', TRUE);

INSERT INTO irrigation_systems (client_id, system_name, status) VALUES
(1, 'Полив Теплиця 1', 'active'),
(1, 'Полив Відкритий Ґрунт', 'active'),
(2, 'Смарт-сад', 'maintenance'),
(3, 'Поле Пшениця', 'active'),
(4, 'Газон Біля Дому', 'active'),
(5, 'Виноградник', 'inactive'),
(6, 'Ягідний Комплекс', 'active'),
(7, 'Теплиця Мікрозелень', 'active'),
(8, 'Сад Яблуневий', 'maintenance'),
(9, 'Оранжерея Троянди', 'active'),
(10, 'Поле Кукурудза', 'active');

INSERT INTO zones (system_id, zone_name, area_sq_meters) VALUES
(1, 'Сектор А (Огірки)', 150.50),
(1, 'Сектор Б (Томати)', 200.00),
(2, 'Ділянка Картопля', 1000.00),
(3, 'Фруктові дерева', 500.00),
(4, 'Північна сторона', 2500.00),
(5, 'Центральний газон', 50.00),
(6, 'Тераса Виноград Каберне', 850.00),
(7, 'Плантація Лохини', 1200.00),
(8, 'Стелажі Рукола', 95.00),
(9, 'Квартал Голден Делішес', 1800.00),
(10, 'Сектор Гібридний', 3200.00);

INSERT INTO sensor_models (manufacturer, model_name, connection_type) VALUES
('Espressif', 'ESP32-C3 SmartNode', 'MQTT'),
('Espressif', 'ESP32-S3 AgriNode', 'MQTT'),
('Bosch', 'BME280 Combo', 'I2C'),
('Arduino', 'MKR WAN 1310', 'LoRaWAN'),
('Xiaomi', 'Mijia Plant', 'Bluetooth'),
('Dragino', 'LSE01 Soil Node', 'LoRaWAN'),
('Sensirion', 'SHT35 Precision', 'I2C'),
('Milesight', 'EM500-SMTC', 'LoRaWAN'),
('Sonoff', 'TH Elite Soil', 'MQTT'),
('Netatmo', 'Smart Garden Probe', 'Wi-Fi');

INSERT INTO sensors (zone_id, model_id, gps_lat, gps_lon, installation_date) VALUES
(1, 1, 49.90150012, 23.95540011, '2026-03-01'),
(2, 2, 49.90160015, 23.95550014, '2026-03-02'),
(3, 4, 49.90200000, 23.95600000, '2026-03-10'),
(4, 3, 49.89500000, 23.94000000, '2026-04-05'),
(5, 1, 49.85000000, 24.01000000, '2026-04-20'),
(6, 5, 49.84000000, 24.02000000, '2026-05-01'),
(7, 6, 48.62080000, 22.28790000, '2026-05-03'),
(8, 7, 49.23310000, 28.46820000, '2026-05-05'),
(9, 8, 49.55350000, 25.59480000, '2026-05-07'),
(10, 9, 49.44440000, 32.05980000, '2026-05-10');

INSERT INTO sensor_readings (sensor_id, reading_timestamp, humidity_percent, temperature_c, light_lux) VALUES
(1, '2026-05-15 08:00:00', 45.50, 22.10, 1500),
(1, '2026-05-15 09:00:00', 44.00, 23.50, 2200),
(2, '2026-05-15 08:00:00', 60.20, 21.00, 1450),
(2, '2026-05-15 09:00:00', 58.50, 22.80, 2300),
(3, '2026-05-15 08:00:00', 30.10, 25.00, 5000),
(4, '2026-05-15 08:00:00', 55.00, 19.50, 800),
(5, '2026-05-15 08:00:00', 41.30, 24.20, 4600),
(6, '2026-05-15 08:00:00', 52.80, 20.40, 3100),
(7, '2026-05-15 08:00:00', 37.90, 26.10, 5400),
(8, '2026-05-15 08:00:00', 64.00, 18.90, 1900),
(9, '2026-05-15 08:00:00', 49.20, 21.70, 1200),
(10, '2026-05-15 08:00:00', 33.40, 27.30, 6100);

INSERT INTO pump_models (manufacturer, model_name, max_power_kw) VALUES
('Grundfos', 'SCALA2', 0.55),
('Pedrollo', 'JCRm 15', 1.10),
('Optima', 'JET100', 0.75),
('Karcher', 'BP 3 Garden', 0.80),
('Aquatica', '775311', 1.50),
('Wilo', 'Jet WJ 202', 0.90),
('DAB', 'EuroInox 40/50', 1.20),
('Metabo', 'P 3300 G', 0.90),
('AL-KO', 'Jet 3600', 0.85),
('Speroni', 'CAM 88', 0.75);

INSERT INTO pumps (zone_id, model_id, status) VALUES
(1, 1, 'online'),
(2, 2, 'online'),
(3, 5, 'online'),
(4, 3, 'offline'),
(5, 4, 'online'),
(6, 1, 'error'),
(7, 6, 'online'),
(8, 7, 'online'),
(9, 8, 'online'),
(10, 9, 'offline');

INSERT INTO nozzles (zone_id, gps_lat, gps_lon, max_flow_liters_per_hour) VALUES
(1, 49.90151000, 23.95541000, 50.00),
(1, 49.90152000, 23.95542000, 50.00),
(2, 49.90161000, 23.95551000, 100.00),
(3, 49.90205000, 23.95605000, 200.00),
(4, 49.89505000, 23.94005000, 150.00),
(5, 49.85005000, 24.01005000, 30.00),
(6, 49.84005000, 24.02005000, 45.00),
(7, 48.62085000, 22.28795000, 120.00),
(8, 49.23315000, 28.46825000, 180.00),
(9, 49.55355000, 25.59485000, 60.00),
(10, 49.44445000, 32.05985000, 220.00);

INSERT INTO pump_operations (pump_id, start_time, end_time, water_pumped_liters) VALUES
(1, '2026-05-14 18:00:00', '2026-05-14 18:30:00', 120.50),
(1, '2026-05-15 06:00:00', '2026-05-15 06:20:00', 80.00),
(2, '2026-05-14 19:00:00', '2026-05-14 20:00:00', 350.00),
(3, '2026-05-15 05:00:00', '2026-05-15 07:00:00', 1500.00),
(5, '2026-05-15 20:00:00', '2026-05-15 20:45:00', 200.50),
(1, '2026-05-15 18:00:00', '2026-05-15 18:15:00', 60.00),
(2, '2026-05-15 19:00:00', '2026-05-15 19:40:00', 240.00),
(3, '2026-05-16 05:00:00', '2026-05-16 06:30:00', 1120.00),
(7, '2026-05-16 06:00:00', '2026-05-16 06:45:00', 310.00),
(8, '2026-05-16 07:00:00', '2026-05-16 08:00:00', 480.00),
(9, '2026-05-16 07:30:00', '2026-05-16 08:00:00', 95.00),
(5, '2026-05-16 19:30:00', '2026-05-16 20:15:00', 210.00);
