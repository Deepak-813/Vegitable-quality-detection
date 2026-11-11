CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    is_admin VARCHAR(10) DEFAULT 'false',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    vegetable_name VARCHAR(100) NOT NULL,
    quality VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    image_path VARCHAR(500),
    recommendation VARCHAR(500),
    prediction_date TIMESTAMPTZ DEFAULT NOW()
);

UPDATE users SET is_admin = 'true' WHERE email = 'admindeepak@gmail.com';

SELECT id, username, email, is_admin, length(is_admin) FROM users WHERE email = 'admindeepak@gmail.com';

UPDATE users SET is_admin = 'true' WHERE email = 'admindeepak@gmail.com';

SELECT id, username, email, is_admin FROM users WHERE is_admin = 'true';

