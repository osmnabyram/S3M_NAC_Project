CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    role VARCHAR(20) DEFAULT 'guest', -- admin, employee, guest
    vlan_id INTEGER DEFAULT 10,
    is_active BOOLEAN DEFAULT true
);

CREATE TABLE IF NOT EXISTS radius_logs (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50),
    auth_status VARCHAR(20),
    vlan_id INTEGER,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Varsayılan admin kullanıcısını ekle (zaten varsa atla)
INSERT INTO users (username, password_hash, role, vlan_id, is_active)
VALUES ('s3m_admin', 'hashed_admin_pass', 'admin', 10, true)
ON CONFLICT (username) DO NOTHING;