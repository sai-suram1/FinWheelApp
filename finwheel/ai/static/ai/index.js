document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userMessageInput = document.getElementById('user-message');
    const sendBtn = document.getElementById('send-btn');

    // Function to append message to chat box
    function appendMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        console.log(message)
        messageDiv.innerText = message;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Function to handle user message
    function handleUserMessage() {
        const userMessage = userMessageInput.value.trim();
        if (userMessage === '') return;

        // Append user's message to the chat box
        appendMessage('user', userMessage);

        // Clear the input field
        userMessageInput.value = '';
        const botMessage = fetchBotResponse(userMessage);
        appendMessage('bot', botMessage);
        /* Simulate a response from the chatbot
        setTimeout(() => {
            const botMessage = 'Hello!';
            appendMessage('bot', botMessage);
        }, 500); */ //Simulate a 1-second delay for the bot response
    }

    function fetchBotResponse(userMessage) {
        try {
            /*
            const response = fetch("bot", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ message: userMessage })
            });
            /*
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            
            console.log(response.body)
            var data = response.body;
            return data;
            */
            fetch("bot", {method: 'POST', body: JSON.stringify({ message: userMessage })})
            .then(response => {
                var x = response.json();
                console.log(JSON.parse(JSON.stringify(x)));
                return JSON.stringify(x);
            })
            .catch(err => console.log(err))
        } catch (error) {
            console.error('There was a problem with the fetch operation:', error);
            return `Bot: Sorry, there was an error processing your request.`;
        }
    }
    // Event listener for the send button
    sendBtn.addEventListener('click', handleUserMessage);

    // Event listener for the Enter key
    userMessageInput.addEventListener('keydown', (event) => {
        if (event.key === 'Enter') {
            handleUserMessage();
        }
    });
});

