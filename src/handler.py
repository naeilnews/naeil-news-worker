from runpod.serverless.modules.rp_logging import RunPodLogger
import base64
import tempfile
import os
from gtts import gTTS
from PIL import Image
import ffmpeg

def handler(event):
    try:
        prompt = event['input']['prompt']

        # 🗣️ 1. 텍스트 → 음성(mp3)
        tts = gTTS(prompt, lang='ko')
        temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_mp3.name)

        # 🖼️ 2. 임시 이미지 생성 (배경용, 정적)
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image = Image.new('RGB', (1280, 720), color=(30, 30, 30))
        image.save(temp_img.name)

        # 🎥 3. ffmpeg로 mp4 영상 생성
        temp_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        ffmpeg.input(temp_img.name, loop=1, t=5).output(
            temp_mp4.name,
            vf="scale=1280:720",
            pix_fmt="yuv420p",
            vcodec="libx264",
            acodec="aac",
            shortest=None,
            audio_bitrate="192k",
            i=temp_mp3.name,
        ).overwrite_output().run()

        # 📦 4. mp4 파일을 base64로 인코딩
        with open(temp_mp4.name, "rb") as f:
            video_data = f.read()
            encoded_video = base64.b64encode(video_data).decode("utf-8")

        return {
            "video_base64": encoded_video
        }

    except Exception as e:
        RunPodLogger.error(str(e))
        return {"error": str(e)}
