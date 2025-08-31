package amocrm

import (
	"bytes"
	"context"
	"crmessenger-whatsapp/internal/model"
	"crypto/hmac"
	"crypto/md5"
	"crypto/sha1"
	"encoding/hex"
	"encoding/json"
	"errors"
	"fmt"
	"github.com/google/uuid"
	"io"
	"log/slog"
	"net/http"
	"time"
	_ "time/tzdata"
)

func New(
	baseURL,
	apiChatURL,
	messenger,
	botName,
	amocrmBotID,
	amocrmChannelSecret,
	amocrmChannelID,
	amocrmChannelCode string,
) *AmocrmClient {
	return &AmocrmClient{
		baseURL:             baseURL,
		apiChatURL:          apiChatURL,
		messenger:           messenger,
		botName:             botName,
		amocrmBotID:         amocrmBotID,
		amocrmChannelSecret: amocrmChannelSecret,
		amocrmChannelID:     amocrmChannelID,
		amocrmChannelCode:   amocrmChannelCode,
	}
}

type AmocrmClient struct {
	baseURL             string
	apiChatURL          string
	messenger           string
	botName             string
	amocrmBotID         string
	amocrmChannelSecret string
	amocrmChannelID     string
	amocrmChannelCode   string
}

func (c *AmocrmClient) CreateSource(ctx context.Context,
	amocrmPipelineID int,
	sourceName,
	amocrmExternalID,
	amocrmToken,
	amocrmSubdomain string,
) (int, error) {
	body := []map[string]any{
		{
			"name":        sourceName,
			"pipeline_id": amocrmPipelineID,
			"external_id": amocrmExternalID,
			"default":     false,
			"origin_code": c.amocrmChannelCode,
		},
	}

	url := fmt.Sprintf("https://%s/sources", amocrmSubdomain+c.baseURL)
	result, err := c.requestSubdomain(ctx, amocrmToken, url, "POST", body)
	if err != nil {
		return 0, err
	}

	embedded := result["_embedded"].(map[string]any)
	sources := embedded["sources"].([]any)
	source := sources[0].(map[string]any)
	amocrmSourceID := int(source["id"].(float64))
	return amocrmSourceID, nil
}

func (c *AmocrmClient) ConnectChannelToAccount(ctx context.Context,
	amocrmToken,
	amocrmSubdomain string,
) (string, error) {
	url := fmt.Sprintf("https://%s/account?with=amojo_id", amocrmSubdomain+c.baseURL)
	result, err := c.requestSubdomain(ctx, amocrmToken, url, "GET", nil)
	if err != nil {
		return "", err
	}

	amojoID := result["amojo_id"].(string)
	body := map[string]any{
		"account_id":       amojoID,
		"title":            c.messenger,
		"hook_api_version": "v2",
	}

	path := fmt.Sprintf("/%s/connect", c.amocrmChannelID)
	result, err = c.requestApiChats(ctx, body, path, "POST")
	if err != nil {
		return "", err
	}

	return result["scope_id"].(string), nil
}

func (c *AmocrmClient) CreateContact(ctx context.Context,
	amocrmToken,
	amocrmSubdomain,
	contactPhoneNumber,
	contactName string,
) (int, error) {
	body := []map[string]any{
		{
			"name": contactName,
			"custom_fields_values": []map[string]any{
				{
					"field_code": "PHONE",
					"values": []map[string]string{
						{
							"value": contactPhoneNumber,
						},
					},
				},
			},
		},
	}

	url := fmt.Sprintf("https://%s/contacts", amocrmSubdomain+c.baseURL)
	result, err := c.requestSubdomain(ctx, amocrmToken, url, "POST", body)
	if err != nil {
		return 0, err
	}

	embedded, ok := result["_embedded"].(map[string]any)
	if !ok {
		return 0, fmt.Errorf("missing _embedded in response")
	}

	contacts, ok := embedded["contacts"].([]any)
	if !ok || len(contacts) == 0 {
		return 0, fmt.Errorf("no contacts returned")
	}

	contact := contacts[0].(map[string]any)
	amocrmContactID, ok := contact["id"].(float64)
	if !ok {
		return 0, fmt.Errorf("invalid contact ID")
	}

	return int(amocrmContactID), nil
}

func (c *AmocrmClient) CreateLead(ctx context.Context,
	amocrmToken,
	amocrmSubdomain string,
	amocrmContactID,
	amocrmPipelineID int,
) (int, error) {
	body := []map[string]any{
		{
			"pipeline_id": amocrmPipelineID,
			"_embedded": map[string][]map[string]int{
				"contacts": {
					{"id": amocrmContactID},
				},
			},
		},
	}

	url := fmt.Sprintf("https://%s/leads", amocrmSubdomain+c.baseURL)
	result, err := c.requestSubdomain(ctx, amocrmToken, url, "POST", body)
	if err != nil {
		return 0, err
	}

	embedded := result["_embedded"].(map[string]any)
	leads := embedded["leads"].([]any)
	lead := leads[0].(map[string]any)
	return int(lead["id"].(float64)), nil
}

func (c *AmocrmClient) UpdateMessageStatus(
	ctx context.Context,
	status int,
	amocrmMessageID,
	amocrmScopeID string,
) error {
	body := map[string]any{
		"msgid":           amocrmMessageID,
		"delivery_status": status,
	}

	path := fmt.Sprintf("/%s/%s/delivery_status", amocrmScopeID, amocrmMessageID)

	_, err := c.requestApiChats(ctx, body, path, "POST")
	return err
}

func (c *AmocrmClient) CreateChat(ctx context.Context,
	amocrmContactID int,
	amocrmConversationID,
	amocrmScopeID,
	contactName string,
) (string, error) {
	body := map[string]any{
		"conversation_id": amocrmConversationID,
		"user": map[string]string{
			"id":   fmt.Sprintf("%d", amocrmContactID),
			"name": contactName,
		},
	}

	path := fmt.Sprintf("/%s/chats", amocrmScopeID)

	response, err := c.requestApiChats(ctx, body, path, "POST")
	if err != nil {
		return "", err
	}

	amocrmChatID, ok := response["id"].(string)
	if !ok {
		return "", fmt.Errorf("failed to get chat ID from response")
	}

	return amocrmChatID, nil
}

func (c *AmocrmClient) AssignChatToContact(ctx context.Context,
	amocrmToken string,
	amocrmSubdomain string,
	amocrmChatID string,
	amocrmContactID int,
) error {
	body := []map[string]any{
		{
			"contact_id": amocrmContactID,
			"chat_id":    amocrmChatID,
		},
	}

	url := fmt.Sprintf("https://%s/contacts/chats", amocrmSubdomain+c.baseURL)
	_, err := c.requestSubdomain(ctx, amocrmToken, url, "POST", body)
	if err != nil {
		return err
	}

	return nil
}

func (c *AmocrmClient) ImportMessageFromUserbotToAmocrm(ctx context.Context,
	amocrmContactID int,
	amocrmConversationID,
	amocrmChatID,
	amocrmExternalID,
	amocrmScopeID,
	contactName,
	text string,
) (string, error) {
	payload := map[string]any{
		"event_type": "new_message",
		"payload": map[string]any{
			"timestamp":           time.Now().Unix(),
			"msec_timestamp":      time.Now().UnixMilli(),
			"msgid":               uuid.New().String(),
			"conversation_id":     amocrmConversationID,
			"conversation_ref_id": amocrmChatID,
			"sender": map[string]any{
				"id":     uuid.New().String(),
				"name":   c.botName,
				"ref_id": c.amocrmBotID,
			},
			"receiver": map[string]any{
				"id":   fmt.Sprintf("%d", amocrmContactID),
				"name": contactName,
			},
			"message": map[string]any{
				"type": "text",
				"text": text,
			},
			"silent": true,
			"source": map[string]any{
				"external_id": amocrmExternalID,
			},
		},
	}

	path := fmt.Sprintf("/%s", amocrmScopeID)
	response, err := c.requestApiChats(ctx, payload, path, "POST")
	if err != nil {
		return "", fmt.Errorf("failed to send message: %w", err)
	}

	newMessage, ok := response["new_message"].(map[string]any)
	if !ok {
		return "", fmt.Errorf("invalid response format - missing new_message")
	}

	amocrmMessageID, ok := newMessage["msgid"].(string)
	if !ok {
		return "", fmt.Errorf("invalid response format - missing msgid")
	}

	return amocrmMessageID, nil
}

func (c *AmocrmClient) SendMessageFromContact(ctx context.Context,
	amocrmContactID int,
	amocrmConversationID,
	amocrmChatID,
	amocrmExternalID,
	amocrmScopeID,
	contactName,
	text string,
) (string, error) {
	msgID := uuid.New().String()
	body := map[string]interface{}{
		"event_type": "new_message",
		"payload": map[string]interface{}{
			"timestamp":           time.Now().Unix(),
			"msec_timestamp":      time.Now().UnixMilli(),
			"msgid":               msgID,
			"conversation_id":     amocrmConversationID,
			"conversation_ref_id": amocrmChatID,
			"sender": map[string]string{
				"id":   fmt.Sprintf("%d", amocrmContactID),
				"name": contactName,
			},
			"message": map[string]string{
				"type": "text",
				"text": text,
			},
			"silent": true,
			"source": map[string]string{
				"external_id": amocrmExternalID,
			},
		},
	}

	path := fmt.Sprintf("/%s", amocrmScopeID)
	result, err := c.requestApiChats(ctx, body, path, "POST")
	if err != nil {
		return "", err
	}

	newMessage := result["new_message"].(map[string]any)
	return newMessage["msgid"].(string), nil
}

func (c *AmocrmClient) ContactIDByNameAndPhone(ctx context.Context,
	amocrmToken,
	amocrmSubdomain,
	amocrmContactName,
	amocrmContactPhone string,
) (int, error) {
	body := []map[string]any{
		{
			"filter": map[string]any{
				"name": amocrmContactName,
			},
		},
	}

	url := fmt.Sprintf("https://%s/contacts", amocrmSubdomain+c.baseURL)
	response, err := c.requestSubdomain(ctx, amocrmToken, url, "GET", body)
	if err != nil {
		return 0, err
	}

	contactsIFace := response["_embedded"].(map[string]any)["contacts"].([]interface{})
	contacts := make([]map[string]any, 0, len(contactsIFace))
	for _, c := range contactsIFace {
		contacts = append(contacts, c.(map[string]any))
	}
	for _, contact := range contacts {
		fmt.Println("я тут 1")
		customFieldsRaw, ok := contact["custom_fields_values"]
		if !ok || customFieldsRaw == nil {
			continue
		}

		customFields, ok := customFieldsRaw.([]interface{})
		if !ok {
			continue
		}

		for _, fieldRaw := range customFields {
			fmt.Println("я тут 2")
			field, ok := fieldRaw.(map[string]any)
			if !ok {
				continue
			}
			if field["field_code"] == "PHONE" {
				valuesRaw, ok := field["values"].([]interface{})
				if !ok {
					continue
				}
				for _, valueRaw := range valuesRaw {
					fmt.Println("я тут 3")
					value, ok := valueRaw.(map[string]any)
					if !ok {
						continue
					}
					phoneValue, ok := value["value"].(string)
					if ok {
						if phoneValue == amocrmContactPhone {
							contactID := int(contact["id"].(float64))
							return contactID, nil
						}
					}
				}
			}
		}
	}
	return 0, errors.New("contact not found")
}

func (c *AmocrmClient) DeleteSource(ctx context.Context,
	amocrmToken,
	amocrmSubdomain string,
	amocrmSourceID int,
) error {
	body := []map[string]int{
		{"id": amocrmSourceID},
	}

	url := fmt.Sprintf("https://%s%s/sources", amocrmSubdomain, c.baseURL)

	_, err := c.requestSubdomain(ctx, amocrmToken, url, "DELETE", body)
	return err
}

func (c *AmocrmClient) requestSubdomain(ctx context.Context,
	amocrmToken,
	url,
	httpMethod string,
	body any,
) (map[string]any, error) {
	logger := ctx.Value(model.LoggerKey).(*slog.Logger)

	jsonBody, err := json.Marshal(body)
	if err != nil {
		return nil, err
	}
	logger.Debug("AMOCRM subdomain",
		slog.String("url", url),
		slog.String("body", string(jsonBody)),
	)

	req, err := http.NewRequestWithContext(ctx, httpMethod, url, bytes.NewBuffer(jsonBody))
	if err != nil {
		return nil, err
	}

	req.Header.Set("Authorization", "Bearer "+amocrmToken)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{
		Timeout: 30 * time.Second,
	}

	resp, err := client.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	logger.Debug("AMOCRM subdomain response",
		slog.String("response", string(respBody)),
		slog.String("amocrm_url", url),
	)

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("HTTP request failed with status %d", resp.StatusCode)
	}

	var result map[string]any
	if err := json.Unmarshal(respBody, &result); err != nil {
		return nil, err
	}

	return result, nil
}

func (c *AmocrmClient) requestApiChats(ctx context.Context,
	body map[string]any,
	path,
	method string,
) (map[string]any, error) {
	logger := ctx.Value(model.LoggerKey).(*slog.Logger)

	bodyBytes, err := json.Marshal(body)
	logger.Debug("AMOCRM api chats request body",
		slog.String("body", string(bodyBytes)),
		slog.String("amocrm_path", path),
	)

	if err != nil {
		return nil, err
	}
	bodyChecksum := fmt.Sprintf("%x", md5.Sum(bodyBytes))
	//logger.Debug("api chats request body checksum", slog.String("bodyChecksum", string(bodyBytes)))

	loc, err := time.LoadLocation("Europe/Moscow")
	if err != nil {
		panic(err)
	}
	date := time.Now().In(loc).Format("Mon, 02 Jan 2006 15:04:05 -0700")

	signature := c.generateSignature(ctx, c.amocrmChannelSecret, bodyChecksum, path, date, method)
	headers := c.prepareHeaders(bodyChecksum, signature, date)
	//logger.Debug("api chats headers", slog.Any("headers", headers))

	req, err := http.NewRequestWithContext(ctx, method, c.apiChatURL+path, bytes.NewBuffer(bodyBytes))
	if err != nil {
		return nil, err
	}

	for k, v := range headers {
		req.Header.Set(k, v[0])
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}
	logger.Debug("AMOCRM api chats response",
		slog.String("amocrm_response", string(respBody)),
		slog.String("amocrm_path", path),
	)

	if resp.StatusCode < 200 || resp.StatusCode >= 300 {
		return nil, fmt.Errorf("HTTP request failed with status %d", resp.StatusCode)
	}

	var result map[string]any
	if err := json.Unmarshal(respBody, &result); err != nil {
		return nil, fmt.Errorf("failed to unmarshal response: %w", err)
	}

	return result, nil
}

func (c *AmocrmClient) generateSignature(ctx context.Context,
	secret string,
	bodyChecksum, path, date, method string,
) string {
	//logger := ctx.Value(model.LoggerKey).(*slog.Logger)

	stringToHash := fmt.Sprintf(
		"%s\n%s\napplication/json\n%s\n%s",
		method,
		bodyChecksum,
		date,
		"/v2/origin/custom"+path,
	)
	//logger.Debug("stringToHash", slog.String("stringToHash", stringToHash))

	h := hmac.New(sha1.New, []byte(secret))
	h.Write([]byte(stringToHash))
	signature := hex.EncodeToString(h.Sum(nil))
	//logger.Debug("signature", slog.String("signature", signature))

	return signature
}

func (c *AmocrmClient) prepareHeaders(bodyChecksum, signature, date string) http.Header {
	headers := http.Header{}
	headers.Set("Date", date)
	headers.Set("Content-Type", "application/json")
	headers.Set("Content-MD5", bodyChecksum)
	headers.Set("X-Signature", signature)
	return headers
}
