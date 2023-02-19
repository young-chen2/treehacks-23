import os
import requests
import audio_process
from flask import Flask, request, jsonify, render_template, send_file
from google.cloud import storage

app = Flask(__name__)
pipeline = audio_process.AudioProcess()

BUCKET_NAME = "storied-deck-378303_cloudbuild"

@app.route("/")
def index():
    return render_template("cafe.html")

@app.route("/record-audio")
def record_audio():
    pipeline.imports()
    pipeline.recordAudio() # records for 10 seconds, saves audio locally
    prompt = pipeline.processAudio() # parses audio, saves audio locally
    message = pipeline.promptGTP(prompt, pipeline.conversation_context)
    pipeline.speakText(message)

@app.route("/delete-audio")
def delete_audio():
    pipeline.deleteAudio()

@app.route("/upload-audio", methods=['POST'])
def upload_audio():
    # Get the uploaded file
    file = request.files['response.mp3']

    # Create a client object for Google Cloud Storage
    client = storage.Client()

    # Get a reference to the bucket
    bucket = client.get_bucket(BUCKET_NAME)

    # Create a blob object with the name of the uploaded file
    blob = bucket.blob(file.filename)

    # Upload the file to the blob
    blob.upload_from_string(
        file.read(),
        content_type=file.content_type
    )

    # Return the URL of the uploaded file
    return blob.public_url


@app.route("/play-audio", methods=["GET"])
def play_audio():
    client = storage.Client()

    # Get a reference to the bucket
    bucket = client.get_bucket(BUCKET_NAME)

    # Get a reference to the blob
    blob = bucket.blob('response.mp3')

    # Download the blob into memory as bytes
    file_content = blob.download_as_bytes()

    # Create a response object with the file content and appropriate headers
    response = app.make_response(file_content)
    response.headers['mp3'] = blob.content_type
    response.headers['attachment'] = f'attachment; filename="{blob.name}"'

    # Serve the response
    return response

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
