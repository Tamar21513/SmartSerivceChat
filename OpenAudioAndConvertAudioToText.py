import whisper
import time
import os
import torch


#טעינה
model = whisper.load_model("base")

#המרת שמע לטקסט
def Convert_audio_to_text(audio_path):
    print("Convert_audio_to_text")
    try:
        text =""
        print("\n")    
        print(f"Playing: {os.path.basename(audio_path)}")
        result = model.transcribe(audio_path, language="en")    
        text += result["text"]             
        return text.strip()
         
    except Exception as e:
        print(f"Error playing {audio_path}: {e}")
        return None



#print(Convert_audio_to_text(r"C:\Tamarush\programming\project\ChatTM\Audios\tamarMoriel.mp3"))

#המרת כל הקבצים הנמצאים בתקיה
def main():
    folder_path = 'C:\Tamarush\programming\project\ChatTM\Audios'


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
        text = Convert_audio_to_text(audio_path)
        if text:
            print(text)
            save_path = audio_path.rsplit('.', 1)[0] + '.txt'
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(text)

    print("Finished playing all audio files.")






#from openai import OpenAI
#import os
#from dotenv import load_dotenv
#
#def AudioToText():
#    load_dotenv()
#
#    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
#    audio_file_path = r"C:\Tamarush\programming\project\ChatTM\Audios\Audio0.wav"
#
#    with open(audio_file_path, "rb") as audio_file:
#        transcription = client.audio.transcriptions.create(
#            file=audio_file,
#            model="whisper-1"
#        )
#
#    print(transcription.text)
#
#AudioToText()from openai import OpenAI
#import os
#from dotenv import load_dotenv
#
#def AudioToText():
#    load_dotenv()
#
#    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
#
#    audio_file_path = r"C:\Tamarush\programming\project\ChatTM\Audios\Audio0.wav"
#
#    with open(audio_file_path, "rb") as audio_file:
#        transcription = client.audio.transcriptions.create(
#            file=audio_file,
#            model="whisper-1"
#        )
#
#    print(transcription.text)
#
#AudioToText()
