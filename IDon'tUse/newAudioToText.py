import whisper
import os
from pydub import AudioSegment

# טען את המודל
model = whisper.load_model("base")  # אפשר לשנות ל-large אם רוצים דיוק גבוה





def transcribe_near_real_time(audio_path, segment_ms=5000):
    """
    מחלק את קובץ האודיו לסגמנטים ומדפיס תמלול באנגלית כמעט בזמן אמת.
    segment_ms = אורך הסגמנט במילישניות (כאן 5 שניות)
    """
    audio = AudioSegment.from_file(audio_path)
    total_length = len(audio)
    
    print(f"Transcribing: {os.path.basename(audio_path)}")
    senResult=""
    for start_ms in range(0, total_length, segment_ms):
        end_ms = min(start_ms + segment_ms, total_length)
        segment = audio[start_ms:end_ms]
        
        # שמור זמנית
        temp_file = "temp_segment.wav"
        segment.export(temp_file, format="wav")
        
        # תמלול
        result = model.transcribe(temp_file, language="en")
        text = result["text"]
        senResult+=text
        print(text, end=' ', flush=True)  # מציג מיידית את הטקסט
        
    print("\n--- Finished ---")
    print('-'*50)
    return senResult


def main():
    folder_path = r'C:\Tamarush\programming\project\ChatTM\Audios'


    #יצירת מערך קישורים לקבצי האודיו
    audio_files = [
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.endswith((".mp3", ".wav"))
    ]

    #אם אין קבצי שמע בתיקייה זו
    if not audio_files:
        print(f"No audio files found in: {folder_path}")
        return
    
    #המרת הקבצים לטקסט
    for audio_path in audio_files:
        text = transcribe_near_real_time(audio_path)
        if text:
            print(text)
            save_path = audio_path.rsplit('.', 1)[0] + '.txt'
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)

    print("Finished playing all audio files.")




#main()








#import whisper
#
#model = whisper.load_model("base")
#
#
#
#
#def transcribe_near_real_time(audio_path, segment_ms=5000):
#    """
#    מחלק את קובץ האודיו לסגמנטים ומדפיס תמלול באנגלית כמעט בזמן אמת.
#    segment_ms = אורך הסגמנט במילישניות (כאן 5 שניות)
#    """
#    audio = AudioSegment.from_file(audio_path)
#    total_length = len(audio)
#    
#
#    
#    for start_ms in range(0, total_length, segment_ms):
#        end_ms = min(start_ms + segment_ms, total_length)
#        segment = audio[start_ms:end_ms]
#        
#        # שמור זמנית
#        temp_file = "temp_segment.wav"
#        segment.export(temp_file, format="wav")
#        
#        # תמלול
#        audio = whisper.load_audio(temp_file)
#        audio = whisper.pad_or_trim(audio)
#
#        # make log-Mel spectrogram and move to the same device as the model
#        mel = whisper.log_mel_spectrogram(audio, n_mels=model.dims.n_mels).to(model.device)
#
#        # detect the spoken language
#        _, probs = model.detect_language(mel)
#        print(f"Detected language: {max(probs, key=probs.get)}")
#
#        # decode the audio
#        options = whisper.DecodingOptions()
#        result = whisper.decode(model, mel, options)
#        text = result.text
#        print(text, end=' ', flush=True)  # מציג מיידית את הטקסט
#        
#    print("\n--- Finished ---")
#

#transcribe_near_real_time("C:\Tamarush\programming\project\ChatTM\Audios\Audio1.mp3")


#from faster_whisper import WhisperModel
#
#model_size = "small.en"
#
## Run on GPU with FP16
#model = WhisperModel(model_size, device="cpu", compute_type="float16")
#
## or run on GPU with INT8
## model = WhisperModel(model_size, device="cuda", compute_type="int8_float16")
## or run on CPU with INT8
## model = WhisperModel(model_size, device="cpu", compute_type="int8")
#
#segments, info = model.transcribe(r"C:\Tamarush\programming\project\ChatTM\Audios\Audio1.mp3", beam_size=5)
#
#print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
#
#for segment in segments:
#    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))


#from faster_whisper import WhisperModel, BatchedInferencePipeline
#
#model = WhisperModel("turbo", device="cpu", compute_type="float16")
#batched_model = BatchedInferencePipeline(model=model)
#segments, info = batched_model.transcribe(r"C:\Tamarush\programming\project\ChatTM\Audios\Audio1.mp3", batch_size=16)
#
#for segment in segments:
#    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))