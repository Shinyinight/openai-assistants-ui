window.onload = function() {
    document.getElementById('user-input').focus();
};

let currentThreadId = null;

function showLoadingOnButton() {
    const sendButton = document.getElementById('send-btn');
    sendButton.innerHTML = '<div class="loader"></div>';
    sendButton.disabled = true;
}

function hideLoadingOnButton() {
    const sendButton = document.getElementById('send-btn');
    sendButton.innerHTML = 'Send';
    sendButton.disabled = false;
}

function sendUserInput(threadId, userInput, files=[]) {
    showLoadingOnButton();
    addToChatHistory('User', userInput);

    fetch('/ask', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ input: userInput, thread_id: threadId, file_ids: files }),
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingOnButton();
        if (data.responses && typeof data.responses === 'string') {
            addToChatHistory('Assistant', data.responses);
        } else {
            document.getElementById('logs').innerText = 'No response from assistant or error in data';
        }
    })
    .catch((error) => {
        hideLoadingOnButton();
        console.error('Error:', error);
        document.getElementById('logs').innerText = 'Error sending message.';
    });
}

function formatMessage(message) {
    return message.replace(/ /g, '&nbsp;').replace(/\n/g, '<br>');
}

function addToChatHistory(role, message) {
    const messagesContainer = document.getElementById('messages-container');
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message');

    message = formatMessage(message);
    let roleClass = role === 'User' ? 'User' : 'Assistant';
    messageDiv.innerHTML = `<strong class="${roleClass}">${role}</strong>: ${message}`;
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

document.getElementById('send-btn').addEventListener('click', function() {
    var userInputField = document.getElementById('user-input');
    var userInput = userInputField.value;
    var threadId = currentThreadId;

    if (!userInput.trim() && !document.getElementById('file-input').files.length) {
        return;
    }

    if (!threadId) {
        fetch('/create_thread')
        .then(response => response.json())
        .then(data => {
            if (data.thread_id) {
                currentThreadId = data.thread_id;
                sendUserInput(data.thread_id, userInput);
            } else {
                document.getElementById('logs').innerText = 'Error creating threads';
            }
        })
        .catch((error) => {
            console.error('Error:', error);
            document.getElementById('logs').innerText = 'Error creating threadd';
        });
    } else {
        sendUserInput(threadId, userInput);
    }

    userInputField.value = '';
});

document.getElementById('user-input').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
        event.preventDefault();
        document.getElementById('send-btn').click();
    }
});
