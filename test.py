import audio_process

pipeline = audio_process.AudioProcess()

pipeline.imports()
pipeline.recordAudio() # records for 10 seconds, saves audio locally
prompt = pipeline.processAudio() # parses audio, saves audio locally
message = pipeline.promptGTP(prompt, pipeline.conversation_context)
pipeline.speakText(message)
