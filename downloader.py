from flask import Flask, request, render_template, send_file
from pytubefix import YouTube
import os
import subprocess
import threading

app = Flask(__name__)

def merge_audio_video(video_path, audio_path, output_path):
    command = [
        "ffmpeg", "-i", video_path, "-i", audio_path, "-c:v", "copy", "-c:a", "aac", "-strict", "experimental", output_path
    ]
    subprocess.run(command, check=True)
    return output_path

def delete_files_later(*files):
    def delete_task():
        import time
        time.sleep(10)  # 10초 후 파일 삭제
        for file in files:
            if os.path.exists(file):
                os.remove(file)
    threading.Thread(target=delete_task, daemon=True).start()

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url = request.form['url']
        try:
            yt = YouTube(url)
            video_stream = yt.streams.filter(res="720p", mime_type="video/mp4").first()
            audio_stream = yt.streams.filter(only_audio=True, mime_type="audio/mp4").first()

            if not video_stream or not audio_stream:
                return render_template('index.html', error="Error: 720p video or audio stream not available.")

            title = yt.title.replace(" ", "_").replace("/", "_").replace("\\", "_")
            video_path = video_stream.download(filename=f"{title}_video.mp4")
            audio_path = audio_stream.download(filename=f"{title}_audio.mp4")
            output_path = f"{title}.mp4"

            merge_audio_video(video_path, audio_path, output_path)

            delete_files_later(video_path, audio_path, output_path)

            return send_file(output_path, as_attachment=True)
        except Exception as e:
            return render_template('index.html', error=f"Error: {str(e)}")

    return '''
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>YouTube 다운로더</title>
        <style>
            * {
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: 'Noto Sans KR', sans-serif;
            }
            body {
                background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            .container {
                background-color: white;
                border-radius: 10px;
                box-shadow: 0 10px 20px rgba(0,0,0,0.1);
                padding: 30px;
                width: 100%;
                max-width: 600px;
                text-align: center;
            }
            h1 {
                color: #FF0000;
                margin-bottom: 20px;
                font-size: 2.5rem;
            }
            .logo {
                font-size: 4rem;
                margin-bottom: 20px;
                color: #FF0000;
            }
            form {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }
            input[type="text"] {
                padding: 15px;
                border: 2px solid #e1e1e1;
                border-radius: 5px;
                font-size: 16px;
                width: 100%;
                transition: border-color 0.3s;
            }
            input[type="text"]:focus {
                border-color: #FF0000;
                outline: none;
            }
            button {
                background-color: #FF0000;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                cursor: pointer;
                transition: background-color 0.3s;
            }
            button:hover {
                background-color: #cc0000;
            }
            .instructions {
                margin-top: 30px;
                text-align: left;
                color: #666;
            }
            .error {
                color: #FF0000;
                margin-top: 20px;
                font-weight: bold;
            }
            .footer {
                margin-top: 30px;
                font-size: 14px;
                color: #888;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="logo">
                <i class="fab fa-youtube"></i>
                ▶
            </div>
            <h1>YouTube 다운로더</h1>
              
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
              
            <form method="post">
                <input type="text" name="url" placeholder="YouTube URL을 입력하세요" required>
                <button type="submit">720p 영상 다운로드</button>
            </form>
              
            <div class="instructions">
                <h3>사용 방법:</h3>
                <ol>
                    <li>YouTube 영상 URL을 입력합니다.</li>
                    <li>다운로드 버튼을 클릭합니다.</li>
                    <li>720p 품질의 영상이 자동으로 다운로드됩니다.</li>
                </ol>
            </div>
              
            <div class="footer">
                &copy; 2025 YouTube 다운로더 - 개인 용도로만 사용하세요
            </div>
        </div>
    </body>
    </html>
    '''

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
