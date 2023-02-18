import whisper
from pvrecorder import PvRecorder
import wave
import struct
import os
import sys
from gtts import gTTS
from googletrans import Translator
import openai

# TO USE GTP, USE:
# export api_key=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

model = whisper.load_model("base")
recorder = PvRecorder(device_index=-1, frame_length=512)

while True:
    # RECORDING AUDIO!!!
    print("Recording audio...")
        
    for index, device in enumerate(PvRecorder.get_audio_devices()):
        print(f"[{index}] {device}")

    audio = []
    try:
        recorder.start()
        while True:
            frame = recorder.read()
            audio.extend(frame)
    except KeyboardInterrupt:
        recorder.stop()
        with wave.open('current_speech.mp3', 'w') as f:
            f.setparams((1, 2, 16000, 512, "NONE", "NONE"))
            f.writeframes(struct.pack("h" * len(audio), *audio))
    finally:
        recorder.delete()
    print("Audio recorded! (current_speech.mp3)")
    
    # PARSING AUDIO Tos AND SoT!    
    print("Parsing audio...")
    # load audio and pad/trim it to fit 30 seconds
    audio = whisper.load_audio("current_speech.mp3")
    audio = whisper.pad_or_trim(audio)
    # make log-Mel spectrogram and move to the same device as the model
    mel = whisper.log_mel_spectrogram(audio).to(model.device)
    # detect the spoken language
    _, probs = model.detect_language(mel)
    print(f"Detected language: {max(probs, key=probs.get)}")
    # decode the audio
    options = whisper.DecodingOptions(fp16 = False)
    result = whisper.decode(model, mel, options)
    # print the recognized text
    print(result.text)
    
    # CHAT GTP!
    prompt = result.text
    openai.api_key = os.environ['api_key']

    completions = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=1024,
        n=1,
        stop=None,
        temperature=0.5,
    )

    message = completions.choices[0].text
    print(message)
    
    # SPEAKING THE TEXT!
    desired_langs = {'Taiwanese': 'zh-TW',
                     'Chinese': 'zh-CN',
                     'Korean': 'ko',
                     'Japanese': 'ja',
                     'Spanish': 'es',
                     'English': 'en'
                     }
    
    desired_lang = desired_langs['Taiwanese']
    
    translator = Translator()
    translated = translator.translate(message, dest=desired_lang)
    
    myobj = gTTS(translated.text, lang=desired_lang, slow=True)
  
    myobj.save("response.mp3")
  
    os.system("mpg321 response.mp3")
    
    
