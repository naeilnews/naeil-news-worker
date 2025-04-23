import tempfile
import os
from gtts import gTTS
from PIL import Image
import ffmpeg

def handler(event):
    try:
        prompt = event['input']['prompt']

        # 1. 텍스트 → 음성(mp3)
        tts = gTTS(prompt, lang='ko')
        temp_mp3 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tts.save(temp_mp3.name)

        # 2. 이미지 생성 (정적 배경)
        temp_img = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        image = Image.new('RGB', (1280, 720), color=(30, 30, 30))
        image.save(temp_img.name)

        # 3. ffmpeg 영상 생성
        temp_mp4 = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        (
            ffmpeg
            .input(temp_img.name, loop=1, t=5)
            .output(
                temp_mp4.name,
                vf="scale=1280:720,fps=25",
                pix_fmt="yuv420p",
                vcodec="libx264",
                acodec="aac",
                shortest=True,
                audio_bitrate="192k",
                **{'i': temp_mp3.name}
            )
            .overwrite_output()
            .run()
        )

        # 4. 바이너리 mp4 파일 직접 반환
        with open(temp_mp4.name, "rb") as f:
            video_binary = f.read()

        return {
            "file": video_binary
        }

    except Exception as e:
        print(f"[ERROR] {str(e)}")
        return {"error": str(e)}
