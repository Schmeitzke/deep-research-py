# chat/api_views.py
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
import json
from django.db import transaction
from django.contrib.auth import get_user_model
from .models import ChatSession, ChatMessage
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@csrf_exempt
def save_chat(request):
    logger.info("Received request to save chat.")
    
    if request.method == "OPTIONS":
        response = JsonResponse({"detail": "ok"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    if request.method != "POST":
        logger.warning(f"Incorrect method: {request.method}")
        return HttpResponseBadRequest("Only POST requests are allowed.")
    
    try:
        data = json.loads(request.body.decode("utf-8"))
        logger.info(f"Request payload: {data}")
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {e}")
        return HttpResponseBadRequest("Invalid JSON payload.")
    
    session_data = data.get("session")
    if not session_data:
        logger.error("Missing 'session' data in the request.")
        return HttpResponseBadRequest("Missing 'session' data in the request.")
    
    title = session_data.get("title", "")
    messages_data = session_data.get("messages")
    if not messages_data or not isinstance(messages_data, list):
        logger.error("Invalid or missing 'messages' field.")
        return HttpResponseBadRequest("Invalid or missing 'messages' field.")

    if request.user.is_authenticated:
        user = request.user
    else:
        try:
            user = User.objects.get(username="anonymous")
        except User.DoesNotExist:
            user = User.objects.create_user(username="anonymous", password="unused")
    
    try:
        with transaction.atomic():
            chat_session = ChatSession.objects.create(user=user, title=title)
            messages_to_create = [
                ChatMessage(session=chat_session, role=msg.get("role"), content=msg.get("content"))
                for msg in messages_data if msg.get("role") and msg.get("content")
            ]
            ChatMessage.objects.bulk_create(messages_to_create)
        logger.info(f"Chat session saved successfully: {chat_session.id}")
    except Exception as e:
        logger.error(f"Error saving chat session: {e}")
        return JsonResponse({"error": str(e)}, status=500)
    
    return JsonResponse({
        "message": "Chat session saved successfully.",
        "session_id": chat_session.id
    })
