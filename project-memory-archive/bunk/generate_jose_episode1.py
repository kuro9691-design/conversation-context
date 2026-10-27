"""
Passengers 第1話（Scene1-2: ホセの朝〜タクシー乗務開始）
ホセの全セリフをGemini TTS（Charon声）で一括生成するスクリプト。
"""

import os
import time
import wave
from google import genai
from google.genai import types

API_KEY = os.environ.get("GEMINI_API_KEY")
if not API_KEY:
    raise SystemExit("環境変数 GEMINI_API_KEY が設定されていません。")

client = genai.Client(api_key=API_KEY)

VOICE = "Charon"
MODEL = "gemini-2.5-flash-preview-tts"

BASE_CHARACTER = (
    "a 63-year-old taxi driver, weathered and worn down by life, "
    "speaking in a low, tired voice with a slight gravelly texture"
)

LINES = [
    ("01", "毎日同じニュースだな。", "muttering to himself, mildly resigned, low energy"),
    ("02", "おはよう、マリア。", "speaking gently to a photo of his late wife, quiet and low, no cheerfulness"),
    ("03", "今日も暑くなりそうだな。", "continuing to speak softly to the photo, flat and calm"),
    ("04", "金が要るんだよ。", "matter-of-fact, slightly tired, talking to a fellow driver"),
    ("05", "もう3年来てない。", "a little sad, voice trailing off slightly"),
    ("06", "いい息子だな。", "quiet, a touch of envy hidden under politeness"),
    ("07", "了解。", "short, professional, neutral to a passenger"),
    ("08", "分かりました。", "short, professional, neutral to a passenger"),
    ("09", "2人います。", "brief, neutral answer to a passenger's question"),
    ("10", "…いえ。", "a short pause before answering, quiet, a little pained"),
    ("11", "…まあ。", "looking out the window while speaking, distant, subdued"),
    ("12", "…そうですか。", "turning back slightly, quiet acknowledgment"),
    ("13", "…そうですね。", "calm, quiet agreement, a little weary"),
    ("14", "ありがとうございます。", "polite, plain, to a passenger getting out"),
]


def save_wave(filename: str, pcm_data: bytes, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)


def generate(line_id: str, text: str, direction: str) -> str:
    style_prompt = (
        f"Say this line as {BASE_CHARACTER}. Direction for this specific line: {direction}. "
        f"Line: {text}"
    )
    response = client.models.generate_content(
        model=MODEL,
        contents=style_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=VOICE)
                )
            ),
        ),
    )
    candidate = response.candidates[0]
    if candidate.content is None or not candidate.content.parts:
        raise RuntimeError(f"empty response (finish_reason={candidate.finish_reason})")
    pcm_data = candidate.content.parts[0].inline_data.data
    out_path = f"jose_ep1_{line_id}.wav"
    save_wave(out_path, pcm_data)
    return out_path


if __name__ == "__main__":
    # free tier quota for gemini-2.5-flash-tts is 3 requests/minute
    REQUEST_INTERVAL_SEC = 22
    MAX_RETRIES = 2

    first = True
    for line_id, text, direction in LINES:
        out_path = f"jose_ep1_{line_id}.wav"
        if os.path.exists(out_path):
            print(f"[SKIP] {line_id}: already exists -> {out_path}")
            continue
        if not first:
            time.sleep(REQUEST_INTERVAL_SEC)
        first = False
        for attempt in range(MAX_RETRIES + 1):
            try:
                path = generate(line_id, text, direction)
                print(f"[OK] {line_id}: {text} -> {path}")
                break
            except Exception as e:
                if attempt < MAX_RETRIES:
                    print(f"[RETRY {attempt + 1}] {line_id}: {text} -> {e}")
                    time.sleep(REQUEST_INTERVAL_SEC)
                else:
                    print(f"[ERROR] {line_id}: {text} -> {e}")
