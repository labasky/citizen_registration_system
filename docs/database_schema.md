# Database Schema Design for Citizen Registration System

## 1. Entity Relationship Diagram (Conceptual)

```
+----------------+       +----------------+       +----------------+
| State          |       | LGA            |       | Ward           |
+----------------+       +----------------+       +----------------+
| state_id (PK)  |<----->| lga_id (PK)    |<----->| ward_id (PK)   |
| state_name     |       | lga_name       |       | ward_name      |
| state_code     |       | state_id (FK)  |       | lga_id (FK)    |
+----------------+       +----------------+       +----------------+
        ^                        ^                        ^
        |                        |                        |
+----------------+       +----------------+       +----------------+
| User           |       | Role           |       | Permission     |
+----------------+       +----------------+       +----------------+
| user_id (PK)   |<----->| role_id (PK)   |<----->| perm_id (PK)   |
| username       |       | role_name      |       | perm_name      |
| password_hash  |       | description    |       | description    |
| email          |       |                |       |                |
| state_id (FK)  |       +----------------+       +----------------+
| lga_id (FK)    |               ^
| ward_id (FK)   |               |
| role_id (FK)   |       +----------------+
+----------------+       | RolePermission |
        ^                +----------------+
        |                | role_id (FK)   |
        |                | perm_id (FK)   |
        |                +----------------+
        |
+----------------+
| Citizen        |
+----------------+
| citizen_id (PK)|
| unique_id      |
| first_name     |
| middle_name    |
| last_name      |
| date_of_birth  |
| gender         |
| marital_status |
| nationality    |
| state_id (FK)  |
| lga_id (FK)    |
| ward_id (FK)   |
| address        |
| phone          |
| email          |
| religion       |
| ethnicity      |
| photo_url      |
| created_by (FK)|
| created_at     |
| updated_by (FK)|
| updated_at     |
+----------------+
        |
        |
+-------+---------+----------------+----------------+----------------+
|                 |                |                |                |
v                 v                v                v                v
+----------------+ +----------------+ +----------------+ +----------------+
| Biometric      | | Family         | | Education      | | Occupation     |
+----------------+ +----------------+ +----------------+ +----------------+
| bio_id (PK)    | | family_id (PK) | | edu_id (PK)    | | occ_id (PK)    |
| citizen_id (FK)| | citizen_id (FK)| | citizen_id (FK)| | citizen_id (FK)|
| fingerprint    | | relation_type  | | level          | | job_title      |
| facial_data    | | related_to (FK)| | institution    | | employer       |
| signature      | | relation_name  | | qualification  | | work_address   |
+----------------+ +----------------+ | year_completed | | start_date     |
                                      +----------------+ | end_date       |
                                                         | income_range    |
                                                         +----------------+
                                                                |
+----------------+                +----------------+            |
| HealthRecord   |                | Sport          |            |
+----------------+                +----------------+            |
| health_id (PK) |                | sport_id (PK)  |            |
| citizen_id (FK)|                | citizen_id (FK)|            |
| blood_group    |                | sport_name     |            |
| genotype       |                | level          |            |
| allergies      |                | achievements   |            |
| disabilities   |                +----------------+            |
| conditions     |                                              |
| insurance_info |                                              |
+----------------+                                              |
        |                                                       |
        |                                                       |
        v                                                       v
+----------------+                                    +----------------+
| Vaccination    |                                    | Skill          |
+----------------+                                    +----------------+
| vacc_id (PK)   |                                    | skill_id (PK)  |
| health_id (FK) |                                    | occ_id (FK)    |
| vaccine_name   |                                    | skill_name     |
| date_given     |                                    | proficiency    |
| expiry_date    |                                    +----------------+
+----------------+

+----------------+
| IDCard         |
+----------------+
| card_id (PK)   |
| citizen_id (FK)|
| card_number    |
| issue_date     |
| expiry_date    |
| status         |
| issued_by (FK) |
+----------------+

+----------------+
| Document       |
+----------------+
| doc_id (PK)    |
| citizen_id (FK)|
| doc_type       |
| doc_number     |
| issue_date     |
| expiry_date    |
| doc_url        |
+----------------+

+----------------+
| AuditLog       |
+----------------+
| log_id (PK)    |
| user_id (FK)   |
| action         |
| entity_type    |
| entity_id      |
| timestamp      |
| ip_address     |
| details        |
+----------------+
```

## 2. Database Tables (SQL Schema)

### 2.1 Location Tables

```sql
-- States Table
CREATE TABLE states (
    state_id SERIAL PRIMARY KEY,
    state_name VARCHAR(100) NOT NULL,
    state_code VARCHAR(2) NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Local Government Areas Table
CREATE TABLE local_government_areas (
    lga_id SERIAL PRIMARY KEY,
    lga_name VARCHAR(100) NOT NULL,
    lga_code VARCHAR(2) NOT NULL,
    state_id INTEGER NOT NULL REFERENCES states(state_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(state_id, lga_code)
);

-- Wards Table
CREATE TABLE wards (
    ward_id SERIAL PRIMARY KEY,
    ward_name VARCHAR(100) NOT NULL,
    ward_code VARCHAR(3) NOT NULL,
    lga_id INTEGER NOT NULL REFERENCES local_government_areas(lga_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(lga_id, ward_code)
);
```

### 2.2 User Management Tables

```sql
-- Roles Table
CREATE TABLE roles (
    role_id SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Permissions Table
CREATE TABLE permissions (
    permission_id SERIAL PRIMARY KEY,
    permission_name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Role Permissions Table
CREATE TABLE role_permissions (
    role_id INTEGER NOT NULL REFERENCES roles(role_id),
    permission_id INTEGER NOT NULL REFERENCES permissions(permission_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (role_id, permission_id)
);

-- Users Table
CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    role_id INTEGER NOT NULL REFERENCES roles(role_id),
    state_id INTEGER REFERENCES states(state_id),
    lga_id INTEGER REFERENCES local_government_areas(lga_id),
    ward_id INTEGER REFERENCES wards(ward_id),
    is_active BOOLEAN DEFAULT TRUE,
    last_login TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_jurisdiction CHECK (
        (role_id = 1) OR -- Super Admin has no jurisdiction restrictions
        (state_id IS NOT NULL AND lga_id IS NULL AND ward_id IS NULL) OR -- State level
        (state_id IS NOT NULL AND lga_id IS NOT NULL AND ward_id IS NULL) OR -- LGA level
        (state_id IS NOT NULL AND lga_id IS NOT NULL AND ward_id IS NOT NULL) -- Ward level
    )
);

-- Audit Log Table
CREATE TABLE audit_logs (
    log_id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(user_id),
    action VARCHAR(50) NOT NULL,
    entity_type VARCHAR(50) NOT NULL,
    entity_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    details TEXT
);
```

### 2.3 Citizen Data Tables

```sql
-- Citizens Table
CREATE TABLE citizens (
    citizen_id SERIAL PRIMARY KEY,
    unique_id VARCHAR(20) NOT NULL UNIQUE,
    first_name VARCHAR(100) NOT NULL,
    middle_name VARCHAR(100),
    last_name VARCHAR(100) NOT NULL,
    date_of_birth DATE NOT NULL,
    gender VARCHAR(10) NOT NULL,
    marital_status VARCHAR(20),
    nationality VARCHAR(50) NOT NULL DEFAULT 'Nigerian',
    state_of_origin INTEGER REFERENCES states(state_id),
    lga_of_origin INTEGER REFERENCES local_government_areas(lga_id),
    residence_state_id INTEGER NOT NULL REFERENCES states(state_id),
    residence_lga_id INTEGER NOT NULL REFERENCES local_government_areas(lga_id),
    residence_ward_id INTEGER NOT NULL REFERENCES wards(ward_id),
    address TEXT NOT NULL,
    phone VARCHAR(15),
    email VARCHAR(100),
    religion VARCHAR(50),
    ethnicity VARCHAR(50),
    languages TEXT,
    photo_url VARCHAR(255),
    registration_date DATE NOT NULL DEFAULT CURRENT_DATE,
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_by INTEGER REFERENCES users(user_id),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Biometric Data Table
CREATE TABLE biometric_data (
    biometric_id SERIAL PRIMARY KEY,
    citizen_id INTEGER NOT NULL REFERENCES citizens(citizen_id),
    fingerprint_data BYTEA,
    facial_data BYTEA,
    signature_data BYTEA,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Family Relationships Table
CREATE TABLE family_relationships (
    relationship_id SERIAL PRIMARY KEY,
    citizen_id INTEGER NOT NULL REFERENCES citizens(citizen_id),
    related_citizen_id INTEGER REFERENCES citizens(citizen_id),
    relationship_type VARCHAR(50) NOT NULL, -- 'parent', 'child', 'spouse', etc.
    relation_name VARCHAR(200), -- For relations not in the system
    relation_details TEXT,
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT different_citizens CHECK (citizen_id != related_citizen_id)
);

-- Education Table
CREATE TABLE education (
    education_id SERIAL PRIMARY KEY,
    citizen_id INTEGER NOT NULL REFERENCES citizens(citizen_id),
    level VARCHAR(50) NOT NULL, -- 'Primary', 'Secondary', 'Tertiary', etc.
    institution VARCHAR(200) NOT NULL,
    qualification VARCHAR(200),
    field_of_study VARCHAR(200),
    start_year INTEGER,
    end_year INTEGER,
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Occupation Table
CREATE TABLE occupations (
    occupation_id SERIAL PRIMARY KEY,
    citizen_id INTEGER NOT NULL REFERENCES citizens(citizen_id),
    job_title VARCHAR(200) NOT NULL,
    employer VARCHAR(200),
    employment_status VARCHAR(50), -- 'Employed', 'Self-employed', 'Unemployed', etc.
    work_address TEXT,
    start_date DATE,
    end_date DATE,
    income_range VARCHAR(50),
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Skills Table
CREATE TABLE skills (
    skill_id SERIAL PRIMARY KEY,
    occupation_id INTEGER NOT NULL REFERENCES occupations(occupation_id),
    skill_name VARCHAR(100) NOT NULL,
    proficiency VARCHAR(50), -- 'Beginner', 'Intermediate', 'Expert', etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health Records Table
CREATE TABLE health_records (
    health_id SERIAL PRIMARY KEY,
    citizen_id INTEGER NOT NULL REFERENCES citizens(citizen_id),
    blood_group VARCHAR(5),
    genotype VARCHAR(5),
    allergies TEXT,
    disabilities TEXT,
    chronic_conditions TEXT,
    health_insurance_number VARCHAR(100),
    health_insurance_provider VARCHAR(200),
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vaccination Records Table
CREATE TABLE vaccination_records (
    vaccination_id SERIAL PRIMARY KEY,
    health_id INTEGER NOT NULL REFERENCES health_records(health_id),
    vaccine_name VARCHAR(100) NOT NULL,
    date_administered DATE NOT NULL,
    expiry_date DATE,
    administered_by VARCHAR(200),
    batch_number VARCHAR(100),
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Sports and Interests Table
CREATE TABLE sports_interests (
    sport_id SERIAL PRIMARY KEY,
    citizen_id INTEGER NOT NULL REFERENCES citizens(citizen_id),
    activity_type VARCHAR(50) NOT NULL, -- 'Sport', 'Hobby', 'Interest', etc.
    activity_name VARCHAR(100) NOT NULL,
    level VARCHAR(50), -- 'Amateur', 'Professional', etc.
    achievements TEXT,
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Identification Documents Table
CREATE TABLE identification_documents (
    document_id SERIAL PRIMARY KEY,
    citizen_id INTEGER NOT NULL REFERENCES citizens(citizen_id),
    document_type VARCHAR(50) NOT NULL, -- 'National ID', 'Voter Card', 'Passport', etc.
    document_number VARCHAR(100) NOT NULL,
    issue_date DATE,
    expiry_date DATE,
    issuing_authority VARCHAR(200),
    document_url VARCHAR(255),
    created_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ID Cards Table
CREATE TABLE id_cards (
    card_id SERIAL PRIMARY KEY,
    citizen_id INTEGER NOT NULL REFERENCES citizens(citizen_id) UNIQUE,
    card_number VARCHAR(20) NOT NULL UNIQUE,
    issue_date DATE NOT NULL DEFAULT CURRENT_DATE,
    expiry_date DATE,
    status VARCHAR(20) NOT NULL DEFAULT 'Active', -- 'Active', 'Expired', 'Revoked', etc.
    issued_by INTEGER NOT NULL REFERENCES users(user_id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 3. Initial Data and Constraints

### 3.1 Default Roles and Permissions

```sql
-- Insert default roles
INSERT INTO roles (role_name, description) VALUES
('Super Administrator', 'Has complete access to all system functions'),
('State Administrator', 'Has access to all data within a state'),
('LGA Administrator', 'Has access to all data within an LGA'),
('Data Entry Operator', 'Can enter and edit citizen data'),
('Report Viewer', 'Can only view reports and analytics');

-- Insert default permissions
INSERT INTO permissions (permission_name, description) VALUES
('manage_users', 'Create, edit, and delete user accounts'),
('manage_roles', 'Create, edit, and delete roles'),
('register_citizens', 'Register new citizens'),
('edit_citizens', 'Edit existing citizen records'),
('view_citizens', 'View citizen records'),
('delete_citizens', 'Delete citizen records'),
('print_id_cards', 'Print ID cards for citizens'),
('generate_reports', 'Generate and view reports'),
('export_data', 'Export data from the system'),
('manage_system', 'Manage system settings');

-- Assign permissions to roles
-- Super Administrator
INSERT INTO role_permissions (role_id, permission_id)
SELECT 1, permission_id FROM permissions;

-- State Administrator
INSERT INTO role_permissions (role_id, permission_id)
SELECT 2, permission_id FROM permissions 
WHERE permission_name IN ('register_citizens', 'edit_citizens', 'view_citizens', 'print_id_cards', 'generate_reports', 'export_data');

-- LGA Administrator
INSERT INTO role_permissions (role_id, permission_id)
SELECT 3, permission_id FROM permissions 
WHERE permission_name IN ('register_citizens', 'edit_citizens', 'view_citizens', 'print_id_cards', 'generate_reports');

-- Data Entry Operator
INSERT INTO role_permissions (role_id, permission_id)
SELECT 4, permission_id FROM permissions 
WHERE permission_name IN ('register_citizens', 'edit_citizens', 'view_citizens', 'print_id_cards');

-- Report Viewer
INSERT INTO role_permissions (role_id, permission_id)
SELECT 5, permission_id FROM permissions 
WHERE permission_name IN ('view_citizens', 'generate_reports');
```

### 3.2 Indexes for Performance

```sql
-- Indexes for citizens table
CREATE INDEX idx_citizens_unique_id ON citizens(unique_id);
CREATE INDEX idx_citizens_name ON citizens(last_name, first_name, middle_name);
CREATE INDEX idx_citizens_residence ON citizens(residence_state_id, residence_lga_id, residence_ward_id);
CREATE INDEX idx_citizens_origin ON citizens(state_of_origin, lga_of_origin);
CREATE INDEX idx_citizens_dob ON citizens(date_of_birth);

-- Indexes for family relationships
CREATE INDEX idx_family_citizen_id ON family_relationships(citizen_id);
CREATE INDEX idx_family_related_citizen_id ON family_relationships(related_citizen_id);

-- Indexes for education
CREATE INDEX idx_education_citizen_id ON education(citizen_id);

-- Indexes for occupations
CREATE INDEX idx_occupations_citizen_id ON occupations(citizen_id);

-- Indexes for health records
CREATE INDEX idx_health_citizen_id ON health_records(citizen_id);

-- Indexes for audit logs
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp);
CREATE INDEX idx_audit_logs_entity ON audit_logs(entity_type, entity_id);
```

### 3.3 Triggers for Audit and Timestamps

```sql
-- Function to update timestamp
CREATE OR REPLACE FUNCTION update_timestamp()
RETURNS TRIGGER AS $$
BEGIN
   NEW.updated_at = CURRENT_TIMESTAMP;
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for citizens table
CREATE TRIGGER update_citizens_timestamp
BEFORE UPDATE ON citizens
FOR EACH ROW
EXECUTE FUNCTION update_timestamp();

-- Similar triggers for other tables with updated_at column
-- ...

-- Function to log changes to citizens
CREATE OR REPLACE FUNCTION log_citizen_changes()
RETURNS TRIGGER AS $$
BEGIN
   INSERT INTO audit_logs(user_id, action, entity_type, entity_id, details)
   VALUES (current_setting('app.user_id')::integer, 
           TG_OP, 
           'citizen', 
           NEW.citizen_id, 
           'Changed citizen data');
   RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger for citizen changes
CREATE TRIGGER log_citizen_changes_trigger
AFTER INSERT OR UPDATE ON citizens
FOR EACH ROW
EXECUTE FUNCTION log_citizen_changes();

-- Similar triggers for other important tables
-- ...
```

## 4. Views for Reporting

```sql
-- Citizen Demographics View
CREATE VIEW citizen_demographics AS
SELECT 
    c.citizen_id,
    c.unique_id,
    c.first_name,
    c.middle_name,
    c.last_name,
    c.date_of_birth,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.date_of_birth)) AS age,
    c.gender,
    c.marital_status,
    c.nationality,
    s_origin.state_name AS state_of_origin,
    l_origin.lga_name AS lga_of_origin,
    s_res.state_name AS residence_state,
    l_res.lga_name AS residence_lga,
    w_res.ward_name AS residence_ward,
    c.religion,
    c.ethnicity
FROM 
    citizens c
LEFT JOIN 
    states s_origin ON c.state_of_origin = s_origin.state_id
LEFT JOIN 
    local_government_areas l_origin ON c.lga_of_origin = l_origin.lga_id
LEFT JOIN 
    states s_res ON c.residence_state_id = s_res.state_id
LEFT JOIN 
    local_government_areas l_res ON c.residence_lga_id = l_res.lga_id
LEFT JOIN 
    wards w_res ON c.residence_ward_id = w_res.ward_id;

-- Citizen Education View
CREATE VIEW citizen_education AS
SELECT 
    c.citizen_id,
    c.unique_id,
    c.first_name,
    c.last_name,
    e.level,
    e.institution,
    e.qualification,
    e.field_of_study,
    e.end_year
FROM 
    citizens c
JOIN 
    education e ON c.citizen_id = e.citizen_id;

-- Citizen Occupation View
CREATE VIEW citizen_occupation AS
SELECT 
    c.citizen_id,
    c.unique_id,
    c.first_name,
    c.last_name,
    o.job_title,
    o.employer,
    o.employment_status,
    o.income_range,
    s.skill_name,
    s.proficiency
FROM 
    citizens c
JOIN 
    occupations o ON c.citizen_id = o.citizen_id
LEFT JOIN 
    skills s ON o.occupation_id = s.occupation_id;

-- Citizen Health View
CREATE VIEW citizen_health AS
SELECT 
    c.citizen_id,
    c.unique_id,
    c.first_name,
    c.last_name,
    h.blood_group,
    h.genotype,
    h.disabilities,
    h.chronic_conditions,
    h.health_insurance_provider
FROM 
    citizens c
JOIN 
    health_records h ON c.citizen_id = h.citizen_id;

-- LGA Population View
CREATE VIEW lga_population AS
SELECT 
    s.state_name,
    l.lga_name,
    COUNT(c.citizen_id) AS population,
    SUM(CASE WHEN c.gender = 'Male' THEN 1 ELSE 0 END) AS male_count,
    SUM(CASE WHEN c.gender = 'Female' THEN 1 ELSE 0 END) AS female_count,
    SUM(CASE WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.date_of_birth)) < 18 THEN 1 ELSE 0 END) AS minor_count,
    SUM(CASE WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.date_of_birth)) BETWEEN 18 AND 65 THEN 1 ELSE 0 END) AS adult_count,
    SUM(CASE WHEN EXTRACT(YEAR FROM AGE(CURRENT_DATE, c.date_of_birth)) > 65 THEN 1 ELSE 0 END) AS senior_count
FROM 
    citizens c
JOIN 
    states s ON c.residence_state_id = s.state_id
JOIN 
    local_government_areas l ON c.residence_lga_id = l.lga_id
GROUP BY 
    s.state_name, l.lga_name;

-- Occupation Distribution View
CREATE VIEW occupation_distribution AS
SELECT 
    o.job_title,
    COUNT(o.occupation_id) AS count,
    s.state_name,
    l.lga_name
FROM 
    occupations o
JOIN 
    citizens c ON o.citizen_id = c.citizen_id
JOIN 
    states s ON c.residence_state_id = s.state_id
JOIN 
    local_government_areas l ON c.residence_lga_id = l.lga_id
GROUP BY 
    o.job_title, s.state_name, l.lga_name
ORDER BY 
    count DESC;
```

## 5. Database Security Considerations

1. **Data Encryption**
   - Sensitive data like biometric information should be encrypted at rest
   - Use PostgreSQL's pgcrypto extension for column-level encryption

2. **Access Control**
   - Implement row-level security policies to restrict data access based on user jurisdiction
   - Create database roles that align with application roles

3. **Audit Trail**
   - Comprehensive logging of all data modifications
   - Track who made changes, when, and what was changed

4. **Backup and Recovery**
   - Regular automated backups
   - Point-in-time recovery capabilities
   - Disaster recovery planning

5. **Data Validation**
   - Enforce constraints at the database level
   - Use check constraints for data validation

## 6. Database Scaling Considerations

1. **Partitioning**
   - Consider partitioning large tables like citizens by LGA or registration date
   - Implement table partitioning for historical data

2. **Indexing Strategy**
   - Use appropriate indexes for common query patterns
   - Consider partial indexes for frequently filtered queries

3. **Connection Pooling**
   - Implement connection pooling to handle multiple concurrent users

4. **Caching**
   - Implement result caching for frequently accessed, relatively static data
   - Consider using Redis or similar for distributed caching

5. **Read Replicas**
   - Set up read replicas for reporting and analytics queries
   - Separate transaction processing from analytical workloads
