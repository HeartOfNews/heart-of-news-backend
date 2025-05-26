"""
Telegram channel management API endpoints
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api import deps
from app.core.config import settings
from app.services.telegram_service import telegram_service
from app.crud import article as article_crud
from app.models.user import User

router = APIRouter()


@router.get("/status", response_model=Dict[str, Any])
async def get_telegram_status(
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Get Telegram service status and configuration"""
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can access Telegram status"
        )
    
    return {
        "enabled": telegram_service.enabled,
        "configured": telegram_service.bot_token is not None and telegram_service.channel_id is not None,
        "bot_token_set": telegram_service.bot_token is not None,
        "channel_id_set": telegram_service.channel_id is not None,
        "channel_id": telegram_service.channel_id if telegram_service.channel_id else None
    }


@router.post("/test", response_model=Dict[str, Any])
async def test_telegram_connection(
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Test the Telegram bot connection"""
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can test Telegram connection"
        )
    
    if not telegram_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram service is not enabled or configured"
        )
    
    result = await telegram_service.test_connection()
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Telegram connection failed: {result.get('error')}"
        )
    
    return result


@router.post("/send-test-message", response_model=Dict[str, Any])
async def send_test_message(
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Send a test message to the Telegram channel"""
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can send test messages"
        )
    
    if not telegram_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram service is not enabled or configured"
        )
    
    test_message = """
🧪 **Test Message from Heart of News**

This is a test message to verify that your Telegram channel integration is working correctly.

✅ If you can see this message, your setup is working!

🤖 Sent by Heart of News Bot
    """.strip()
    
    result = await telegram_service.send_message(test_message)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to send test message: {result.get('error')}"
        )
    
    return result


@router.post("/publish-article/{article_id}", response_model=Dict[str, Any])
async def publish_article_to_telegram(
    article_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Manually publish a specific article to Telegram"""
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can manually publish articles"
        )
    
    if not telegram_service.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Telegram service is not enabled or configured"
        )
    
    # Get the article
    db_article = article_crud.get(db, id=article_id)
    if not db_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Publish to Telegram
    result = await telegram_service.publish_article(db_article)
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to publish article to Telegram: {result.get('error')}"
        )
    
    return {
        "success": True,
        "article_id": article_id,
        "article_title": db_article.title,
        "telegram_result": result
    }


@router.get("/preview/{article_id}", response_model=Dict[str, Any])
async def preview_telegram_message(
    article_id: str,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user)
) -> Dict[str, Any]:
    """Preview how an article would look when posted to Telegram"""
    if not current_user.role == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin users can preview Telegram messages"
        )
    
    # Get the article
    db_article = article_crud.get(db, id=article_id)
    if not db_article:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Article not found"
        )
    
    # Format the message
    formatted_message = telegram_service.format_article_message(db_article)
    
    return {
        "article_id": article_id,
        "article_title": db_article.title,
        "telegram_message": formatted_message,
        "message_length": len(formatted_message)
    }