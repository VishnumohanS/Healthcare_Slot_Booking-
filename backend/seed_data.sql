-- Sample data. Run AFTER `alembic upgrade head` (tables must exist):
--     python -m app.db.seed          (skips if doctors already exist)
--     sqlite3 healthcare.db < seed_data.sql
-- Idempotent: explicit IDs + INSERT OR IGNORE, so re-running never violates a constraint.

INSERT OR IGNORE INTO doctors (id, name, specialization, start_hour, end_hour) VALUES
    (1, 'Dr. Asha Raman',      'Cardiology',  9, 17),
    (2, 'Dr. Miguel Alvarez',  'Pediatrics',  8, 16),
    (3, 'Dr. Priya Nair',      'Dermatology', 10, 18),
    (4, 'Dr. Tomasz Kowalski', 'Orthopedics', 9, 13);

-- Slots are relative to "tomorrow" (local time) so the sample data is always in the future.
-- datetime() yields the canonical 'YYYY-MM-DD HH:MM:SS' text the application also stores.
INSERT OR IGNORE INTO appointments (id, doctor_id, patient_name, slot, status) VALUES
    (1, 1, 'Sample Patient A',   datetime(date('now', 'localtime', '+1 day') || ' 09:30:00'), 'booked'),
    (2, 1, 'Sample Patient B',   datetime(date('now', 'localtime', '+1 day') || ' 10:00:00'), 'booked'),
    (3, 2, 'Sample Patient C',   datetime(date('now', 'localtime', '+1 day') || ' 08:00:00'), 'booked'),
    (4, 2, 'Cancelled Sample',   datetime(date('now', 'localtime', '+1 day') || ' 08:30:00'), 'cancelled');
