-- FlyRank Internship Backend Track · Week 3 · Assignment A2
-- Stage 4: Learn your first SQL by hand

-- 1. List every task in the database
SELECT * FROM tasks;
-- Result: Returns all task rows with columns (id, title, done)

-- 2. List only completed tasks
SELECT * FROM tasks WHERE done = 1;
-- Result: Returns tasks where done is 1 (e.g., id 1 'Set up project')

-- 3. Count how many tasks are in the table
SELECT COUNT(*) FROM tasks;
-- Result: Returns the total count of task records

-- 4. Mark every task completed
UPDATE tasks SET done = 1;
-- Result: Updates all records, setting done = 1

-- 5. Delete all completed tasks
DELETE FROM tasks WHERE done = 1;
-- Result: Deletes all rows where done = 1 (empty table if all were done)
