# SmartService Chat

מערכת צ'אט חכמה למוקד שירות לקוחות, המשלבת עיבוד שפה טבעית (NLP) וניתוח נתונים למתן מענה מדויק, מהיר ואישי ללקוחות.

## מבנה הריפו

- [`Felis_API/`](Felis_API) — שרת ה-API (C# / ASP.NET, .NET 8), אחראי על משתמשים, חברות, מנויים ודוחות.
- [`Felis_python/`](Felis_python) — שכבת ה-NLP ולמידת המכונה (סיווג פניות, בניית JSON, שליפת תשובות, בנייה בשפה טבעית).
- [`smart-service-client/`](smart-service-client) — לקוח ה-React (Vite).
- [`database/`](database) — סכמת מסד הנתונים.
- [`docs/`](docs) — הצעת הפרויקט, מצגת הסיכום וחומרים נלווים.

## הרצה מקומית

כל תת-פרויקט מכיל הוראות/תלויות משלו (`Felis_API/*.csproj`, `Felis_python/requirements.txt`, `smart-service-client/package.json`).
יש להעתיק את `smart-service-client/.env.example` ל-`.env` ולמלא את הערכים הדרושים לפני הרצת הלקוח.
