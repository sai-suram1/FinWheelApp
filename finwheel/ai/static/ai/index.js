// Example JavaScript for sending messages (dummy implementation)
document.getElementById('send-btn').addEventListener('click', function() {
    sendMessage();
});

document.getElementById('user-message').addEventListener('keypress', function(e) {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

function sendMessage() {
    var messageInput = document.getElementById('user-message');
    var message = messageInput.value.trim();
    
    if (message !== '') {
        var chatBox = document.getElementById('chat-box');
        var messageElement = document.createElement('div');
        messageElement.classList.add('message', 'user');
        messageElement.textContent = message;
        chatBox.appendChild(messageElement);

        // Dummy response from the bot (to simulate a chat response)
        setTimeout(function() {
            var botMessage = document.createElement('div');
            botMessage.classList.add('message', 'bot');
            botMessage.textContent = 'Hello! How can I assist you today?';
            chatBox.appendChild(botMessage);
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
        }, 500);

        messageInput.value = '';
    }
}
