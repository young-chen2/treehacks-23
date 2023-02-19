import whisper
from pvrecorder import PvRecorder
import wave
import struct
import os
import sys
import time
from gtts import gTTS
from googletrans import Translator
import openai

# TO USE GTP, USE:
# export api_key=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
class AudioProcess():
    def __init__(self):
        self.conversation_context = None
        self.recorder = None
        self.model = None
        

    # MAKE CHAT GTP PERSISTENT!
    def imports(self):
        os.environ['api_key'] = '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' # Boxin's key
        openai.api_key = os.environ['api_key']

        self.model = whisper.load_model("base")
        self.recorder = PvRecorder(device_index=-1, frame_length=512)
        
        self.conversation_context = 'Given this context, generate the next response in the conversation. Do so one response at a time and let me speak. Only generate one response Allin for now. If the user input does not make grammatical sense, say "Sorry, I don\'t understand that. It may be your pronounciation or your grammar. Then tell the user what you think he or she is saying and how to to pronounce that. Pretend you are a cashier named Allin working at a cafe. On the menu is sandwiches for $15, salad for $10, soup for $10, water for $1, coffee for $4, orange and apple juice for $3 each, cake for $5, ice cream for $2, and cookies for $2. I will act as a customer. Wait for me to speak before you respond. Do not serve me anything not on the menu. Do not say customer lines. Have a conversation with me where you say your name and ask me what I would like to order. When I say my order, tell me what my total price is and ask if I would like to pay in cash or credit. After I answer, ask if you can get a name for my order, and after I say my name, address me and say "Thank you. Your food will be ready shortly.'
        
        initial_convo = openai.Completion.create(
            engine="text-davinci-003",
            prompt=self.conversation_context,
            max_tokens=30,
            n=1,
            stop=None,
            temperature=0.5,
        )

        print(initial_convo.choices[0].text)
        self.conversation_context += " \n Allin: " + initial_convo.choices[0].text

    def recordAudio(self):
        # RECORDING AUDIO!!!
        print("Recording audio...")
            
        audio = []
        start_time = time.time()
        self.recorder.start()
        while (time.time() - start_time) < 5:
            frame = self.recorder.read()
            audio.extend(frame)
        
        self.recorder.stop()
        with wave.open('current_speech.mp3', 'w') as f:
            f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            f.writeframes(struct.pack("h" * len(audio), *audio))
        
        # self.recorder.delete()
        print("Audio recorded! (current_speech.mp3)")
        
    def processAudio(self):
        # PARSING AUDIO Tos AND SoT!    
        print("Parsing audio...")
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio("current_speech.mp3")
        audio = whisper.pad_or_trim(audio)
        # make log-Mel spectrogram and move to the same device as the model
        mel = whisper.log_mel_spectrogram(audio).to(self.model.device)
        # detect the spoken language
        _, probs = self.model.detect_language(mel)
        print(f"Detected language: {max(probs, key=probs.get)}")
        # decode the audio
        options = whisper.DecodingOptions(fp16 = False)
        result = whisper.decode(self.model, mel, options)
        # print the recognized text
        print("I think you said: " + result.text)
        print("Is that correct? If so, here's what I say to that:")
        return result.text
        
    def promptGTP(self, prompt, conversation_context):
        self.conversation_context += "\nMe: " + prompt
        print(conversation_context)
        conv = openai.Completion.create(
                engine="text-davinci-003",
                prompt=conversation_context,
                max_tokens=1024,
                n=1,
                stop=None,
                temperature=0.5,
            )
        message = conv.choices[0].text
        print(message)
        self.conversation_context += " \n Allin: " + message
        return message
        
    def speakText(message):
        # SPEAKING THE TEXT AFTER TRANSLATING IT!
        desired_langs = {'Taiwanese': 'zh-TW',
                        'Chinese': 'zh-CN',
                        'Korean': 'ko',
                        'Japanese': 'ja',
                        'Spanish': 'es',
                        'English': 'en',
                        'Arabic' : 'ar',
                        'Italian' : 'it',
                        'Hindi' : 'hi'
                        }
        
        desired_lang = desired_langs['English']
        
        translator = Translator()
        translated = translator.translate(message, dest=desired_lang)
        
        print(translated.text)
        
        myobj = gTTS(translated.text, lang=desired_lang, slow=False)
    
        myobj.save('response.mp3')
        
    def clearAudio(self):
        os.remove('current_speech.mp3')
        os.remove('response.mp3')
                
    #     recordAudio()
    #     prompt = processAudio()
    #     message, new_context = promptGTP(prompt, conversation_context)
    #     new_context += " \n Allin: " + message
    #     conversation_context = new_context
    #     speakText(message)
        
    #     # PLAY THE MESSAGE ON FRONT END!!
    
    # except KeyboardInterrupt:
    #     print("Exiting...")


