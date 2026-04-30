# Turtle-ID Database Schema

## 📊 Database Structure

```
Database: turtle_id_db
User: turtle_user
Port: 3306
```

---

## 🗂️ Tables

### 1. `turtles` - Core Turtle Records

```sql
CREATE TABLE turtles (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    species VARCHAR(100) NOT NULL COMMENT 'e.g., Chelonia mydas, Dermochelys coriacea',
    biometric_code VARCHAR(255) UNIQUE COMMENT 'Unique biometric identifier (post-ocular scutes pattern or pineal spot coords)',
    
    -- Analysis data
    analysis_result LONGTEXT COMMENT 'JSON: {species, confidence, features, extraction_method}',
    quality_score DECIMAL(3,2) COMMENT '0.00 - 1.00 image quality',
    
    -- Physical measurements
    shell_length_cm DECIMAL(5,2),
    shell_width_cm DECIMAL(5,2),
    weight_kg DECIMAL(6,2),
    
    -- Health information
    health_status ENUM('GOOD', 'FAIR', 'POOR', 'UNKNOWN') DEFAULT 'UNKNOWN',
    wounds_description TEXT,
    diseases TEXT,
    parasites TEXT,
    
    -- Location & observer
    discovery_latitude DECIMAL(10,8),
    discovery_longitude DECIMAL(11,8),
    discovery_accuracy_m DECIMAL(8,2),
    observer_name VARCHAR(255),
    observer_email VARCHAR(255),
    observer_organization VARCHAR(255),
    
    -- Timestamps
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    INDEX idx_species (species),
    INDEX idx_biometric (biometric_code),
    INDEX idx_registered (registered_at),
    FULLTEXT INDEX ft_description (wounds_description)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Core turtle identification records with biometric data';
```

**Key Fields for SOLID Agents:**
- `biometric_code`: Used by **Matching Agent** for similarity comparison
- `analysis_result`: Stores complete output from **Biolytics Agent**
- `species`: Species classification from **Biolytics Agent**

---

### 2. `sightings` - Observation Records

```sql
CREATE TABLE sightings (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    turtle_id CHAR(36) NOT NULL COMMENT 'Foreign key to turtles',
    
    -- Sighting details
    sighting_date DATETIME NOT NULL,
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    accuracy_m DECIMAL(8,2),
    
    -- Conditions
    water_temperature_c DECIMAL(4,2),
    weather VARCHAR(50),
    water_clarity VARCHAR(50),
    
    -- Observer
    observer_name VARCHAR(255),
    observer_email VARCHAR(255),
    
    -- Image metadata
    image_hash VARCHAR(64) COMMENT 'SHA256 of original image',
    image_quality_score DECIMAL(3,2),
    
    -- Report reference
    report_id CHAR(36),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (turtle_id) REFERENCES turtles(id) ON DELETE CASCADE,
    INDEX idx_turtle_id (turtle_id),
    INDEX idx_sighting_date (sighting_date),
    INDEX idx_report_id (report_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Individual sightings/observations of turtles';
```

---

### 3. `turtle_features` - Extracted Biometric Features

```sql
CREATE TABLE turtle_features (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    turtle_id CHAR(36) NOT NULL COMMENT 'Foreign key to turtles',
    sighting_id CHAR(36) COMMENT 'Optional: specific sighting',
    
    -- Feature type
    feature_type VARCHAR(50) NOT NULL COMMENT 'post_ocular_scutes, pineal_spot, shell_pattern, etc.',
    
    -- For Green Turtles (post-ocular scutes)
    scutes_count INT COMMENT 'Number of scutes detected',
    scutes_pattern VARCHAR(500) COMMENT 'Pattern description or string representation',
    
    -- For Leatherbacks (pineal spot)
    pineal_spot_detected BOOLEAN,
    pineal_spot_size VARCHAR(20) COMMENT 'small, medium, large',
    pineal_spot_coordinates VARCHAR(100) COMMENT 'JSON: {cx, cy}',
    
    -- General
    confidence_score DECIMAL(3,2),
    extraction_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (turtle_id) REFERENCES turtles(id) ON DELETE CASCADE,
    FOREIGN KEY (sighting_id) REFERENCES sightings(id) ON DELETE SET NULL,
    INDEX idx_turtle_id (turtle_id),
    INDEX idx_feature_type (feature_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Extracted biometric features for species-specific identification';
```

---

### 4. `reports` - Generated Analysis Reports

```sql
CREATE TABLE reports (
    id CHAR(36) PRIMARY KEY COMMENT 'UUID',
    sighting_id CHAR(36) NOT NULL COMMENT 'Foreign key to sightings',
    turtle_id CHAR(36) NOT NULL COMMENT 'Foreign key to turtles',
    
    -- Report content
    report_type ENUM('JSON', 'PDF') DEFAULT 'JSON',
    report_data LONGTEXT NOT NULL COMMENT 'JSON report structure',
    
    -- Report details
    matching_result ENUM('EXISTING_RECORD', 'NEW_INDIVIDUAL'),
    matching_confidence DECIMAL(3,2),
    top_match_turtle_id CHAR(36),
    
    -- Methodology & compliance
    methodology_non_invasive BOOLEAN DEFAULT TRUE,
    dekamer_compliant BOOLEAN DEFAULT TRUE,
    dekamer_version VARCHAR(10),
    
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (sighting_id) REFERENCES sightings(id) ON DELETE CASCADE,
    FOREIGN KEY (turtle_id) REFERENCES turtles(id) ON DELETE CASCADE,
    FOREIGN KEY (top_match_turtle_id) REFERENCES turtles(id) ON DELETE SET NULL,
    INDEX idx_sighting_id (sighting_id),
    INDEX idx_turtle_id (turtle_id),
    INDEX idx_matching_result (matching_result)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci
COMMENT='Generated analysis reports (DEKAMER standard compliant)';
```

---

## 🔄 Data Flow Through Agents

### Workflow 1: New Turtle Identification

```
1. Gatekeeper Agent ──► Validates metadata
                        └─► Insert → sightings (observer, location, conditions)

2. Biolytics Agent ─────► Analyzes image
                        └─► Update → turtles (species, analysis_result)
                        └─► Insert → turtle_features (scutes, pineal_spot)

3. Matching Agent ──────► Queries GET /api/turtle/biometrics
                        └─► Similarity search → turtles
                        └─► Update → sightings (report_id)

4. Reporter Agent ──────► Generate report
                        └─► Insert → reports (report_data, matching_result)
```

### Example: Green Turtle Identified

```sql
-- 1. New sighting record
INSERT INTO sightings (
    id, turtle_id, sighting_date, latitude, longitude, 
    observer_name, weather, water_temperature_c
) VALUES (
    'sight-uuid-1', 'turtle-uuid-1', NOW(), 36.7138, 31.2327,
    'Dr. John Doe', 'sunny', 24.5
);

-- 2. Turtle species & analysis
UPDATE turtles SET
    species = 'Chelonia mydas',
    analysis_result = '{
        "species": "Chelonia mydas",
        "confidence": 0.92,
        "biometric_code": "102034560912341111",
        "extraction_method": "post_ocular_scutes_pattern",
        "features": {
            "shell_color": "dark_green",
            "post_ocular_scutes": 15
        }
    }',
    shell_length_cm = 85.5,
    shell_width_cm = 75.0
WHERE id = 'turtle-uuid-1';

-- 3. Biometric features
INSERT INTO turtle_features (
    id, turtle_id, feature_type, scutes_count, confidence_score
) VALUES (
    'feat-uuid-1', 'turtle-uuid-1', 'post_ocular_scutes', 15, 0.92
);

-- 4. Matching result
UPDATE sightings SET
    report_id = 'report-uuid-1'
WHERE id = 'sight-uuid-1';

INSERT INTO reports (
    id, sighting_id, turtle_id, matching_result, 
    matching_confidence, dekamer_compliant
) VALUES (
    'report-uuid-1', 'sight-uuid-1', 'turtle-uuid-1',
    'EXISTING_RECORD', 0.96, TRUE
);
```

---

## 🔑 Index Strategy

### For Matching Agent Performance
```sql
-- Critical index for biometric lookup
CREATE INDEX idx_biometric_code ON turtles(biometric_code);

-- Species filtering
CREATE INDEX idx_species ON turtles(species);

-- Time-based queries
CREATE INDEX idx_registered ON turtles(registered_at);
```

### For Report Queries
```sql
CREATE INDEX idx_turtle_id_sighting ON sightings(turtle_id);
CREATE INDEX idx_sighting_id_report ON reports(sighting_id);
CREATE FULLTEXT INDEX ft_wounds ON turtles(wounds_description);
```

---

## 📋 SQL Migration: Add Biometric Columns

```sql
-- Add biometric_code column if not exists
ALTER TABLE turtles 
ADD COLUMN IF NOT EXISTS biometric_code VARCHAR(255) UNIQUE 
COMMENT 'Unique biometric identifier for matching';

-- Add index
ALTER TABLE turtles 
ADD INDEX IF NOT EXISTS idx_biometric_code (biometric_code);

-- Verify schema
DESC turtles;

-- Show turtles with biometric codes
SELECT id, species, biometric_code FROM turtles 
WHERE biometric_code IS NOT NULL;
```

---

## 🧪 Test Data

### Insert Sample Turtles

```sql
-- Green Turtle 1
INSERT INTO turtles (
    id, species, biometric_code, analysis_result,
    shell_length_cm, shell_width_cm, weight_kg, health_status
) VALUES (
    UUID(), 'Chelonia mydas', '102034560912341111',
    '{
        "species": "Chelonia mydas",
        "confidence": 0.92,
        "extraction_method": "post_ocular_scutes_pattern"
    }',
    85.5, 75.0, 150, 'GOOD'
);

-- Leatherback 1
INSERT INTO turtles (
    id, species, biometric_code, analysis_result,
    shell_length_cm, shell_width_cm, weight_kg, health_status
) VALUES (
    UUID(), 'Dermochelys coriacea', '003651001204003456',
    '{
        "species": "Dermochelys coriacea",
        "confidence": 0.90,
        "extraction_method": "pineal_spot_analysis"
    }',
    120.0, 105.0, 450, 'GOOD'
);
```

---

## 🔍 Query Examples

### Find Turtle by Biometric Code
```sql
SELECT * FROM turtles 
WHERE biometric_code = '102034560912341111';
```

### Get All Turtles for Matching Agent
```sql
SELECT 
    id as turtle_id,
    species,
    biometric_code,
    analysis_result,
    registered_at
FROM turtles
WHERE biometric_code IS NOT NULL
ORDER BY registered_at DESC;
```

### Recent Sightings
```sql
SELECT 
    s.id, s.sighting_date,
    t.species, t.biometric_code,
    s.observer_name, s.water_temperature_c
FROM sightings s
JOIN turtles t ON s.turtle_id = t.id
ORDER BY s.sighting_date DESC
LIMIT 10;
```

### Matching Statistics
```sql
SELECT 
    matching_result,
    COUNT(*) as count,
    AVG(matching_confidence) as avg_confidence
FROM reports
GROUP BY matching_result;
```

---

## 🚀 Database Setup Script

Create `database-agent/setup.sql`:

```sql
-- Create database
CREATE DATABASE IF NOT EXISTS turtle_id_db 
CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE turtle_id_db;

-- Create user
CREATE USER IF NOT EXISTS 'turtle_user'@'localhost' IDENTIFIED BY 'turtle_password';
GRANT ALL PRIVILEGES ON turtle_id_db.* TO 'turtle_user'@'localhost';

-- Create tables
-- [Include all table creation statements above]

-- Create indexes
-- [Include all index creation statements above]

-- Display summary
SELECT 'Database setup complete!' as status;
SHOW TABLES;
```

---

## 🔧 Connection String

```
mysql://turtle_user:turtle_password@localhost:3306/turtle_id_db
```

---

## 📝 Notes

1. **Biometric Code**: Critical for Matching Agent
   - Green Turtle: 20-character string from scute ratios
   - Leatherback: 14-character string from pineal spot coordinates

2. **Analysis Result**: Stored as JSON for flexibility
   - Allows schema evolution without migrations
   - Supports multiple species analysis formats

3. **Timestamps**: All records timestamped for audit trail

4. **UUIDs**: All IDs are UUIDs for distributed system support

5. **Collation**: UTF-8 for international character support

---

## 🎯 SOLID Architecture Mapping

| Agent | Tables Used | Operations |
|-------|------------|-----------|
| Gatekeeper | sightings | INSERT metadata |
| Biolytics | turtles, turtle_features | UPDATE/INSERT analysis |
| Matching | turtles | SELECT by biometric_code |
| Reporter | reports, sightings, turtles | INSERT reports |
| Database | all | CRUD for all |

