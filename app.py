import os
import logging
from flask import Flask, request, render_template, jsonify
from werkzeug.middleware.proxy_fix import ProxyFix
from line_bot import LineBot
from openai_service import OpenAIService

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "fallback-secret-key")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Initialize services
line_bot = LineBot()
openai_service = OpenAIService()

@app.route('/')
def index():
    """Main page showing bot status and information"""
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    """Dashboard for monitoring bot activity"""
    return render_template('dashboard.html')

@app.route('/webhook', methods=['POST'])
def webhook():
    """LINE webhook endpoint for receiving messages"""
    try:
        # Get X-Line-Signature header value
        signature = request.headers.get('X-Line-Signature', '')
        
        # Get request body as text
        body = request.get_data(as_text=True)
        logger.info(f"Request body: {body}")

        # Verify webhook signature and parse events
        events = line_bot.parse_webhook(body, signature)
        
        # Process each event
        for event in events:
            if event.type == 'message' and event.message.type == 'text':
                # Get user message
                user_message = event.message.text
                user_id = event.source.user_id
                
                logger.info(f"Received message from {user_id}: {user_message}")
                
                # Generate AI response
                ai_response = openai_service.generate_response(user_message)
                
                # Send reply back to user
                line_bot.reply_message(event.reply_token, ai_response)
                
                logger.info(f"Sent reply: {ai_response}")

        return 'OK', 200
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return 'Error', 500

@app.route('/api/test-message', methods=['POST'])
def test_message():
    """Test endpoint for generating AI responses"""
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({'error': 'Message is required'}), 400
            
        response = openai_service.generate_response(message)
        return jsonify({'response': response})
        
    except Exception as e:
        logger.error(f"Error in test message: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'line_bot_configured': line_bot.is_configured(),
        'openai_configured': openai_service.is_configured()
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
