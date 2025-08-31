create_amocrm_source = """
INSERT INTO amocrm_sources (amocrm_source_id, userbot_tg_user_id, amocrm_pipeline_id, amocrm_external_id, amocrm_scope_id)
VALUES (:amocrm_source_id, :userbot_tg_user_id, :amocrm_pipeline_id, :amocrm_external_id, :amocrm_scope_id)
RETURNING amocrm_source_id;
"""

amocrm_source_by_userbot_tg_user_id = """
SELECT * FROM amocrm_sources 
WHERE userbot_tg_user_id=:userbot_tg_user_id
"""

amocrm_source_by_amocrm_external_id = """
SELECT * FROM amocrm_sources 
WHERE amocrm_external_id=:amocrm_external_id;
"""

create_chat = """
INSERT INTO amocrm_chats (contact_id, amocrm_conversation_id, amocrm_chat_id)
VAlUES (:contact_id, :amocrm_conversation_id, :amocrm_chat_id)
RETURNING id;
"""

chat_by_contact_id = """
SELECT * FROM amocrm_chats 
WHERE contact_id=:contact_id;
"""

chat_by_amocrm_chat_id = """
SELECT * FROM amocrm_chats 
WHERE amocrm_chat_id=:amocrm_chat_id;
"""

create_contact = """
INSERT INTO amocrm_contacts (first_name, last_name, tg_chat_id, amocrm_contact_id)
VALUES (:first_name, :last_name, :tg_chat_id, :amocrm_contact_id)
RETURNING id;
"""

contact_by_tg_chat_id = """
SELECT * FROM amocrm_contacts
WHERE tg_chat_id = :tg_chat_id;
"""

contact_by_id = """
SELECT * FROM amocrm_contacts
WHERE id = :contact_id;
"""

create_message = """
INSERT INTO amocrm_messages (chat_id, text, role, amocrm_message_id)
VALUES (:chat_id, :text, :role, :amocrm_message_id)
RETURNING id;
"""