-- Add user_id column to sessions table
ALTER TABLE sessions ADD COLUMN user_id INTEGER REFERENCES users(id);