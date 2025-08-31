create_userbot = """
INSERT INTO userbots (tg_user_id, session_string, tg_phone_number)
VALUES (:tg_user_id, :session_string, :tg_phone_number)
RETURNING tg_user_id;
"""

userbot_by_tg_user_id = """
SELECT * FROM userbots
WHERE tg_user_id=:tg_user_id;
"""

userbot_by_amocrm_external_id = """
SELECT * FROM userbots
WHERE amocrm_external_id=:amocrm_external_id;
"""

all_userbot = """
SELECT * FROM userbots;
"""
