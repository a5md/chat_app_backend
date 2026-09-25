from .services import (
    registration_service,
    auth_service,
    oauth2_service,
    user_service,
    conversation_service,
    message_service,
    ws_service
)

def get_registration_service():
    return registration_service

def get_auth_service():
    return auth_service

def get_user_service():
    return user_service

def get_conversation_service():
    return conversation_service

def get_oauth2_service():
    return oauth2_service

def get_message_service():
    return message_service

def get_ws_service():
    return ws_service