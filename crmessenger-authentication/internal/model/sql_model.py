create_account_table = """
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,

    email TEXT NOT NULL,
    password TEXT NOT NULL,
    
    two_fa_key TEXT DEFAULT '',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

on_update_table_query1 = """
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';
"""

on_update_table_query2 = """
CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON accounts
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

drop_account_table = """
DROP TABLE IF EXISTS accounts;
"""

create_queries = [
    create_account_table,
]

drop_queries = [
    drop_account_table
]