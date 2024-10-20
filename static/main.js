document.getElementById('chatForm').addEventListener('submit', function (e) {
    e.preventDefault();

    // Get user input
    const userInput = document.getElementById('user_input').value;

    // Append the user's message to the chatbox
    const messages = document.getElementById('messages');
    const userMessage = document.createElement('div');
    userMessage.classList.add('message', 'user');
    userMessage.textContent = userInput;
    messages.appendChild(userMessage);

    // Clear input field
    document.getElementById('user_input').value = '';

    // Send user input to the Flask backend
    fetch('/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: userInput }),
    })
    .then(response => response.json())
    .then(data => {
        // Append chatbot's response to the chatbox
        const botMessage = document.createElement('div');
        botMessage.classList.add('message', 'bot');
        botMessage.textContent = data.response;
        messages.appendChild(botMessage);
        
        // Scroll chatbox to the bottom
        messages.scrollTop = messages.scrollHeight;
    });
});
