create_account = """
INSERT INTO accounts (id, login)
VALUES (:account_id, :login)
RETURNING id
"""

account_by_id = """
SELECT * FROM accounts
WHERE id = :account_id
"""