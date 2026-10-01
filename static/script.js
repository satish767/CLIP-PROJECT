// Wait for the HTML document to be fully loaded before running the script
document.addEventListener('DOMContentLoaded', () => {

    // Get references to our HTML elements
    const textArea = document.getElementById('clipboardText');
    const sendButton = document.getElementById('sendBtn');
    const getButton = document.getElementById('getBtn');

    // Event listener for the "Send" button
    sendButton.addEventListener('click', () => {
        fetch('/api/update', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ text: textArea.value }),
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert('Text sent!');
            }
        });
    });

    // Event listener for the "Get & Copy" button
    getButton.addEventListener('click', () => {
        fetch('/api/get')
        .then(res => res.json())
        .then(data => {
            const receivedText = data.text;
            textArea.value = receivedText;

            // Use the modern Navigator API to copy text to the clipboard
            if (navigator.clipboard) {
                navigator.clipboard.writeText(receivedText).then(() => {
                    // Give user feedback that text was copied
                    getButton.textContent = 'Copied!';
                    setTimeout(() => { getButton.textContent = 'Get & Copy'; }, 2000);
                });
            }
        });
    });
});