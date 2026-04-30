-- Veritabanı Oluştur
CREATE DATABASE IF NOT EXISTS turtle_id_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE turtle_id_db;

-- Turtles Tablosu
CREATE TABLE IF NOT EXISTS turtles (
    id VARCHAR(36) PRIMARY KEY,
    image_base64 LONGTEXT NOT NULL,
    analysis_result JSON,
    metadata JSON,
    species VARCHAR(100),
    location VARCHAR(200),
    registered_at DATETIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_species (species),
    INDEX idx_location (location),
    FULLTEXT INDEX ft_metadata (metadata)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Sightings Tablosu (Avistama Kayıtları)
CREATE TABLE IF NOT EXISTS sightings (
    id VARCHAR(36) PRIMARY KEY,
    turtle_id VARCHAR(36) NOT NULL,
    location VARCHAR(200),
    date_sighted DATETIME,
    observer_name VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (turtle_id) REFERENCES turtles(id),
    INDEX idx_turtle_id (turtle_id),
    INDEX idx_date (date_sighted)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Turtle Features Tablosu (Benzerlik Araması için)
CREATE TABLE IF NOT EXISTS turtle_features (
    id VARCHAR(36) PRIMARY KEY,
    turtle_id VARCHAR(36) NOT NULL,
    feature_vector LONGBLOB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (turtle_id) REFERENCES turtles(id),
    INDEX idx_turtle_id (turtle_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Test Verisi Ekle (Opsiyonel)
INSERT INTO turtles (id, image_base64, species, location, registered_at) VALUES
('turtle_001', 'base64_image_data_here', 'Chelonia mydas', 'Dalyan Beach', NOW()),
('turtle_002', 'base64_image_data_here', 'Dermochelys coriacea', 'Iztuzu Beach', NOW());

INSERT INTO sightings (id, turtle_id, location, date_sighted, observer_name) VALUES
('sighting_001', 'turtle_001', 'Dalyan Beach', NOW(), 'Dr. John Doe'),
('sighting_002', 'turtle_001', 'Dalyan Beach', DATE_SUB(NOW(), INTERVAL 5 DAY), 'Dr. Jane Smith');

-- Tabloları Kontrol Et
SELECT 'Tables created successfully!' as status;
SHOW TABLES;
