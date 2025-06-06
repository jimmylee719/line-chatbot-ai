import os
import logging
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

logger = logging.getLogger(__name__)

class LineBot:
    def __init__(self):
        """Initialize LINE Bot with credentials from environment variables"""
        self.channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', '')
        self.channel_secret = os.getenv('LINE_CHANNEL_SECRET', '')
        
        if self.channel_access_token and self.channel_secret:
            self.line_bot_api = LineBotApi(self.channel_access_token)
            self.handler = WebhookHandler(self.channel_secret)
            logger.info("LINE Bot initialized successfully")
        else:
            self.line_bot_api = None
            self.handler = None
            logger.warning("LINE Bot credentials not found in environment variables")
    
    def is_configured(self):
        """Check if LINE Bot is properly configured"""
        return self.line_bot_api is not None and self.handler is not None
    
    def parse_webhook(self, body, signature):
        """Parse webhook request and return events"""
        if not self.is_configured():
            raise Exception("LINE Bot is not configured")
        
        try:
            events = self.handler.parse(body, signature)
            return events
        except InvalidSignatureError:
            logger.error("Invalid signature error")
            raise Exception("Invalid signature")
        except Exception as e:
            logger.error(f"Error parsing webhook: {str(e)}")
            raise
    
    def reply_message(self, reply_token, message_text):
        """Send reply message to user"""
        if not self.is_configured():
            raise Exception("LINE Bot is not configured")
        
        try:
            # Create text message
            message = TextSendMessage(text=message_text)
            
            # Send reply
            self.line_bot_api.reply_message(reply_token, message)
            logger.info(f"Reply sent successfully: {message_text}")
            
        except LineBotApiError as e:
            logger.error(f"LINE Bot API error: {e.message}")
            raise Exception(f"Failed to send message: {e.message}")
        except Exception as e:
            logger.error(f"Error sending reply: {str(e)}")
            raise
    
    def push_message(self, user_id, message_text):
        """Send push message to specific user"""
        if not self.is_configured():
            raise Exception("LINE Bot is not configured")
        
        try:
            message = TextSendMessage(text=message_text)
            self.line_bot_api.push_message(user_id, message)
            logger.info(f"Push message sent to {user_id}: {message_text}")
            
        except LineBotApiError as e:
            logger.error(f"LINE Bot API error: {e.message}")
            raise Exception(f"Failed to send push message: {e.message}")
        except Exception as e:
            logger.error(f"Error sending push message: {str(e)}")
            raise
    
    def get_profile(self, user_id):
        """Get user profile information"""
        if not self.is_configured():
            raise Exception("LINE Bot is not configured")
        
        try:
            profile = self.line_bot_api.get_profile(user_id)
            return {
                'user_id': profile.user_id,
                'display_name': profile.display_name,
                'picture_url': profile.picture_url,
                'status_message': profile.status_message
            }
        except LineBotApiError as e:
            logger.error(f"Error getting profile: {e.message}")
            return None
        except Exception as e:
            logger.error(f"Error getting profile: {str(e)}")
            return None
