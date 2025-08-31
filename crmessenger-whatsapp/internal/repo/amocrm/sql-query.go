package amocrm

const CreateAmocrmSource = `
INSERT INTO amocrm_sources (amocrm_source_id, userbot_wa_phone_number, amocrm_pipeline_id, amocrm_external_id, amocrm_scope_id)
VALUES (@amocrm_source_id, @userbot_wa_phone_number, @amocrm_pipeline_id, @amocrm_external_id, @amocrm_scope_id)
RETURNING amocrm_source_id;
`

var AmocrmSourceByWaPhoneNumber = `
SELECT * FROM amocrm_sources
WHERE userbot_wa_phone_number = @userbot_wa_phone_number
`

const AmocrmSourceByExternalID = `
SELECT * FROM amocrm_sources 
WHERE amocrm_external_id = @amocrm_external_id;
`

const CreateChat = `
INSERT INTO amocrm_chats (contact_id, amocrm_conversation_id, amocrm_chat_id)
VALUES (@contact_id, @amocrm_conversation_id, @amocrm_chat_id)
RETURNING id;
`

const ChatByContactID = `
SELECT * FROM amocrm_chats 
WHERE contact_id = @contact_id;
`

const ChatByAmocrmChatID = `
SELECT * FROM amocrm_chats 
WHERE amocrm_chat_id = @amocrm_chat_id;
`

const CreateContact = `
INSERT INTO amocrm_contacts (wa_phone_number, amocrm_contact_id)
VALUES (@wa_phone_number, @amocrm_contact_id)
RETURNING id;
`

const ContactByWaPhoneNumber = `
SELECT * FROM amocrm_contacts
WHERE wa_phone_number = @wa_phone_number;
`

const ContactByID = `
SELECT * FROM amocrm_contacts
WHERE id = @contact_id;
`

const CreateMessage = `
INSERT INTO amocrm_messages (chat_id, text, role, amocrm_message_id)
VALUES (@chat_id, @text, @role, @amocrm_message_id)
RETURNING id;
`
