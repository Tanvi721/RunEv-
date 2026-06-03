ALTER TABLE users ADD COLUMN auth_provider VARCHAR(32) DEFAULT 'email';
ALTER TABLE users ADD COLUMN created_at DATETIME;
ALTER TABLE users ADD COLUMN last_login_at DATETIME;
ALTER TABLE users ADD COLUMN failed_login_count INTEGER DEFAULT 0 NOT NULL;
ALTER TABLE users ADD COLUMN locked_until DATETIME;

UPDATE users SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL;
UPDATE users SET failed_login_count = 0 WHERE failed_login_count IS NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_providers_vehicle_number_idx ON providers(vehicle_number);
CREATE INDEX IF NOT EXISTS ix_users_email ON users(email);
CREATE INDEX IF NOT EXISTS ix_users_failed_login ON users(email, failed_login_count, locked_until);
