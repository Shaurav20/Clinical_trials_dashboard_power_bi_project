CREATE DATABASE clinical_trials;
USE clinical_trials;

-- Main trials table (adjusted for your data characteristics)
CREATE TABLE trials (
    nct_id VARCHAR(20) PRIMARY KEY,
    title TEXT,
    status VARCHAR(50),
    phase VARCHAR(20),
    study_type VARCHAR(50),
    sponsor VARCHAR(255) DEFAULT 'Unknown',
    start_date DATE,
    completion_date DATE,
    enrollment INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_status (status),
    INDEX idx_phase (phase),
    INDEX idx_study_type (study_type),
    INDEX idx_start_date (start_date)
);

-- Locations table
CREATE TABLE locations (
    location_id INT AUTO_INCREMENT PRIMARY KEY,
    nct_id VARCHAR(20),
    country VARCHAR(100),
    state VARCHAR(100),
    city VARCHAR(100),
    facility VARCHAR(255),
    FOREIGN KEY (nct_id) REFERENCES trials(nct_id) ON DELETE CASCADE,
    INDEX idx_country (country),
    INDEX idx_state (state),
    INDEX idx_nct_id (nct_id)
);

-- Conditions table
CREATE TABLE conditions (
    condition_id INT AUTO_INCREMENT PRIMARY KEY,
    nct_id VARCHAR(20),
    condition_name VARCHAR(255),
    FOREIGN KEY (nct_id) REFERENCES trials(nct_id) ON DELETE CASCADE,
    INDEX idx_condition (condition_name),
    INDEX idx_nct_id (nct_id)
);

-- Interventions table
CREATE TABLE interventions (
    intervention_id INT AUTO_INCREMENT PRIMARY KEY,
    nct_id VARCHAR(20),
    intervention_type VARCHAR(100),
    intervention_name VARCHAR(255),
    FOREIGN KEY (nct_id) REFERENCES trials(nct_id) ON DELETE CASCADE,
    INDEX idx_type (intervention_type),
    INDEX idx_nct_id (nct_id)
);