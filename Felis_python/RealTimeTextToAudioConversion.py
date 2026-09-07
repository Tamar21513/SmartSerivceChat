from TTS.api import TTS
import sounddevice as sd
import soundfile as sf
import numpy as np

tts = TTS(model_name="tts_models/multilingual/multi-dataset/your_tts",
    progress_bar=False,
    gpu=False)


# Convert text to speech with a preset speaker and play it back immediately
def ConversTTS(text_from_system):
    check_speaker = tts.speakers[0]
    wav = tts.tts(text_from_system,speaker=check_speaker,language="en")
    sd.play(wav, samplerate=tts.synthesizer.output_sample_rate)
    sd.wait()

