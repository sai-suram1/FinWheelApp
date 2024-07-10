document.addEventListener('DOMContentLoaded', () => {
    const chatBox = document.getElementById('chat-box');
    const userMessageInput = document.getElementById('user-message');
    const sendBtn = document.getElementById('send-btn');

    // Function to append message to chat box
    function appendMessage(sender, message) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message', sender);
        //console.log(message)
        messageDiv.innerHTML = `<hr><h4>${sender}:</h4> ${message}<hr>`;
        chatBox.appendChild(messageDiv);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Function to handle user message
    async function handleUserMessage() {
        var userMessage = userMessageInput.value.trim();
        if (userMessage === '') return;

        // Append user's message to the chat box
        appendMessage('user', userMessage);

        // Clear the input field
        userMessageInput.value = '';
        
        //Simulate a response from the chatbot
        setTimeout(() => {
            fetch("bot", {
                method: 'POST', 
                body: JSON.stringify({ message: userMessage , chat: sendBtn.className}), 
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{csrf_token}}' 
            }})
            .then(response => response.text())
            .then(data => {
                console.log(data);
                appendMessage('bot', data);
            })
            .catch(err => console.log(err))
            
        }, 2000);
    }


    // NOT USED
    async function fetchBotResponse(userMessage, chatID) {
        try {
            await fetch("bot", {
                method: 'POST', 
                body: JSON.stringify({ message: userMessage, chat: chatID}), 
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{csrf_token}}' 
            }})
            .then(response => response.text())
            .then(data => {
                console.log(data);
                return data;
            })
            .catch(err => console.log(err))
        } catch (err) {
            console.error('There was a problem with the fetch operation:', err);
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

    async function handleChatChange(chatID){
        try {
            document.getElementById('chat-box').innerHTML = ""; // clear the box
            await fetch("chatpull", {
                method: 'POST', 
                body: JSON.stringify({ pullID: chatID }), 
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{csrf_token}}' 
            }})
            .then(response => response.text())
            .then(data => {
                console.log(data);
                document.getElementById('chat-box').innerHTML = data;
                sendBtn.setAttribute("class", chatID);
            })
            .catch(err => console.log(err))
        } catch (err) {
            console.error('There was a problem with the fetch operation:', err);
            return `Bot: Sorry, there was an error processing your request.`;
        }
        
    }


   
    //const chatBtn = document.getElementByClass('chatButton');
    //chatBtn.addEventListener('click', handleChatChange(chatBtn.id));
    

});

