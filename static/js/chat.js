// Chat functionality for legal document analyzer
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chat-container');
    const chatMessages = document.getElementById('chat-messages');
    const chatInput = document.getElementById('chat-input');
    const chatForm = document.getElementById('chat-form');
    
    // Get document analysis data from the page
    const documentAnalysis = {
        summary: document.querySelector('.bg-white.border.rounded-lg.shadow-sm.p-6.mb-6 p')?.textContent || '',
        clauses: Array.from(document.querySelectorAll('.border-l-4.pl-4.py-4')).map(clause => {
            return {
                title: clause.querySelector('h5')?.textContent || '',
                summary: clause.querySelector('div.mt-3:nth-child(2) p')?.textContent || '',
                risk: clause.querySelector('span')?.textContent || ''
            };
        })
    };
    
    // Add welcome message
    addMessage('assistant', 'Hello! I\'m your legal document assistant. You can ask me questions about this document, and I\'ll help you understand it better. What would you like to know?');
    
    // Handle form submission
    chatForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (message) {
            // Add user message to chat
            addMessage('user', message);
            chatInput.value = '';
            
            // Send message to server for processing
            processMessage(message, documentAnalysis);
        }
    });
    
    // Add message to chat display
    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `mb-4 ${sender === 'user' ? 'text-right' : ''}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = `inline-block p-3 rounded-lg max-w-xs md:max-w-md lg:max-w-lg ${
            sender === 'user' 
                ? 'bg-indigo-600 text-white rounded-br-none' 
                : 'bg-gray-200 text-gray-800 rounded-bl-none'
        }`;
        
        // Format the text to handle asterisks and create proper HTML
        const formattedText = formatResponse(text);
        messageContent.innerHTML = formattedText;
        
        messageDiv.appendChild(messageContent);
        chatMessages.appendChild(messageDiv);
        
        // Scroll to bottom
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Format response text to handle asterisks and create lists
    function formatResponse(text) {
        // Convert **bold** to <strong>bold</strong>
        let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Convert numbered lists (1., 2., 3., etc.)
        formatted = formatted.replace(/^(\d+\.\s.*?)(?=(\n\d+\.|$))/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)+/gs, '<ol class="list-decimal pl-5 mb-2">$&</ol>');
        formatted = formatted.replace(/<li>\d+\.\s*/g, '<li>');
        
        // Convert bullet points (* or - at the beginning of lines)
        formatted = formatted.replace(/^([\*\-]\s.*?)(?=(\n[\*\-]|$))/gm, '<li>$1</li>');
        formatted = formatted.replace(/(<li>.*<\/li>)+/gs, '<ul class="list-disc pl-5 mb-2">$&</ul>');
        formatted = formatted.replace(/<li>[\*\-]\s*/g, '<li>');
        
        // Handle line breaks
        formatted = formatted.replace(/\n/g, '<br>');
        
        return formatted;
    }
    
    // Process user message with document context
    async function processMessage(message, documentContext) {
        try {
            // Show typing indicator
            const typingIndicator = document.createElement('div');
            typingIndicator.className = 'mb-4';
            typingIndicator.id = 'typing-indicator';
            typingIndicator.innerHTML = `
                <div class="inline-block p-3 rounded-lg bg-gray-200 text-gray-800 rounded-bl-none">
                    <div class="flex space-x-1">
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.2s"></div>
                        <div class="w-2 h-2 bg-gray-500 rounded-full animate-bounce" style="animation-delay: 0.4s"></div>
                    </div>
                </div>
            `;
            chatMessages.appendChild(typingIndicator);
            chatMessages.scrollTop = chatMessages.scrollHeight;
            
            // Send request to server
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: message,
                    document_context: documentContext
                })
            });
            
            // Remove typing indicator
            typingIndicator.remove();
            
            if (response.ok) {
                const data = await response.json();
                if (data.error) {
                    addMessage('assistant', `Error: ${data.error}`);
                } else {
                    addMessage('assistant', data.response);
                }
            } else {
                addMessage('assistant', 'Sorry, I encountered an error processing your request.');
            }
        } catch (error) {
            // Remove typing indicator if present
            const typingIndicator = document.getElementById('typing-indicator');
            if (typingIndicator) typingIndicator.remove();
            
            addMessage('assistant', 'Sorry, I encountered an error processing your request.');
            console.error('Chat error:', error);
        }
    }
});