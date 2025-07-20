import speech_recognition as spr
from googletrans import Translator
rec = spr.Recognizer()
mc = spr.Microphone()


# Function to capture voice and recognize text
def recognize_speech(recog, source):
    try:
        recog.adjust_for_ambient_noise(source, duration=0.2)  # Adjust for background noise
        audio = recog.listen(source)  # Capture audio input
        recognized_text = recog.recognize_google(audio)  # Recognize using Google's recognizer
        return recognized_text.lower()
    except spr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio.")
        return None
    except spr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None


# Capture initial voice
with mc as source:
    print("Speak 'hello' to initiate the Translation!")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    MyText = recognize_speech(rec, source)

# Check if the input contains 'hello'
if MyText and 'hello' in MyText:
    # Translator method for translation
    translator = Translator()

    # Source and target languages
    from_lang = 'en'
    to_lang = 'hi'

    with mc as source:
        print("Speak a sentence to translate...")
        get_sentence = recognize_speech(rec, source)

        # If sentence recognized properly
        if get_sentence:
            try:
                # Print sentence to be translated
                print(f"Phrase to be Translated: {get_sentence}")

                # Translate the text
                text_to_translate = translator.translate(get_sentence, src=from_lang, dest=to_lang)
                if text_to_translate and text_to_translate.text:
                    translated_text = text_to_translate.text
                    print(f"Translated Text (to Hindi): {translated_text}")
                else:
                    print("Translation failed or returned None.")
            except Exception as e:
                print(f"An error occurred during translation: {e}")
