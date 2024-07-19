from flask import Flask, render_template, request, jsonify, session
from openai import OpenAI
import time

# Initialize Flask app
app = Flask(__name__)

# Initialize OpenAI client with the API key
#openai.api_key = "sk-proj-uCh4Cs5ftq5wOYJK8C3OT3BlbkFJjWok8Fg5obwXyUe08TZ7"

client = OpenAI(
    api_key = "sk-proj-uCh4Cs5ftq5wOYJK8C3OT3BlbkFJjWok8Fg5obwXyUe08TZ7",
)

# Specify the ID of the existing assistant
existing_assistant_id = "asst_fG1hFtScLVFdllgbb3om345k"

# Retrieve the Existing Assistant
existing_assistant = client.beta.assistants.retrieve(existing_assistant_id)
print(f"This is the existing assistant object: {existing_assistant} \n")

@app.route('/')
def index():
    session['last_message_index'] = 0  # Reset last message index when session starts
    return render_template('index.html')

@app.route('/create_thread', methods=['GET'])
def create_thread():
    try:
        thread = client.beta.threads.create()
        session['last_message_index'] = 0  # Reset index whenever a new thread is created
        return jsonify({"thread_id": thread.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/ask', methods=['POST'])
def ask_openai():
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('input')
    if not user_input:
        return jsonify("No input provided"), 400

    try:
        thread_message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
        my_run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=existing_assistant_id
        )
        while my_run.status in ["queued", "in_progress"]:
            my_run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=my_run.id)
            time.sleep(0.5)

        if my_run.status == "completed":
            all_messages = client.beta.threads.messages.list(thread_id=thread_id)
            last_index = session.get('last_message_index', 0)
            responses = [message.content[0].text.value for message in all_messages.data[last_index:] if message.role == 'assistant']
            session['last_message_index'] = len(all_messages.data)  # Update the index to the current length of messages
            return jsonify({"responses": responses})
        else:
            return jsonify({"error": f"Run status: {my_run.status}"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
