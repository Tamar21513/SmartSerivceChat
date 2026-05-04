#הפיכת טקסט לשמע בזמן אמת
from TTS.api import TTS
import sounddevice as sd
import soundfile as sf
import numpy as np

# יצירת אובייקט מודל YourTTS
tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts",
    progress_bar=False,
    gpu=False)


def ConversTTS(text_from_system):
    #השמעת קול ספציפי
    check_speaker = tts.speakers[0]
    # הפקת השמע כ‑numpy array
    wav = tts.tts(text_from_system,speaker=check_speaker,language="en")
    # ניגון מידי בזמן אמת
    sd.play(wav, samplerate=tts.synthesizer.output_sample_rate)
    sd.wait()

