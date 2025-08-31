from dataclasses import dataclass
from datetime import datetime


@dataclass
class AuthorizationDataDTO:
    account_id: int
    access_token: str
    refresh_token: str
