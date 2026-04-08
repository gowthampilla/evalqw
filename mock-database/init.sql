CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    plan_type VARCHAR(50) DEFAULT 'basic'
);

INSERT INTO users (name, email, plan_type) VALUES
('Rahul', 'rahul@startup.in', 'basic'),
('Vikram', 'vikram@startup.in', 'premium'),
('Neha', 'neha@startup.in', 'enterprise');