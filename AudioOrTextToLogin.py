import OpenAudioAndConvertAudioToText as AudioToText
import DataExtraction as DExtaction





def AudioOrTextToLogin(phat_audio):
    text = AudioToText.Convert_audio_to_text(phat_audio)
    return text





#שמע
text = AudioOrTextToLogin(r"C:\Tamarush\programming\project\ChatTM\Audios\name_mail_password6.mp3")
DExtaction.If_exists_inDB(text)


#טקסט
DExtaction.If_exists_inDB("Hello!! username: Mosh Choen, email: mc123456@gmail.com, password: As485#15 HI")
