from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import time
import os

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

existing_assistant = client.beta.assistants.update(
  assistant_id=existing_assistant_id,
  tool_resources={"file_search": {"vector_store_ids": ["vs_hXflqWbBvHyeug5LJTp798vD"]}},
)

# Route to serve the index page
@app.route('/')
def index():
    return render_template('index.html')

# New Route to create a new thread and retrieve assistant details
@app.route('/create_thread', methods=['GET'])
def create_thread():
    try:
        # Create a new chat thread
        thread = client.beta.threads.create(
        messages=[ { "role": "user", "content": "Hi, what can you do??"} ],
        tool_resources={
            "file_search": {
            "vector_store_ids": ["vs_hXflqWbBvHyeug5LJTp798vD"]
            }
        }
        )
        return jsonify({"thread_id": thread.id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Route to handle POST requests to communicate with the assistant
@app.route('/ask', methods=['POST'])
def ask_openai():
    data = request.json
    thread_id = data.get('thread_id')
    user_input = data.get('input')

    print(f"This is the thread_id: {thread_id} \n")
    print(f"This is the user_input: {user_input} \n")

    if not user_input:
        return jsonify("No input provided"), 400

    try:
        # Create message on thread
        thread_message = client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=user_input
        )
        print(f"This is the thread_message: {thread_message} \n")
        # Run assistant on thread
        my_run = client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=existing_assistant_id,
            instructions=existing_assistant.instructions
        )
        print(f"This is the my_run: {my_run} \n")
        # Periodically retrieve the Run to check on its status
        while my_run.status in ["queued", "in_progress"]:
            my_run = client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=my_run.id
            )
            time.sleep(0.5)  # Sleep briefly before checking again

        if my_run.status == "completed":
            # Retrieve the Messages added by the Assistant to the Thread
            all_messages = client.beta.threads.messages.list(thread_id=thread_id)
            # Extracting text from the response
            responses = [message.content[0].text.value for message in all_messages.data if message.role == 'assistant']
            print("Assistant Responses:", responses[0])  # Print the responses in the console
            return jsonify({"responses": responses[0]})
        else:
            return jsonify({"error": "Run status: {my_run.status}"})
    except Exception as e:
        print(str(e))
        return jsonify({"error": str(e)}), 500


# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)
