-- Create model_personalities table
CREATE TABLE model_personalities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    model_name VARCHAR(50) NOT NULL,
    personality_name VARCHAR(50) NOT NULL,
    temperature FLOAT DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 1024,
    system_prompt TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    UNIQUE(user_id, model_name, personality_name)
);