import os
import pygame
import time

def play_audio_from_folder(audio_path):
    #אתחול המיקסר
    pygame.mixer.init()
  

    try:
         pygame.mixer.music.load(audio_path)
         pygame.mixer.music.play()
         while pygame.mixer.music.get_busy():
            time.sleep(1)
    except:
        print(f"Error playing {audio_path}")

   




def main():
    folder_path = 'C:\Tamarush\programming\project\ChatTM\Audios'
  #רשימה לכל קבצי השמע שבתיקייה זו.
    audio_files = []
    for filename in os.listdir(folder_path):
        if filename.endswith(".mp3") or filename.endswith(".wav"):
            #תיצור קישור לקובץ
            full_path = os.path.join(folder_path, filename)
            audio_files.append(full_path)

    #אם אין קבצי שמע בתיקייה זו
    if not audio_files:
        print(f"No audio files found in: {folder_path}")
        return
    
    #הפעלת הקבצים
    for audio_path in audio_files:
        print(f"Playing: {os.path.basename(audio_path)}")
        play_audio_from_folder(audio_path)
        while pygame.mixer.music.get_busy():
            time.sleep(1)
    print("Finished playing all audio files.")




main()


