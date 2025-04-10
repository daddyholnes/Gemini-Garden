-- Add email column to users table
ALTER TABLE users ADD COLUMN email VARCHAR(255);

-- Optional: Make email column NOT NULL after populating existing data
-- ALTER TABLE users ALTER COLUMN email SET NOT NULL;