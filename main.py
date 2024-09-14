from flask import Flask, request, jsonify
import google.generativeai as genai
from flask_cors import CORS
import os


app = Flask(__name__)
CORS(app)  # Habilitar CORS

# Configure the API key
# genai.configure(api_key="AIzaSyCpJjl21-CwSjFlXZ7U0MDq99l3HTkM1LA")
genai.configure(api_key=os.getenv("API_KEY"))

# Set up the model
model = genai.GenerativeModel('gemini-1.5-pro-exp-0827')

def set_context(chat):
    context = """
    You are a multi language support bot for a company. Your primary goal is to help clients 
    with their inquiries and issues while maintaining a positive image of the company. 
    Always assist the client without negatively affecting the company's interests. 
    Be polite, professional, and solution-oriented in your responses.
    Keep your responses concise and direct, ideally under 70 words.
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

# Initialize chat history
chat = model.start_chat(history=[])
set_context(chat)

@app.route('/chat', methods=['POST'])
def chat_endpoint():
    user_input = request.json.get('message')
    
    if not user_input:
        return jsonify({'error': 'No message provided'}), 400
    
    try:
        # Generate a response
        response = chat.send_message(user_input)
        truncated_response = truncate_response(response.text)
        return jsonify({'response': truncated_response})
    except Exception as e:
        # Print error details to the console
        print(f"An error occurred: {e}")
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

if __name__ == "__main__":
    app.run()
