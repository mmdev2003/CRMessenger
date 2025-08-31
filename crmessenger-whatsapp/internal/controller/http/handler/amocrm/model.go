package amocrm

type CreateAmocrmSourceBody struct {
	UserbotWaPhoneNumber string `json:"userbot_wa_phone_number"`
	AmocrmPipelineID     int    `json:"amocrm_pipeline_id"`
}

type TextMessageFromAmocrmBody struct {
	AccountID string `json:"account_id"`
	Message   struct {
		Receiver     map[string]any `json:"receiver"`
		Sender       map[string]any `json:"sender"`
		Source       map[string]any `json:"source"`
		Conversation struct {
			ID string `json:"id"`
		} `json:"conversation"`
		Message struct {
			ID   string `json:"id"`
			Text string `json:"text"`
		} `json:"message"`
	} `json:"message"`
}
