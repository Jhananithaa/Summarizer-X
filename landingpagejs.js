// script.js
document.getElementById('hamburger').addEventListener('click', function() {
    const navbarLink = document.getElementById('navbar-link');
    if (navbarLink.style.display === 'flex') {
        navbarLink.style.display = 'none';
    } else {
        navbarLink.style.display = 'flex';
    }
});
function flipCard(cardWrapper) {
    const card = cardWrapper.querySelector('.card');
    card.classList.toggle('flipped'); // Toggles the flipped class on click
  }
window.onload = function() {
    // Check if the browser supports speech recognition
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      const recognition = new SpeechRecognition();
      recognition.lang = 'en-US'; // Set language
      recognition.interimResults = false; // Return only final result
      recognition.continuous = false; // Stop after user finishes speaking
  
      // Automatically prompt the blind user with text-to-speech (TTS)
      function promptForInput() {
        const speech = new SpeechSynthesisUtterance("Welcome! Please tell me what content you'd like summarized.");
        window.speechSynthesis.speak(speech);
      }
  
      // Start speech recognition once TTS has finished
      speech.onend = function() {
        recognition.start();
      };
  
      // On page load, give the welcome message and start mic access
      promptForInput();
  
      // Process the recognized voice input
      recognition.onresult = function(event) {
        const transcript = event.results[0][0].transcript;
        console.log('User said:', transcript); // Log for debugging
        // Here you would pass 'transcript' to your summarizer function
        summarizeContent(transcript);
      };
  
      // Handle errors or if no speech is detected
      recognition.onerror = function(event) {
        console.error('Error occurred during speech recognition:', event.error);
        const errorSpeech = new SpeechSynthesisUtterance("Sorry, I didn't catch that. Could you please repeat your request?");
        window.speechSynthesis.speak(errorSpeech);
      };
    } else {
      // If speech recognition is not supported
      alert('Speech recognition is not supported in this browser. Please try using a different browser.');
    }
  };
  
  // Function to process the voice command and summarize content
  function summarizeContent(command) {
    // Example: Process the command and return a summary (implement your summarizer here)
    console.log('Processing the request to summarize:', command);
    const summary = "This is a summary of the content you requested."; // Placeholder summary
    // Read the summary aloud
    const summarySpeech = new SpeechSynthesisUtterance(summary);
    window.speechSynthesis.speak(summarySpeech);
  }
  
