import os
import requests
import audio_process
from flask import Flask, request, jsonify, render_template, send_file

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/record-audio", methods=["POST"])
def record_audio():
    audio_process.

@app.route("/upload-audio", methods=["POST"])
def upload_audio():
    # Get the audio file from the request
    audio_file = request.files.get("audio")

    # Upload the audio file to a remote URL
    remote_url = "http://example.com/upload"
    response = requests.post(remote_url, files={"audio": audio_file})

    if response.status_code == 200:
        # Get the URL of the uploaded audio file
        remote_audio_url = response.json().get("url")

        # Return a page with a button to play the audio file
        return render_template("play_audio.html", audio_url=remote_audio_url)
    else:
        # Return an error message if the upload failed
        return jsonify({"error": "Failed to upload audio file"})

@app.route("/play-audio", methods=["GET"])
def play_audio():
    # Get the URL of the remote audio file
    remote_audio_url = request.args.get("url")

    # Download the remote audio file
    local_audio_filename = "temp_audio.wav"
    response = requests.get(remote_audio_url)

    # Save the downloaded audio file to disk
    with open(local_audio_filename, "wb") as f:
        f.write(response.content)

    # Return the audio file for playback
    return send_file(local_audio_filename, mimetype="audio/wav", as_attachment=False)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
