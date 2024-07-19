from flask import Flask, render_template, request, jsonify
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key here (ideally from environment variables)
openai.api_key = "sk-proj-uCh4Cs5ftq5wOYJK8C3OT3BlbkFJjWok8Fg5obwXyUe08TZ7"

# Index route to serve the UI
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle the assistant interactions
@app.route('/ask', methods=['POST'])
def ask_openai():
    user_input = request.form['input']  # Assuming input name is 'input' in your HTML form

    # Create a thread
    thread = openai.beta.threads.create()
    thread_id = thread.id

    # Send a message to the thread
    thread_message = openai.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )

    # Run the assistant on the thread
    assistant_id = "asst_fG1hFtScLVFdllgbb3om345k"  # Replace with your actual assistant ID
    run = openai.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id
    )

    # Check for the run completion and retrieve the response
    while run.status not in ['completed', 'failed', 'cancelled']:
        run = openai.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
    if run.status == 'completed':
        # Retrieve the latest message from the thread
        response = openai.beta.threads.messages.list(thread_id=thread_id)
        latest_message = response.data[-1].content  # Assuming the last message is from the assistant
        return jsonify(latest_message)

    return jsonify("An error occurred"), 500

if __name__ == '__main__':
    app.run(debug=True)
