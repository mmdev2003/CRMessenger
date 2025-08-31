from pydantic import BaseModel

class CreateAmocrmAccountBody(BaseModel):
    amocrm_subdomain: str
    amocrm_token: str