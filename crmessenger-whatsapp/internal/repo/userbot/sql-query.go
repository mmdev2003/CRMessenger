package userbot

const CreateUserbot = `
INSERT INTO userbot (wa_phone_number, account_id)
VALUES (@wa_phone_number, @account_id)
RETURNING wa_phone_number;
`
