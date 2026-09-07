import OpenAudioAndConvertAudioToText as AudioToText
import DataExtraction as DExtaction





# Convert an audio file to text using the audio-to-text module
def AudioOrTextToLogin(phat_audio):
    text = AudioToText.Convert_audio_to_text(phat_audio)
    return text





text = AudioOrTextToLogin(r"C:\Tamarush\programming\project\ChatTM\Audios\name_mail_password6.mp3")
DExtaction.If_exists_inDB(text)


DExtaction.If_exists_inDB("Hello!! username: Mosh Choen, email: mc123456@gmail.com, password: As485#15 HI")
