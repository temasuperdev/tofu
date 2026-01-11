from typing import Optional
import re

def sanitize_html(content: str) -> str:
    """
    Очистка HTML-контента от потенциально опасных тегов и атрибутов
    """
    # Удаляем потенциально опасные теги
    dangerous_tags = ['script', 'iframe', 'embed', 'object', 'link', 'meta', 'base']
    
    for tag in dangerous_tags:
        # Удаляем открывающие и закрывающие теги
        content = re.sub(r'<\s*' + tag + r'\b[^>]*>', '', content, flags=re.IGNORECASE)
        content = re.sub(r'<\s*/\s*' + tag + r'\s*>', '', content, flags=re.IGNORECASE)
    
    # Удаляем опасные атрибуты
    dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover', 'onmouseout', 'onfocus', 'onblur']
    
    for attr in dangerous_attrs:
        pattern = r'\s*' + attr + r'\s*=\s*[\'"][^\'"]*[\'"]'
        content = re.sub(pattern, '', content, flags=re.IGNORECASE)
    
    return content

def validate_email(email: str) -> bool:
    """
    Проверка валидности email адреса
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Обрезка текста до заданной длины
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def normalize_whitespace(text: str) -> str:
    """
    Нормализация пробельных символов
    """
    return re.sub(r'\s+', ' ', text).strip()