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
    const data = {
        key: "message",
        value: message
    };
    var chatBox = document.getElementById('chat-box');
    var messageElement = document.createElement('div');
    messageElement.classList.add('message', 'user');
    messageElement.textContent = message;
    chatBox.appendChild(messageElement);
    messageInput.value = '';
    if (message !== '') {
        try {
            const response = fetch("bot", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            });
    
            if (!response.ok) {
                throw new Error('Network response was not ok ' + response.statusText);
            }
    
            const jsonResponse =  response.json();
            var final_output = JSON.stringify(jsonResponse, null, 2);
            console.log(final_output)
        } catch (error) {
            var final_output = 'Error: ' + error.message;
        }
        var botMessage = document.createElement('div');
        botMessage.classList.add('message', 'bot');
        botMessage.textContent = final_output.response;
        chatBox.appendChild(botMessage);
        chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom

        /* Dummy response from the bot (to simulate a chat response)
        setTimeout(function() {
            var botMessage = document.createElement('div');
            botMessage.classList.add('message', 'bot');
            botMessage.textContent = final_output;
            chatBox.appendChild(botMessage);
            chatBox.scrollTop = chatBox.scrollHeight; // Scroll to bottom
        }, 500);
        */
        
    }
}

