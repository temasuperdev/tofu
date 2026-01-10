from marshmallow import Schema, fields, validate, ValidationError
import validators  # pip install validators


class MessageSchema(Schema):
    message = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=1000),
        error_messages={
            "required": "Поле message обязательно",
            "validator_failed": "Сообщение должно быть строкой длиной от 1 до 1000 символов"
        }
    )


def validate_url(url):
    return validators.url(url)


def validate_email(email):
    return validators.email(email)