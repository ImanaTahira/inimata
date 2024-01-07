# Contoh Flask Backend (flask_app.py)
from flask import Flask, request, jsonify
import subprocess
import psutil  # Pastikan untuk menginstal psutil dengan 'pip install psutil'
import threading

app = Flask(__name__)

ffmpeg_process = None

def shutdown_server():
    func = request.environ.get('werkzeug.server.shutdown')
    if func is not None:
        func()

@app.route("/start_streaming", methods=["POST"])
def start_streaming():
    global ffmpeg_process

    input_video = request.form.get("input_video")
    rtmp_url = request.form.get("rtmp_url")

    ffmpeg_command = (
        f'ffmpeg -re -i "{input_video}" -c:v libx264 -preset veryfast '
        f'-maxrate 3000k -bufsize 6000k -c:a aac -b:a 192k -ac 2 -ar 44100 -f flv "{rtmp_url}"'
    )

    ffmpeg_process = subprocess.Popen(ffmpeg_command, shell=True, start_new_session=True)
    return jsonify({"status": "streaming started"})

@app.route("/stop_streaming", methods=["POST"])
def stop_streaming():
    global ffmpeg_process

    if ffmpeg_process:
        try:
            parent = psutil.Process(ffmpeg_process.pid)
            for child in parent.children(recursive=True):
                child.terminate()
            parent.terminate()
            parent.wait()
            ffmpeg_process = None
            # Memanggil fungsi shutdown untuk menghentikan server Flask
            threading.Thread(target=shutdown_server).start()
            return jsonify({"status": "streaming stopped"})
        except Exception as e:
            return jsonify({"status": f"Error stopping streaming: {e}"}), 500
    else:
        return jsonify({"status": "No streaming process to stop"}), 400

if __name__ == "__main__":
    app.run(debug=True)
