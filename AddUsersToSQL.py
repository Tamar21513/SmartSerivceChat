import pyodbc
import os
from argon2 import PasswordHasher
import RealTimeTextToAudioConversion as TextToAudio
import DataExtraction as dExtraction

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


#בדיקה האם המשתמש כבר קיים במערכת
def user_exists(mail, nameUser):
   cursor.execute(
      '''
      SELECT Top 1 user_id FROM Users
      WHERE email = ? and username = ?
      ''',
      mail, nameUser
   )
   return cursor.fetchone() is not None

#פונקצית הוספת משתמש לערכת
def EnterUsers(password,nameUser,mail):
   nameUserL = nameUser.lower()
   mailL = mail.lower()
   if user_exists(mailL, nameUserL):
      message = "A user with this email and username already exists in the system."
      print("\n")
      print(message)        
      TextToAudio.ConversTTS(message)
      
      return

   #בדיקה אם הסיסמא היא סיסמא חזקה, אם לא יוחזר הודעה זו.
   if dExtraction.Is_strong_password(password):
      message = "The password is not a strong password. The password must contain: a lowercase or uppercase letter, a number, and a character. Minimum 8 characters."
      print("\n")
      print(message)        
      TextToAudio.ConversTTS(message)

      return
   

   #הכנסה לטבלת הגיבוב
   hashPass = ph.hash(password)
   try:
      ##הכנסת משתמשים
      cursor.execute(''' INSERT INTO Users (email, username, password_hash) VALUES 
      (?,?,?)''',
      mailL, nameUserL,hashPass) 
      conn.commit() 
      message = "User created successfully"
      print("\n") 
      print(message)        
      TextToAudio.ConversTTS(message)
      
   except pyodbc.IntegrityError:
      message = "Unable to create user – duplicate data"
      print("\n") 
      print(message)       
      TextToAudio.ConversTTS(message)
      

#EnterUsers('As485#15','Mosh Choen','mc123456@gmail.com')
#EnterUsers('Ab215131129!','Tamar Moriel','moriel9847594@gmail.com')
#EnterUsers('Ab215','nechami Moriel','moriel594@gmail.com')



print("\n")
print("All the Users")
#הדפסת משתמשים
cursor.execute('SELECT * FROM Users') 
print(type(cursor)) 
for row in cursor: 
   print(row) 


