import pyodbc
from argon2 import PasswordHasher
import RealTimeTextToAudioConversion as TextToAudio

conn = pyodbc.connect( 
   "Driver={SQL Server};" 
   "Server=.\SQLEXPRESS;" 
   "Database=UserDB;" 
   "Trusted_Connection=yes;" 
) 

#להרצת שאילתות
cursor = conn.cursor()

#ברירת מחדל
ph = PasswordHasher()

def login_user(mail_uesrnama = " ", entered_password = " " ):
    
    #בדיקה אם משתמש קיים והסיסמה נכונה
    # שליפת hash של המשתמש לפי אימייל או שם משתמש
    cursor.execute(
        '''
        SELECT password_hash
        FROM Users
        WHERE email = ? OR username = ?
        ''',
        mail_uesrnama, mail_uesrnama
    )
    result = cursor.fetchone()

    if result is None:
        message = "The user does not exist in the system. Do you want to register for the system?"
        print("\n")        
        TextToAudio.ConversTTS(message)
        print(message)

        return False

    stored_hash = result[0]

    # בדיקה של הסיסמה שהוזנה מול ההאש
    try:
        if ph.verify(stored_hash, entered_password):
            message = "Login successful!"
            print("\n")
            print(message)
            TextToAudio.ConversTTS(message)

            return True
    except Exception:
        message = "One of the entered data is incorrect."
        print("\n")
        print(message)
        TextToAudio.ConversTTS(message)
        return False
    
#TRUE
#login_user('mc123456@gmail.com','As485#15')
#true
#login_user('mosh choen','As485#15')
#true
#login_user('mc123456@gmail.com','fg#15')
#false
#login_user('As485#15','t m')
#false
#login_user('Ab215131129!','moriel9847594@gmail.com')
#true
#login_user('moriel9847594@gmail.com','Ab215131129!')
