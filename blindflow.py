import streamlit as st
import speech_recognition as sr
import pyttsx3
import pdfkit
import docx
from bs4 import BeautifulSoup
from groq import Groq
import requests
import re
import os

# Initialize TTS engine
engine = pyttsx3.init()

def set_voice_language(language_code=None):
    """
    Set the TTS voice to match the desired language.
    """
    voices = engine.getProperty('voices')
    for voice in voices:
        if language_code and language_code in voice.languages:
            engine.setProperty('voice', voice.id)
            return
    engine.setProperty('voice', voices[0].id)

def speak(text, rate=150, chunk_size=150):
    """
    Enhanced TTS function for clear and complete output.
    """
    engine.setProperty('rate', rate)  # Adjust speaking rate
    sentences = re.split(r'(?<=[.!?]) +', text)  # Split into sentences

    for sentence in sentences:
        if len(sentence) > chunk_size:
            for i in range(0, len(sentence), chunk_size):
                engine.say(sentence[i:i + chunk_size])
                engine.runAndWait()
        else:
            engine.say(sentence)
            engine.runAndWait()

def listen(max_retries=3):
    """
    Listens for user input and converts it to text using speech recognition.
    """
    recognizer = sr.Recognizer()
    recognizer.dynamic_energy_threshold = False
    recognizer.energy_threshold = 200
    for attempt in range(max_retries):
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            print("Listening...")
            try:
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=7)
                response = recognizer.recognize_google(audio)
                print(f"User said: {response}")
                return response.lower()
            except sr.UnknownValueError:
                speak("I couldn't understand that. Please try again.")
            except sr.WaitTimeoutError:
                speak("I didn't hear anything. Please start speaking as soon as I start listening.")
            except sr.RequestError:
                speak("Sorry, there was an error with the Google service.")
                return None
    return None

def fetch_article_from_wikipedia(topic):
    """
    Fetches an article from Wikipedia based on the topic provided.
    """
    wikipedia_url = f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}"
    print(f"Searching Wikipedia for: {wikipedia_url}")

    response = requests.get(wikipedia_url)
    if response.status_code != 200:
        return "Sorry, I couldn't retrieve meaningful content from the Wikipedia article."

    soup = BeautifulSoup(response.text, 'html.parser')
    paragraphs = soup.find_all('p')
    article_text = ' '.join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])

    return article_text if article_text else "Sorry, I couldn't retrieve meaningful content from the Wikipedia article."

def truncate_content(content, max_length=2000):
    """
    Truncates content if it exceeds the maximum allowed length.
    """
    return content[:max_length] + "..." if len(content) > max_length else content

def process_with_llm(content, action):
    """
    Processes the content with the LLM for summarization, rephrasing, or translation.
    """
    client = Groq(api_key="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")
    message = f"{action}: {content}"
    truncated_message = truncate_content(message)

    chat_completion = client.chat.completions.create(
        messages=[{"role": "user", "content": truncated_message}],
        model="llama3-8b-8192",
    )

    return chat_completion.choices[0].message.content.strip()

def save_pdf(content, filename="output"):
    """
    Saves the content as a PDF.
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                font-size: 14px;
            }}
        </style>
    </head>
    <body>
        {content}
    </body>
    </html>
    """
    output_path = f"{filename}.pdf"
    options = {'quiet': '', 'encoding': 'UTF-8'}
    pdfkit.from_string(html_content, output_path, configuration=pdf_config, options=options)
    speak(f"PDF saved as {output_path}")

def save_word(content, filename="output"):
    """
    Saves the content as a Word document.
    """
    output_path = f"{filename}.docx"
    doc = docx.Document()
    doc.add_paragraph(content)
    doc.save(output_path)
    speak(f"Word document saved as {output_path}")

# Configure wkhtmltopdf path for pdfkit
pdf_config = pdfkit.configuration(wkhtmltopdf=r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe')

def main_flow():
    """
    Main application flow for the voice-controlled Summarizer X.
    """
    while True:
        speak("Welcome to Summarizer X. What do you want to explore? Summarizer, Rephraser, or Translation?")
        user_choice = listen()

        if user_choice is None:
            break

        speak(f"You chose {user_choice}. Please specify the topic.")
        data_query = listen()

        if data_query is None:
            break

        article_content = fetch_article_from_wikipedia(data_query)

        if "Sorry" not in article_content:
            if user_choice == "summarizer":
                result_text = process_with_llm(article_content, "summarize")
            elif user_choice == "rephraser":
                result_text = process_with_llm(article_content, "rephrase")
            elif user_choice == "translation":
                speak("Please specify the language to translate into.")
                language = listen()
                if language:
                    set_voice_language(language)
                    result_text = process_with_llm(article_content, f"translate to {language}")
                else:
                    speak("Translation language not specified. Exiting.")
                    break
            else:
                speak("Invalid choice. Please restart and try again.")
                break

            speak("Would you like to read it aloud, download as PDF, or save as a Word document?")
            download_option = listen()

            if download_option:
                if "pdf" in download_option:
                    save_pdf(result_text)
                if "word" in download_option:
                    save_word(result_text)
                if "read aloud" in download_option:
                    speak(result_text)
        else:
            speak("Sorry, I couldn't find meaningful content on that topic.")

        speak("Do you want to explore something else? Say yes to continue or no to exit.")
        continue_choice = listen()
        if continue_choice and "no" in continue_choice:
            break

    speak("Thank you for using Summarizer X. Redirecting you to the landing page.")
    st.experimental_rerun()  # Redirect to main.html

# Streamlit Application
def app():
    st.title("Summarizer X: Voice-Controlled Application")
    st.write("This page is fully voice-controlled. Please speak your commands.")
    main_flow()

if __name__ == "__main__":
    app()