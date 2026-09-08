-- Runs automatically the first time the Postgres volume is created.
-- Exactly one table, exactly one string column, exactly one row.
CREATE TABLE IF NOT EXISTS greeting (
    message TEXT NOT NULL
);

INSERT INTO greeting (message)
SELECT 'hello world'
WHERE NOT EXISTS (SELECT 1 FROM greeting);
