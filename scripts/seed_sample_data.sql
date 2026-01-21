-- Sample data seeding script for testing
-- This adds sample users and violation records for demo purposes

-- Add sample users
INSERT OR IGNORE INTO users (username, password, role) VALUES 
('john_doe', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'user'),
('jane_smith', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'user'),
('test_user', '5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8', 'user');

-- Note: password is 'password' hashed with SHA-256

-- Add sample violation records
INSERT INTO violation_records (user_id, vehicle_type, has_helmet, speed, has_license, violations, total_fine, status, created_at) VALUES
(2, 'motorcycle', 'no', 55, 'yes', '["Riding motorcycle without helmet", "Speeding - 15 km/h over the 40 km/h limit"]', 55000, 'violation', datetime('now', '-5 days')),
(2, 'car', 'na', 38, 'yes', '[]', 0, 'legal', datetime('now', '-4 days')),
(3, 'motorcycle', 'yes', 65, 'no', '["Driving without a valid license", "Speeding - 25 km/h over the 40 km/h limit", "Motorcycle exceeding safe speed of 60 km/h"]', 160000, 'violation', datetime('now', '-3 days')),
(2, 'car', 'na', 42, 'yes', '["Speeding - 2 km/h over the 40 km/h limit"]', 20000, 'violation', datetime('now', '-2 days')),
(3, 'truck', 'na', 35, 'yes', '[]', 0, 'legal', datetime('now', '-1 day')),
(2, 'motorcycle', 'yes', 45, 'yes', '["Speeding - 5 km/h over the 40 km/h limit"]', 20000, 'violation', datetime('now'));

-- Verify data
SELECT 'Users created:' as info, COUNT(*) as count FROM users WHERE role = 'user';
SELECT 'Violation records created:' as info, COUNT(*) as count FROM violation_records;
