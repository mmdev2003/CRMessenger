package model

var CreateTable = `
CREATE TABLE IF NOT EXISTS userbots (
    wa_phone_number TEXT PRIMARY KEY,
    
    account_id TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS amocrm_sources (
    amocrm_source_id INTEGER PRIMARY KEY,

    userbot_wa_phone_number TEXT NOT NULL,
    
    amocrm_pipeline_id INTEGER NOT NULL,
    amocrm_external_id TEXT NOT NULL,
    amocrm_scope_id TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS amocrm_contacts(
    id SERIAL PRIMARY KEY,
    
    wa_phone_number TEXT NOT NULL,
    amocrm_contact_id INTEGER NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
       
CREATE TABLE IF NOT EXISTS amocrm_chats (
    id SERIAL PRIMARY KEY,
    
    contact_id INTEGER NOT NULL,
    amocrm_conversation_id TEXT NOT NULL,
    amocrm_chat_id TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS amocrm_messages (
    id SERIAL PRIMARY KEY,
    chat_id INTEGER NOT NULL,
    
    amocrm_message_id TEXT NOT NULL,
    role TEXT NOT NULL,
    text TEXT NOT NULL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE 'plpgsql';
   
CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON userbots
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON amocrm_sources
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON amocrm_chats
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON amocrm_messages
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();

CREATE TRIGGER update_updated_at_trigger
BEFORE UPDATE ON amocrm_contacts
FOR EACH ROW
EXECUTE PROCEDURE update_updated_at();
`

var DropTable = `
DROP TABLE IF EXISTS userbots;
DROP TABLE IF EXISTS amocrm_sources;
DROP TABLE IF EXISTS amocrm_contacts;
DROP TABLE IF EXISTS amocrm_chats;
DROP TABLE IF EXISTS amocrm_messages;
`
