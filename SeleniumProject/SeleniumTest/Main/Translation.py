from deep_translator import GoogleTranslator
stringLang = input("Enter the OPCO string: ")
translator = GoogleTranslator(source='auto', target='en')
translation = translator.translate(stringLang)
print(f"Translation is: {translation}")
