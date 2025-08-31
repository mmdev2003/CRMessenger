create_userbot_table = """
CREAtE TABLE IF NOT EXISTS userbots (
    tg_user_id BIGINT PRIMARY KEY,
    tg_phone_number TEXT NOT NULL,

    session_string TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_amocrm_source_table = """
CREAtE TABLE IF NOT EXISTS amocrm_sources (
    amocrm_source_id INTEGER PRIMARY KEY,

    userbot_tg_user_id BIGINT NOT NULL,
    
    amocrm_pipeline_id INTEGER NOT NULL,
    amocrm_external_id TEXT NOT NULL,
    amocrm_scope_id TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""


create_amocrm_contact_table = """
CREATE TABLE IF NOT EXISTS amocrm_contacts (
    id SERIAL PRIMARY KEY,
    
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    tg_chat_id BIGINT NOT NULL,
    
    amocrm_contact_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_amocrm_chat_table = """
CREATE TABLE IF NOT EXISTS amocrm_chats (
    id SERIAL PRIMARY KEY,
    
    contact_id INTEGER NOT NULL,
    amocrm_conversation_id TEXT NOT NULL,
    amocrm_chat_id TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
"""

create_amocrm_message_table = """
CREATE TABLE IF NOT EXISTS amocrm_messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    
    amocrm_message_id TEXT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    
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
BEFORE UPDATE ON amocrm_sources
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
"""

drop_userbot_table = """
DROP TABLE IF EXISTS userbots;
"""

drop_amocrm_sources_table = """
DROP TABLE IF EXISTS amocrm_sources;
"""

drop_amocrm_contact_table = """
DROP TABLE IF EXISTS amocrm_contacts;
"""

drop_amocrm_chat_table = """
DROP TABLE IF EXISTS amocrm_chats;
"""

drop_amocrm_message_table = """
DROP TABLE IF EXISTS amocrm_messages;
"""

create_queries = [
    create_amocrm_source_table,
    # create_userbot_table,
    create_amocrm_contact_table,
    create_amocrm_chat_table,
    create_amocrm_message_table,
    on_update_table_query1,
    on_update_table_query2
]

drop_queries = [
    # drop_userbot_table,
    drop_amocrm_contact_table,
    drop_amocrm_chat_table,
    drop_amocrm_message_table,
    drop_amocrm_sources_table
]