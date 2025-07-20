from deep_translator import GoogleTranslator
import speech_recognition as spr

# Creating Recogniser() class object
rec = spr.Recognizer()
# Creating Microphone() instance
mc = spr.Microphone()


# Function to capture voice and recognize text
def recognize_speech(recog, source):
    try:
        recog.adjust_for_ambient_noise(source, duration=1)  # Adjust for background noise
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
    with mc as source:
        print("Speak a sentence to translate...")
        get_sentence = recognize_speech(rec, source)

        # If sentence recognized properly
        if get_sentence:
            try:
                # Print sentence to be translated
                print(f"Phrase to be Translated: {get_sentence}")

                # Translate the text using deep-translator
                translated_text = GoogleTranslator(source='auto', target='en').translate(get_sentence)
                print(f"Translated Text (to English): {translated_text}")
            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("Unable to capture the sentence for translation.")
