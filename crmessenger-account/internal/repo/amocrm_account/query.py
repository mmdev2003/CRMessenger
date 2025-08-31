create_amocrm_account = """
INSERT INTO amocrm_accounts (account_id, amocrm_subdomain, amocrm_token)
VALUES (:account_id, :amocrm_subdomain, :amocrm_token)
RETURNING id
"""

amocrm_account_by_id = """
SELECT * FROM amocrm_accounts
WHERE id = :amocrm_account_id
"""