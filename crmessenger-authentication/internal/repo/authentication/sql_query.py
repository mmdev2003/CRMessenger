create_account = """
INSERT INTO accounts (email, password)
VALUES (:email, :password)
RETURNING id
"""

account_by_id = """
SELECT * FROM accounts 
WHERE id=:account_id
"""

account_by_email = """
SELECT * FROM accounts 
WHERE email=:email
"""

update_email_two_fa = """
UPDATE accounts
SET email_two_fa=:email_two_fa
WHERE id=:account_id
"""

set_two_fa_key = """
UPDATE accounts
SET two_fa_key=:two_fa_key
WHERE id=:account_id
"""

delete_two_fa_key = """
UPDATE accounts
SET two_fa_key= ''
WHERE id=:account_id
"""

update_password = """
UPDATE accounts
SET password=:new_password
WHERE id=:account_id
"""