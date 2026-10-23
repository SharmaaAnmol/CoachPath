"""
SQL & Relational Databases Question Bank.
Contains 30 verified questions (10 basic, 10 intermediate, 10 advanced).
"""

SQL_DATABASES_QUESTIONS = [
    # ─── BASIC (10 Questions) ───────────────────────────────────────────
    {
        "difficulty": "basic",
        "topic": "SQL Constraints & Keys",
        "prompt_text": "What is the key difference between a PRIMARY KEY and a UNIQUE constraint in a relational database?",
        "code_snippet": None,
        "options": [
            "PRIMARY KEY can be assigned to multiple columns, whereas UNIQUE cannot.",
            "A table can have only one PRIMARY KEY which rejects NULL values, whereas a table can have multiple UNIQUE constraints and UNIQUE columns generally permit NULLs.",
            "UNIQUE constraints automatically encrypt column data.",
            "PRIMARY KEYs are only supported in MySQL, not PostgreSQL."
        ],
        "correct_option_index": 1,
        "explanation": "A table can define only one PRIMARY KEY, which enforces both uniqueness and NOT NULL on its columns. Multiple UNIQUE constraints can exist per table, and in standard SQL, UNIQUE columns permit NULL values (as NULL != NULL)."
    },
    {
        "difficulty": "basic",
        "topic": "DDL vs DML",
        "prompt_text": "Which of the following SQL statements is categorized as Data Definition Language (DDL)?",
        "code_snippet": None,
        "options": [
            "UPDATE users SET status = 'active';",
            "INSERT INTO audit_logs VALUES (1, 'Login');",
            "ALTER TABLE accounts ADD COLUMN balance NUMERIC(10, 2);",
            "DELETE FROM sessions WHERE expired = true;"
        ],
        "correct_option_index": 2,
        "explanation": "DDL (Data Definition Language) statements modify database structure and schema (CREATE, ALTER, DROP, TRUNCATE). UPDATE, INSERT, and DELETE are DML (Data Manipulation Language) statements."
    },
    {
        "difficulty": "basic",
        "topic": "Null Handling & Three-Valued Logic",
        "prompt_text": "What will the query `SELECT * FROM candidates WHERE score = NULL;` return?",
        "code_snippet": "SELECT * FROM candidates WHERE score = NULL;",
        "options": [
            "All candidates whose score is NULL.",
            "All candidates whose score is 0.",
            "An empty result set (zero rows) because comparisons with NULL using '=' evaluate to UNKNOWN in SQL three-valued logic.",
            "A SyntaxError exception."
        ],
        "correct_option_index": 2,
        "explanation": "In SQL three-valued logic (TRUE, FALSE, UNKNOWN), any comparison with NULL using equality operators (`= NULL` or `<> NULL`) yields UNKNOWN (falsy in WHERE filters). The proper syntax is `IS NULL`."
    },
    {
        "difficulty": "basic",
        "topic": "Aggregate Functions & Group By",
        "prompt_text": "What is the fundamental difference between WHERE and HAVING clauses in SQL?",
        "code_snippet": "SELECT department_id, AVG(salary)\nFROM employees\nWHERE status = 'active'\nGROUP BY department_id\nHAVING AVG(salary) > 80000;",
        "options": [
            "WHERE and HAVING are completely identical aliases.",
            "WHERE filters individual rows before grouping occurs; HAVING filters aggregated groups after the GROUP BY clause is evaluated.",
            "HAVING can only be used with primary key columns.",
            "WHERE cannot use comparison operators like '>' or '<'."
        ],
        "correct_option_index": 1,
        "explanation": "WHERE filters base rows prior to aggregation and cannot reference aggregate functions. HAVING filters aggregated group results produced by GROUP BY."
    },
    {
        "difficulty": "basic",
        "topic": "Joins: Inner vs Left",
        "prompt_text": "What does a LEFT OUTER JOIN return when a row in the left table has no matching row in the right table?",
        "code_snippet": None,
        "options": [
            "The row from the left table is omitted from the result set entirely.",
            "The row from the left table is included with NULL values for all columns from the right table.",
            "The query terminates with a Foreign Key Violation error.",
            "The row from the left table is duplicated 10 times."
        ],
        "correct_option_index": 1,
        "explanation": "A LEFT OUTER JOIN preserves all rows from the left table. If no match exists in the right table, columns belonging to the right table are populated with NULLs."
    },
    {
        "difficulty": "basic",
        "topic": "Set Operations: UNION vs UNION ALL",
        "prompt_text": "Why is `UNION ALL` typically faster than `UNION` when combining two query results?",
        "code_snippet": None,
        "options": [
            "UNION ALL compresses rows in memory.",
            "UNION automatically executes an expensive deduplication step (sort or hash) to eliminate duplicate rows, while UNION ALL concatenates results directly without deduplication.",
            "UNION ALL executes queries concurrently across multiple database servers.",
            "UNION ALL converts strings to binary numbers."
        ],
        "correct_option_index": 1,
        "explanation": "`UNION` deduplicates rows between queries, requiring sorting or hashing all rows. `UNION ALL` retains all rows including duplicates, skipping sorting/deduplication and running significantly faster."
    },
    {
        "difficulty": "basic",
        "topic": "Filtering & LIKE Pattern Matching",
        "prompt_text": "In SQL LIKE clauses, what does the percent sign (%) wildcard match?",
        "code_snippet": "SELECT * FROM users WHERE email LIKE 'admin%@coachpath.dev';",
        "options": [
            "Exactly one single character.",
            "Zero, one, or multiple arbitrary characters.",
            "Only numeric digits.",
            "Only ASCII whitespace characters."
        ],
        "correct_option_index": 1,
        "explanation": "In standard SQL LIKE patterns, `%` matches zero or more arbitrary characters, while `_` (underscore) matches exactly one character."
    },
    {
        "difficulty": "basic",
        "topic": "COALESCE Function",
        "prompt_text": "What does the function `COALESCE(col1, col2, 'Default')` return?",
        "code_snippet": None,
        "options": [
            "A concatenated string of all three values.",
            "The first non-NULL expression among its arguments from left to right.",
            "The largest alphabetical string among the arguments.",
            "A boolean indicating whether any argument is NULL."
        ],
        "correct_option_index": 1,
        "explanation": "COALESCE evaluates its arguments in order and returns the current value of the first expression that is not NULL. If all arguments are NULL, it returns NULL."
    },
    {
        "difficulty": "basic",
        "topic": "Sorting & Ordering",
        "prompt_text": "In standard PostgreSQL, where do NULL values appear by default in an `ORDER BY salary DESC` clause?",
        "code_snippet": "SELECT name, salary FROM staff ORDER BY salary DESC;",
        "options": [
            "At the very top (first) of the result set.",
            "At the very bottom (last) of the result set.",
            "They are excluded from the result set.",
            "In random positions throughout the rows."
        ],
        "correct_option_index": 0,
        "explanation": "In PostgreSQL, NULLs are treated as larger than any non-null value by default. In DESC order, NULLs sort first (`NULLS FIRST`), unless overridden with `NULLS LAST`."
    },
    {
        "difficulty": "basic",
        "topic": "Pagination: LIMIT and OFFSET",
        "prompt_text": "What is a major scalability drawback of using large OFFSET values (e.g., `LIMIT 20 OFFSET 500000`) for deep database pagination?",
        "code_snippet": None,
        "options": [
            "Database connections are forcibly closed after offset 10,000.",
            "The database engine must scan and discard 500,000 rows from disk/index before returning the requested 20 rows, resulting in high I/O and latency.",
            "OFFSET values cannot exceed 32,767 in SQL.",
            "OFFSET modifies the underlying table row order permanently."
        ],
        "correct_option_index": 1,
        "explanation": "OFFSET pagination forces the database to scan, order, and discard all preceding offset rows before yielding the page, scaling in O(OFFSET) time. Keyset/cursor-based pagination (`WHERE id > last_seen_id LIMIT 20`) is vastly superior for deep pagination."
    },

    # ─── INTERMEDIATE (10 Questions) ────────────────────────────────────
    {
        "difficulty": "intermediate",
        "topic": "Window Functions: ROW_NUMBER vs RANK vs DENSE_RANK",
        "prompt_text": "If three candidates tie for score 95 at the top of a list, what ranks are assigned by ROW_NUMBER(), RANK(), and DENSE_RANK() for those three and the next candidate with score 90?",
        "code_snippet": None,
        "options": [
            "ROW_NUMBER: 1, 2, 3, 4; RANK: 1, 1, 1, 4; DENSE_RANK: 1, 1, 1, 2",
            "ROW_NUMBER: 1, 1, 1, 2; RANK: 1, 2, 3, 4; DENSE_RANK: 1, 1, 1, 4",
            "All three produce 1, 1, 1, 2",
            "All three produce 1, 2, 3, 4"
        ],
        "correct_option_index": 0,
        "explanation": "ROW_NUMBER() assigns consecutive distinct numbers (1,2,3,4). RANK() gives tied items the same rank and skips ranks (1,1,1, then 4). DENSE_RANK() gives tied items the same rank without gaps (1,1,1, then 2)."
    },
    {
        "difficulty": "intermediate",
        "topic": "Common Table Expressions (CTEs)",
        "prompt_text": "What is the primary architectural purpose of a `WITH RECURSIVE` CTE in SQL?",
        "code_snippet": "WITH RECURSIVE org_tree AS (\n    SELECT id, manager_id, 1 as level FROM employees WHERE manager_id IS NULL\n    UNION ALL\n    SELECT e.id, e.manager_id, o.level + 1 FROM employees e JOIN org_tree o ON e.manager_id = o.id\n)\nSELECT * FROM org_tree;",
        "options": [
            "To parallelize query execution across background thread pools.",
            "To query hierarchical, tree-structured, or graph data (such as org charts or bill-of-materials) by repeatedly joining intermediate iterations until a fixed-point is reached.",
            "To create temporary tables stored in Redis.",
            "To loop through procedural PL/pgSQL cursors."
        ],
        "correct_option_index": 1,
        "explanation": "Recursive CTEs (`WITH RECURSIVE`) enable querying hierarchical and recursive relationships in pure declarative SQL. An anchor member query seeds the initial set, and a recursive member iterates until no new rows are produced."
    },
    {
        "difficulty": "intermediate",
        "topic": "Database Normalization (3NF & BCNF)",
        "prompt_text": "A table in 2nd Normal Form (2NF) violates 3rd Normal Form (3NF) if it contains which type of dependency?",
        "code_snippet": None,
        "options": [
            "Multi-valued dependencies.",
            "Transitive dependencies (a non-prime attribute determines another non-prime attribute: X -> Y where Y depends on X, and X depends on the primary key).",
            "Partial functional dependencies on a composite candidate key.",
            "Foreign keys pointing to tables in different schemas."
        ],
        "correct_option_index": 1,
        "explanation": "A relation is in 3NF if it is in 2NF and every non-key attribute is non-transitively dependent on the primary key. If non-key attribute A determines non-key attribute B (transitive dependency), it violates 3NF."
    },
    {
        "difficulty": "intermediate",
        "topic": "Indexes: B-Tree Mechanics",
        "prompt_text": "Why are B-Trees the standard default index structure across relational database management systems?",
        "code_snippet": None,
        "options": [
            "They only support exact equality lookups and consume zero disk space.",
            "They maintain sorted order with balanced node depth, providing efficient O(log n) performance for exact lookups, range scans (BETWEEN, <, >), prefix matching, and ORDER BY queries.",
            "They eliminate database write operations.",
            "They store complete table backups in CPU registers."
        ],
        "correct_option_index": 1,
        "explanation": "B-Trees keep data sorted and self-balanced with high branching factor (fan-out), minimizing disk I/O. They efficiently support exact matches, range queries, inequality searches, sorting, and MIN/MAX lookups."
    },
    {
        "difficulty": "intermediate",
        "topic": "Composite Indexes & Leftmost Prefix Rule",
        "prompt_text": "Given a composite index on `(last_name, first_name, date_of_birth)`, which of the following WHERE clauses CANNOT utilize this index effectively?",
        "code_snippet": None,
        "options": [
            "WHERE last_name = 'Smith'",
            "WHERE last_name = 'Smith' AND first_name = 'Alice'",
            "WHERE first_name = 'Alice' AND date_of_birth = '1995-05-12'",
            "WHERE last_name = 'Smith' AND date_of_birth = '1995-05-12'"
        ],
        "correct_option_index": 2,
        "explanation": "B-Tree composite indexes require queries to filter on the leftmost prefix of index columns. A query filtering only on `first_name` and `date_of_birth` omits the leading column `last_name`, preventing an index seek."
    },
    {
        "difficulty": "intermediate",
        "topic": "Views vs Materialized Views",
        "prompt_text": "What is the key performance trade-off between a standard SQL VIEW and a MATERIALIZED VIEW?",
        "code_snippet": None,
        "options": [
            "Standard views store results on disk; materialized views are virtual queries.",
            "A standard view executes its underlying query dynamically on every invocation; a materialized view persists query results physically on disk, offering fast reads at the cost of storage and required periodic refreshes.",
            "Materialized views cannot be indexed.",
            "Standard views can only contain 100 rows."
        ],
        "correct_option_index": 1,
        "explanation": "A standard VIEW is a stored query run dynamically whenever queried. A MATERIALIZED VIEW caches the result set on disk as a table that can be indexed, but requires explicit refresh (`REFRESH MATERIALIZED VIEW`) as underlying data changes."
    },
    {
        "difficulty": "intermediate",
        "topic": "ACID Properties: Durability",
        "prompt_text": "How does a relational database guarantee Durability when a transaction commits?",
        "code_snippet": None,
        "options": [
            "By writing dirty data pages to the OS virtual memory pagefile.",
            "By synchronously flushing the transaction's changes to non-volatile storage in a Write-Ahead Log (WAL) / redo log before returning success to the client.",
            "By keeping all committed data solely in RAM caches.",
            "By sending email notifications to database administrators."
        ],
        "correct_option_index": 1,
        "explanation": "Durability guarantees that committed data survives power losses and crashes. This is achieved by flushing log records to the Write-Ahead Log (WAL / redo log) on persistent storage via fsync before acknowledging commit."
    },
    {
        "difficulty": "intermediate",
        "topic": "Subqueries: Correlated vs Non-Correlated",
        "prompt_text": "What makes a subquery 'correlated' in SQL?",
        "code_snippet": "SELECT e.name, e.salary\nFROM employees e\nWHERE e.salary > (\n    SELECT AVG(salary) FROM employees WHERE department_id = e.department_id\n);",
        "options": [
            "The subquery is executed only once and cached for the entire query.",
            "The subquery references column values from the outer query, meaning it conceptually evaluates for each candidate row processed by the outer query.",
            "The subquery creates a temporary table on disk.",
            "The subquery is executed asynchronously in the background."
        ],
        "correct_option_index": 1,
        "explanation": "A correlated subquery references columns from the outer query (`e.department_id`). It depends on the current outer row and cannot be evaluated independently as a standalone query."
    },
    {
        "difficulty": "intermediate",
        "topic": "Window Functions: LEAD and LAG",
        "prompt_text": "What does the `LAG(revenue, 1) OVER (ORDER BY quarter)` window function return for each row?",
        "code_snippet": "SELECT quarter, revenue,\n       revenue - LAG(revenue, 1) OVER (ORDER BY quarter) as revenue_growth\nFROM quarterly_sales;",
        "options": [
            "The revenue from the immediately preceding row in the specified sort order.",
            "The revenue from the immediately following row.",
            "The average revenue across all quarters.",
            "The percentage variance of revenue from the mean."
        ],
        "correct_option_index": 0,
        "explanation": "LAG(column, offset) accesses data from a preceding row at a given physical offset prior to the current row in the window partition, making it standard for period-over-period delta calculations."
    },
    {
        "difficulty": "intermediate",
        "topic": "Foreign Keys & Cascading Deletes",
        "prompt_text": "What happens when a referenced parent row is deleted in a table with a foreign key defined as `ON DELETE CASCADE`?",
        "code_snippet": "CREATE TABLE orders (\n    id UUID PRIMARY KEY,\n    user_id UUID REFERENCES users(id) ON DELETE CASCADE\n);",
        "options": [
            "The database rejects the parent deletion and throws a ForeignKeyConstraintViolation.",
            "All child rows in the orders table referencing the deleted user_id are automatically and atomically deleted.",
            "The child rows have their user_id set to NULL.",
            "The parent row is flagged as archived without modifying the orders table."
        ],
        "correct_option_index": 1,
        "explanation": "`ON DELETE CASCADE` specifies that deleting a record in the referenced parent table automatically cascades to delete all child rows that reference that parent record."
    },

    # ─── ADVANCED (10 Questions) ─────────────────────────────────────────
    {
        "difficulty": "advanced",
        "topic": "Transaction Isolation Levels & Concurrency Anomalies",
        "prompt_text": "What concurrency anomaly can still occur under REPEATABLE READ isolation in standard SQL that is only prevented by SERIALIZABLE isolation?",
        "code_snippet": None,
        "options": [
            "Dirty Reads (reading uncommitted data).",
            "Non-Repeatable Reads (re-reading a modified row sees changed values).",
            "Phantom Reads (a transaction queries rows matching a condition, and a concurrent transaction inserts new matching rows that appear upon re-query) and Write Skew.",
            "Lost updates on primary keys."
        ],
        "correct_option_index": 2,
        "explanation": "Repeatable Read prevents Dirty Reads and Non-Repeatable Reads. However, it permits Phantom Reads (concurrent inserts matching predicate ranges) in ANSI SQL, as well as Write Skew. Serializable eliminates all concurrency anomalies."
    },
    {
        "difficulty": "advanced",
        "topic": "MVCC (Multi-Version Concurrency Control)",
        "prompt_text": "How does PostgreSQL's MVCC implementation enable high-concurrency readers to proceed without blocking writers, and vice-versa?",
        "code_snippet": None,
        "options": [
            "By taking exclusive table locks on every transaction.",
            "By maintaining multiple physical row versions (tuples) tagged with transaction visibility IDs (xmin and xmax), allowing readers to view a consistent snapshot corresponding to their transaction start point.",
            "By duplicating the entire database cluster for each connected client.",
            "By queueing all read queries in an asynchronous Redis cache."
        ],
        "correct_option_index": 1,
        "explanation": "Under MVCC, an UPDATE inserts a new tuple with current xmin and marks the old tuple with xmax. Readers read the snapshot version valid for their transaction without acquiring read locks, so readers never block writers and writers never block readers."
    },
    {
        "difficulty": "advanced",
        "topic": "Query Optimization: EXPLAIN ANALYZE Interpretation",
        "prompt_text": "In PostgreSQL EXPLAIN ANALYZE output, what does a 'Bitmap Index Scan' followed by a 'Bitmap Heap Scan' indicate?",
        "code_snippet": "-> Bitmap Heap Scan on orders (cost=4.20..15.30 rows=5 ...)\n   -> Bitmap Index Scan on idx_orders_status (cost=0.00..4.20 rows=5 ...)",
        "options": [
            "The index is corrupted and requires a REINDEX operation.",
            "The database scans the index to build an in-memory bitmap of matching physical page addresses, and then visits the heap pages in physical disk order to minimize random I/O.",
            "The query was rejected by the query planner and executed sequentially.",
            "The table has been converted into a bitmap image file."
        ],
        "correct_option_index": 1,
        "explanation": "Bitmap scans bridge the gap between sequential scans and index scans. The Bitmap Index Scan inspects the index and records matching block/offset locations in a memory bitmap; the Bitmap Heap Scan then reads table pages sequentially, avoiding scattered random disk seeks."
    },
    {
        "difficulty": "advanced",
        "topic": "Locking: Pessimistic vs Optimistic",
        "prompt_text": "What SQL clause implements pessimistic row-level locking during a read operation to prevent concurrent modifications until transaction commit?",
        "code_snippet": "SELECT * FROM bank_accounts WHERE id = 101 ...;",
        "options": [
            "LOCK IN SNAPSHOT MODE",
            "FOR UPDATE",
            "WITH LOCKING LEVEL 5",
            "PREVENT CONCURRENT MODIFICATION"
        ],
        "correct_option_index": 1,
        "explanation": "`SELECT ... FOR UPDATE` locks the selected rows against concurrent updates, deletes, or other FOR UPDATE locks until the holding transaction terminates (COMMIT or ROLLBACK)."
    },
    {
        "difficulty": "advanced",
        "topic": "PostgreSQL Vacuuming & Table Bloat",
        "prompt_text": "Why is the VACUUM process critical in PostgreSQL database maintenance?",
        "code_snippet": None,
        "options": [
            "To compress text columns using LZ4 compression.",
            "To reclaim dead tuples left behind by UPDATE and DELETE operations and freeze transaction IDs to prevent 32-bit transaction wraparound failure.",
            "To remove unindexed tables from memory.",
            "To purge SQL query logs older than 7 days."
        ],
        "correct_option_index": 1,
        "explanation": "Because PostgreSQL MVCC leaves old row versions (dead tuples) in place during UPDATE and DELETE, VACUUM removes dead tuples so their space can be reused for new rows, and advances the transaction ID horizon to prevent transaction ID wraparound."
    },
    {
        "difficulty": "advanced",
        "topic": "Covering Indexes & Index-Only Scans",
        "prompt_text": "How does a covering index created with the `INCLUDE` clause (e.g., `CREATE INDEX idx ON orders (user_id) INCLUDE (total_amount)`) optimize query execution?",
        "code_snippet": "SELECT total_amount FROM orders WHERE user_id = 'c8b2...';",
        "options": [
            "It turns total_amount into a primary key.",
            "It stores total_amount in the B-Tree leaf nodes without adding it to the search tree key, allowing an Index-Only Scan that satisfies the query without visiting the table heap pages.",
            "It automatically recalculates total_amount on each read.",
            "It enforces unique constraints across both columns."
        ],
        "correct_option_index": 1,
        "explanation": "The `INCLUDE` clause appends non-key payload columns strictly to the leaf pages of the B-Tree index. Queries that need those columns can be satisfied entirely from the index (Index-Only Scan) without accessing table heap pages."
    },
    {
        "difficulty": "advanced",
        "topic": "Table Partitioning Strategies",
        "prompt_text": "In declarative table partitioning in PostgreSQL, what is 'partition pruning'?",
        "code_snippet": "CREATE TABLE events (...) PARTITION BY RANGE (event_date);",
        "options": [
            "Dropping partitions when disk usage exceeds 90%.",
            "The query planner's optimization where constraints on the partition key allow queries to skip scanning irrelevant partition tables entirely.",
            "Archiving old partitions to AWS S3 automatically.",
            "Truncating partitions that contain NULL values."
        ],
        "correct_option_index": 1,
        "explanation": "Partition pruning is an optimizer feature where the query planner analyzes WHERE clauses on the partition key to exclude (prune) partition tables that cannot possibly contain matching records, drastically reducing I/O."
    },
    {
        "difficulty": "advanced",
        "topic": "Write Skew Anomaly",
        "prompt_text": "What is the 'Write Skew' anomaly that occurs under Snapshot Isolation (Repeatable Read)?",
        "code_snippet": "-- Scenario: At least one doctor must be on call.\n-- T1 and T2 both see 2 doctors on call concurrently, and each takes their own doctor off call.\n-- Result: 0 doctors on call!",
        "options": [
            "Two transactions overwrite the exact same row concurrently.",
            "Two concurrent transactions read overlapping data sets satisfying an invariant, and each makes disjoint updates that individually preserve the invariant but collectively violate it.",
            "A hard drive failure during a write operation.",
            "Writing to a read replica instead of the primary database."
        ],
        "correct_option_index": 1,
        "explanation": "Write skew occurs when two concurrent transactions read overlapping state, make disjoint writes that each satisfy business rules in their snapshot, but the combination violates a system invariant. It is only prevented by Serializable isolation."
    },
    {
        "difficulty": "advanced",
        "topic": "Deadlocks & Graph Cycles",
        "prompt_text": "How does a database engine identify deadlocks between concurrent transactions?",
        "code_snippet": None,
        "options": [
            "By timing out any query that takes more than 1 second.",
            "By periodically constructing a Directed Wait-For Graph of transactions and locks, and detecting cycles in the graph (e.g. via Tarjan's algorithm), aborting one transaction to break the cycle.",
            "By rejecting transactions that modify more than 10 rows.",
            "By restarting the entire database server."
        ],
        "correct_option_index": 1,
        "explanation": "The database lock manager maintains a 'Wait-For Graph' where nodes are transactions and edges represent lock dependencies. A cycle in this graph indicates a deadlock. The engine aborts/rolls back a designated victim transaction to resolve the cycle."
    },
    {
        "difficulty": "advanced",
        "topic": "Connection Pooling & Architecture",
        "prompt_text": "Why is deploying an external connection pooler like PgBouncer in transaction pooling mode essential for scaling PostgreSQL to tens of thousands of client connections?",
        "code_snippet": None,
        "options": [
            "PostgreSQL natively supports only 10 connections.",
            "PostgreSQL uses a process-per-connection architecture where each active connection consumes 5-10MB of RAM and incurs OS context-switching overhead; transaction pooling multiplexes thousands of frontend connections onto a small pool of backend server processes.",
            "PgBouncer translates SQL queries into NoSQL JSON documents.",
            "PgBouncer compresses TCP network packets using SSL encryption."
        ],
        "correct_option_index": 1,
        "explanation": "PostgreSQL forks an OS process per client connection. Thousands of idle or active client connections cause severe memory overhead, cache thrashing, and context-switching bottlenecks. PgBouncer multiplexes client transactions onto a compact pool (e.g., 50-100) of backend processes."
    }
]
