import os
import wave
from google import genai
from google.genai import types

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise SystemExit("GEMINI_API_KEYが未設定です")

client = genai.Client(api_key=api_key)

LINE = "お客さん、今日はどこまで行くんだい？このあたりの道なら任せてくれよ！"

PROMPT = (
    "Say this in a low, tired, slightly gravelly voice — no cheerfulness, no enthusiasm, "
    "like a 63-year-old taxi driver who has just woken up after a rough night's sleep "
    "and is speaking slowly with a slight sigh in his voice: "
    f"{LINE}"
)

VOICES = ["Gacrux", "Algenib", "Charon"]

def save_wave(filename, pcm_data, channels=1, rate=24000, sample_width=2):
    with wave.open(filename, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(sample_width)
        wf.setframerate(rate)
        wf.writeframes(pcm_data)

for voice in VOICES:
    print(f"Generating voice: {voice}")
    response = client.models.generate_content(
        model="gemini-2.5-flash-preview-tts",
        contents=PROMPT,
        config=types.GenerateContentConfig(
            response_modalities=["AUDIO"],
            speech_config=types.SpeechConfig(
                voice_config=types.VoiceConfig(
                    prebuilt_voice_config=types.PrebuiltVoiceConfig(
                        voice_name=voice
                    )
                )
            ),
        ),
    )
    data = response.candidates[0].content.parts[0].inline_data.data
    filename = f"jose_{voice.lower()}.wav"
    save_wave(filename, data)
    print(f"Saved: {filename}")

print("Done")
