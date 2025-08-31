from abc import abstractmethod
from typing import Protocol

class ISmtpClient(Protocol):
    @abstractmethod
    def send_message(self, recipient_email: str, text: str): pass
