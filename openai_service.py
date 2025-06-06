import os
import logging
import json
import requests
from openai import OpenAI
import google.generativeai as genai

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        """Initialize AI service with multiple model options"""
        # OpenAI
        self.openai_key = os.getenv('OPENAI_API_KEY', '')
        self.openai_client = None
        if self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)
            logger.info("OpenAI service initialized successfully")
        
        # Ollama (local/free)
        self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
        
        # Hugging Face (free tier)
        self.hf_token = os.getenv('HUGGINGFACE_TOKEN', '')
        
        # Google Gemini (free tier)
        self.gemini_key = os.getenv('GEMINI_API_KEY', '')
        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            logger.info("Google Gemini initialized successfully")
        
        # Anthropic Claude (if available)
        self.anthropic_key = os.getenv('ANTHROPIC_API_KEY', '')
        
        logger.info("AI service initialized with multiple model options")
    
    def is_configured(self):
        """Check if any AI service is properly configured"""
        return (self.openai_client is not None or 
                self.hf_token or 
                self.gemini_key or 
                self.anthropic_key or 
                self._check_ollama())
    
    def _check_ollama(self):
        """Check if Ollama is available"""
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False
    
    def _generate_with_huggingface(self, user_message, system_prompt):
        """Generate response using Hugging Face API"""
        if not self.hf_token:
            return None
        
        try:
            # Test token first with a simple request
            test_url = "https://huggingface.co/api/whoami"
            headers = {"Authorization": f"Bearer {self.hf_token}"}
            
            test_response = requests.get(test_url, headers=headers, timeout=10)
            if test_response.status_code != 200:
                logger.error(f"HF Token validation failed: {test_response.status_code}")
                return None
            
            # Try different available models
            models = [
                "bigscience/bloom-560m",
                "distilgpt2", 
                "gpt2"
            ]
            
            for model in models:
                try:
                    api_url = f"https://api-inference.huggingface.co/models/{model}"
                    
                    # Simple text generation
                    payload = {
                        "inputs": f"問題：{user_message}\n回答：",
                        "parameters": {
                            "max_new_tokens": 80,
                            "temperature": 0.8,
                            "return_full_text": False
                        }
                    }
                    
                    response = requests.post(api_url, headers=headers, json=payload, timeout=25)
                    logger.info(f"HF {model} response: {response.status_code}")
                    
                    if response.status_code == 200:
                        result = response.json()
                        logger.info(f"HF result for {model}: {result}")
                        
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get("generated_text", "")
                            if generated_text and len(generated_text.strip()) > 5:
                                clean_response = generated_text.strip()
                                clean_response = clean_response.replace("<|endoftext|>", "")
                                return f"AI 回應：{clean_response}"
                    
                    elif response.status_code == 503:
                        logger.info(f"Model {model} is loading, trying next...")
                        continue
                    elif response.status_code == 401:
                        logger.error("HF Token unauthorized")
                        return None
                    else:
                        logger.warning(f"HF {model} failed with status {response.status_code}")
                        
                except Exception as model_error:
                    logger.warning(f"Model {model} error: {str(model_error)}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Hugging Face API error: {str(e)}")
            return None
    
    def _generate_with_gemini(self, user_message, system_prompt):
        """Generate response using Google Gemini API"""
        if not self.gemini_key:
            return None
        
        try:
            # Try different available Gemini models
            models = ['gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            
            for model_name in models:
                try:
                    model = genai.GenerativeModel(model_name)
                    
                    # Combine system prompt with user message
                    full_prompt = f"{system_prompt}\n\n用戶問題：{user_message}\n\n請用繁體中文回答："
                    
                    response = model.generate_content(full_prompt)
                    
                    if response.text:
                        logger.info(f"Generated response using Gemini {model_name} for: {user_message}")
                        return response.text.strip()
                        
                except Exception as model_error:
                    logger.warning(f"Gemini model {model_name} failed: {str(model_error)}")
                    continue
            
            return None
            
        except Exception as e:
            logger.error(f"Google Gemini API error: {str(e)}")
            return None
    
    def _generate_with_ollama(self, user_message, system_prompt):
        """Generate response using Ollama"""
        if not self._check_ollama():
            return None
        
        try:
            payload = {
                "model": "llama2",  # Default model, can be changed
                "prompt": f"{system_prompt}\n\nUser: {user_message}\nAssistant:",
                "stream": False
            }
            
            response = requests.post(f"{self.ollama_url}/api/generate", json=payload, timeout=30)
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "").strip()
            return None
        except Exception as e:
            logger.error(f"Ollama API error: {str(e)}")
            return None
    
    def generate_response(self, user_message):
        """Generate AI response for user message using available models"""
        if not self.is_configured():
            return "抱歉，AI 服務目前無法使用。請稍後再試。"
        
        # System prompt for the chatbot personality
        system_prompt = """你是一個友善且樂於助人的聊天機器人。請用繁體中文回應用戶。
特點：
- 友善、有禮貌
- 提供有用的資訊和建議
- 保持對話自然流暢
- 如果不確定答案，會誠實告知
- 避免提供有害或不當的內容"""
        
        # Handle common commands
        if user_message.lower() in ['hi', 'hello', '你好', '嗨']:
            return "你好！我是你的智能助手，有什麼可以幫助你的嗎？"
        
        if user_message.lower() in ['help', '幫助', '說明']:
            return """我可以幫助你：
• 回答各種問題
• 進行日常對話
• 提供資訊和建議
• 解釋概念和知識

直接輸入你的問題或想聊的話題就可以了！"""
        
        # Try different AI services in order of preference
        
        # 1. Try OpenAI first (if available and has quota)
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    max_tokens=500,
                    temperature=0.7
                )
                ai_response = response.choices[0].message.content
                if ai_response:
                    ai_response = ai_response.strip()
                logger.info(f"Generated response using OpenAI for: {user_message}")
                return ai_response
            except Exception as e:
                logger.warning(f"OpenAI failed, trying alternatives: {str(e)}")
        
        # 2. Try Google Gemini (free tier)
        gemini_response = self._generate_with_gemini(user_message, system_prompt)
        if gemini_response:
            logger.info(f"Generated response using Gemini for: {user_message}")
            return gemini_response
        
        # 3. Try Hugging Face (free tier)
        hf_response = self._generate_with_huggingface(user_message, system_prompt)
        if hf_response:
            logger.info(f"Generated response using Hugging Face for: {user_message}")
            return hf_response
        
        # 4. Try Ollama (local/free)
        ollama_response = self._generate_with_ollama(user_message, system_prompt)
        if ollama_response:
            logger.info(f"Generated response using Ollama for: {user_message}")
            return ollama_response
        
        # 4. Fallback to simple rule-based responses
        fallback_response = self._generate_fallback_response(user_message)
        if fallback_response:
            logger.info(f"Generated fallback response for: {user_message}")
            return fallback_response
        
        # Final fallback message
        return "抱歉，AI 服務目前無法使用。請稍後再試或聯絡管理員。"
    
    def _generate_fallback_response(self, user_message):
        """Generate simple rule-based responses when AI services are unavailable"""
        message_lower = user_message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['你好', '嗨', 'hi', 'hello', '哈囉']):
            return "你好！我是你的智能助手。雖然高級 AI 功能暫時無法使用，但我仍然可以協助你處理一些基本問題。"
        
        # Help requests
        if any(word in message_lower for word in ['幫助', '幫忙', 'help', '說明', '功能']):
            return """我可以提供以下協助：
• 回答常見問題
• 提供基本資訊
• 進行簡單對話
• 協助使用說明

目前 AI 服務正在維護中，完整功能將稍後恢復。"""
        
        # Time/date questions
        if any(word in message_lower for word in ['時間', '日期', '現在', 'time', 'date']):
            return "抱歉，我目前無法取得即時時間資訊。請檢查你的裝置時間或稍後再試。"
        
        # Weather questions
        if any(word in message_lower for word in ['天氣', '氣溫', 'weather', '下雨']):
            return "抱歉，我目前無法提供天氣資訊。建議你查看天氣應用程式或氣象網站。"
        
        # Thanks
        if any(word in message_lower for word in ['謝謝', '感謝', 'thank', '謝']):
            return "不客氣！很高興能為你服務。如有其他問題，隨時可以詢問我。"
        
        # Goodbye
        if any(word in message_lower for word in ['再見', '掰掰', 'bye', 'goodbye', '拜拜']):
            return "再見！期待下次為你服務。祝你有美好的一天！"
        
        # Default response for other questions
        return "我收到了你的訊息，但目前高級 AI 功能暫時無法使用。請稍後再試，或者詢問一些基本問題，我會盡力協助你。"
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text (optional feature)"""
        if not self.is_configured():
            return None
        
        try:
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-4o",
                    messages=[
                        {
                            "role": "system",
                            "content": "Analyze the sentiment of the following text. Respond with JSON format: {'sentiment': 'positive/negative/neutral', 'confidence': 0.0-1.0}"
                        },
                        {"role": "user", "content": text}
                    ],
                    response_format={"type": "json_object"}
                )
                
                result = response.choices[0].message.content
                return result
            
            return None
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return None
