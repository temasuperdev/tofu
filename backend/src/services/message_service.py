from typing import Dict, Any
from ..models.message_model import Message
from datetime import datetime
from ..utils.logging_config import get_logger


class MessageService:
    def __init__(self):
        self.logger = get_logger(__name__)

    def process_message(self, content: str, pod_name: str) -> Dict[str, Any]:
        """
        Обработка сообщения
        """
        # Создаем объект сообщения
        message = Message(
            content=content.strip(),
            pod_name=pod_name
        )
        
        # Логируем обработку сообщения
        self.logger.info("Processing message", content=content[:50], truncated=len(content) > 50)
        
        # Возвращаем результат
        return {
            'success': True,
            'message': f'Сообщение получено: {message.content}',
            'processed_at': message.created_at.isoformat(),
            'pod': message.pod_name
        }