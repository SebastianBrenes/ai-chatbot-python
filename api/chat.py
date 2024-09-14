from http.server import BaseHTTPRequestHandler
import json
import google.generativeai as genai
import os
import traceback

# Configure the API key
genai.configure(api_key=os.getenv("API_KEY"))

# Set up the model
model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')

# Initialize chat history
chat = model.start_chat(history=[])

def set_context(chat):
    context = """
    You are a multi language support bot for a company, you will always answer in the last language the user talked.
    Your primary goal is to help clients with their inquiries and issues while maintaining a positive image of the company.
    Always assist the client without negatively affecting the company's interests.
    Be polite, professional, and solution-oriented in your responses.
    Keep your responses concise and direct, ideally 50 words, at most 70 words.
    Only ask to connect with a real human if it is completely necessary.
    """
    chat.send_message(context)

def truncate_response(response, max_words=70):
    words = response.split()
    if len(words) <= max_words:
        formatted_response = response.replace(". ", ".<br><br>")
        return formatted_response
    truncated_text = ' '.join(words[:max_words])
    return truncated_text.replace(". ", ".<br><br>") + '...'

# Set the context for the chat
set_context(chat)

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        # Set CORS headers for the preflight request
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

        try:
            user_input = json.loads(post_data)['message']
            
            # Generate a response
            response = chat.send_message(user_input)
            truncated_response = truncate_response(response.text)

            # Send the response
            self.wfile.write(json.dumps({'response': truncated_response}).encode('utf-8'))
        except Exception as e:
            # Handle errors
            error_details = traceback.format_exc()
            print(f"An error occurred: {error_details}")
            self.wfile.write(json.dumps({'error': f"An error occurred: {str(e)}", 'details': error_details}).encode('utf-8'))

    def do_OPTIONS(self):
        # Handle preflight requests
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()