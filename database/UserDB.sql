create database SmartServiceChatDB;

--טבלת סוגי מנויים
CREATE TABLE Subscriptions (
    subscription_id INT IDENTITY(1,1) PRIMARY KEY,
    subscription_name VARCHAR(100) NOT NULL,   -- שם המנוי
    duration_days INT NOT NULL,                -- אורך המנוי בימים
    priority INT NOT NULL,                     -- עדיפות
	price INT NOT NULL,
	description VARCHAR(255) NULL,
	is_active BIT NOT NULL DEFAULT 1,
    subscription_type VARCHAR(20) NOT NULL    -- Company / Customer
);


--משתמשים
CREATE TABLE Users(
    user_id INT IDENTITY(1,1) PRIMARY KEY, 
    username VARCHAR(50) NOT NULL, 
    email VARCHAR(100) UNIQUE,  
    password_hash VARCHAR(255) NOT NULL,
	city VARCHAR(50) NULL,
	age INT NULL,
	occupation VARCHAR(50) NULL,
	role VARCHAR(50) NOT NULL,
	subscription_id INT NOT NULL,
	subscription_start_date DATETIME NOT NULL DEFAULT GETDATE(),
	FOREIGN KEY (subscription_id) REFERENCES Subscriptions(subscription_id)
);




--חברות מנויות
CREATE TABLE Company (
    company_id INT IDENTITY(1,1) PRIMARY KEY,
    company_name VARCHAR(150) NOT NULL,
	password_hash VARCHAR(255) NOT NULL,
    is_active BIT NOT NULL,
	subscription_id INT NOT NULL,
	subscription_start_date DATETIME NOT NULL DEFAULT GETDATE(),
	FOREIGN KEY (subscription_id) REFERENCES Subscriptions(subscription_id)
);


--מסדי נתוני חברות
CREATE TABLE CompanyData (
    data_id INT IDENTITY(1,1) PRIMARY KEY,
    company_id INT NOT NULL UNIQUE,
    title VARCHAR(200) NOT NULL,
    content NVARCHAR(MAX) NOT NULL,
    topic VARCHAR(MAX) NOT NULL,

    FOREIGN KEY (company_id) REFERENCES Company(company_id)
);


--טבלת שיחות
CREATE TABLE Reports (
    report_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT GETDATE(),
    report_content NVARCHAR(MAX) NOT NULL,

    FOREIGN KEY (user_id) REFERENCES Users(user_id)
);


--טבלת מה יש לו
CREATE TABLE ThingsTheUserHas (
    ThingsTheUserHas_id INT IDENTITY(1,1) PRIMARY KEY,
    user_id INT NOT NULL,
    ThingsTheUserHas_content NVARCHAR(MAX) NOT NULL,

    FOREIGN KEY (user_id) REFERENCES Users(user_id),
	CONSTRAINT UQ_ThingsTheUserHas_UserId UNIQUE (user_id)
);

--קטגוריות
CREATE TABLE Category (
    category_id INT IDENTITY(1,1) PRIMARY KEY,
    category_name NVARCHAR(100) NOT NULL UNIQUE
);


--קטגוריה לחברה
CREATE TABLE CompanyCategories (
    company_category_id INT IDENTITY(1,1) PRIMARY KEY,

    company_id INT NOT NULL,
    category_id INT NOT NULL,

    priority INT NOT NULL,

    FOREIGN KEY (company_id) REFERENCES Company(company_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id),

    CONSTRAINT UQ_Company_Category UNIQUE (company_id, category_id),
    CONSTRAINT CK_CompanyCategories_Priority CHECK (priority > 0)
);










--הכנסת נתונים לטבלת מנויים
INSERT INTO Subscriptions
(
    subscription_name,
    duration_days,
    priority,
    price,
    description,
	is_active,
    subscription_type
)
VALUES
(
    'Company Basic',
    30,
    3,
    99,
    'For small companies with a low number of support requests.',
	1,
    'Company'
),
(
    'Company Pro',
    180,
    2,
    499,
    'For companies with a medium number of support requests.',
	1,
    'Company'
),
(
    'Company Premium',
    365,
    1,
    899,
    'High priority, extended service, and advanced management.',
	0,
    'Company'
),
(
    'Customer Basic',
    30,
    3,
    5,
    'A symbolic payment for basic system usage.',
	1,
    'Customer'
),
(
    'Customer Plus',
    90,
    2,
    12,
    'Better access with extended conversation history.',
	1,
    'Customer'
);





--הכנסת נתונים למשתמשים
INSERT INTO Users (username, email, password_hash, age, city , occupation, role, subscription_id, subscription_start_date)
VALUES
(
    'mosh chen',
    'mc123456@gmail.com',
    '$argon2id$v=19$m=65536,t=3,p=4$rtP1L8lwS//aVs+GFqkZ/w$N2CdUOMvomY58tRAGDsBMmzHGwC59uSvrE2C2KM/t44',
	54,
	'',
	'',
    'user',
	4,
	'05-27-2026'
),
(
    'tamar moriel',
    'moriel9847594@gmail.com',
    '$argon2id$v=19$m=65536,t=3,p=4$+9VCtvr+mDDUXpzo9HkNQA$IVfhif00c52/jPSq5MaIgJ5oEQRhMQovF7+o+Sh3FfE',
	NULL,
	'Tel Aviv',
	'',
    'admin',
	5,
	'05-27-2026'
),
(
    'nechami moriel',
    'moriel594@gmail.com',
    '$argon2id$v=19$m=65536,t=3,p=4$L4zptfNM/KfHj5PkJz4WlQ$F/AHkWsEi9i135n7VEb0qeJntAazKjWzji4OzhA+IWc',
	NULL,
	'',
	'',
    'user',
	4,
	'05-27-2026'
);


--הכנסת נתונים לחברות
INSERT INTO Company (company_name,password_hash, is_active,subscription_id,subscription_start_date)
VALUES
('El Al','$argon2id$v=19$m=65536,t=3,p=4$3Lfvf++Gbe28pfRKqqeT3Q$/vf9OtQFVsSOZkrLHDfELHTd33XPq3vvKZACb8wlIbw', 1,1,'05-27-2026'),
('JBL','$argon2id$v=19$m=65536,t=3,p=4$Fa+5jVKJfG//IwMdGgy0nQ$eLoKkJCdr9f27xeElu8aJWhwCjIDRoOLtOTEWUb9ICc', 1,2,'05-27-2026'),
('osem','$argon2id$v=19$m=65536,t=3,p=4$nd59L3mpT3HDSYt7RKM0rQ$a7tLn4S2uzCswySjN9YUDdTfZZiZ3U3sfd5XCo1A7Rk', 1,3,'05-27-2026'),
('Eged','$argon2id$v=19$m=65536,t=3,p=4$PQc44qXgPse8Gyo95Lk8qQ$axnqzKe+Zjch9oIovvNkEekv8uv9eYdGCPl/65p8wEU', 1,1,'05-27-2026')






--הכנסת נתונים לטבלת שיחות
DECLARE @UserId INT;

SELECT @UserId = 3
FROM Users
WHERE username = N'nechami moriel';

IF @UserId IS NULL
BEGIN
	THROW 50001, 'User nechami_moriel was not found in Users table.', 1;
END;

BEGIN TRANSACTION;

INSERT INTO Reports (user_id, report_content)
VALUES (@UserId, N'Transcript:
Bot: Hello, I am Smart Service Chat. How can I help you?
User: I’m looking for comfortable headphones for working from home.
Bot: Over-ear or in-ear?
User: Over-ear, comfort is key.
Bot: The NoiseCancel Pro series offers active noise cancellation, memory foam padding, and 30 hours battery life.
User: Can I connect to multiple devices?
Bot: Yes, switch between laptop and phone easily.
User: Sound quality for calls?
Bot: Excellent, built-in mic with noise reduction.
User: Music quality?
Bot: Deep bass, balanced treble, clear highs.

Topics in report:
Headphones
comfortable headphones
over-ear headphones
NoiseCancel Pro series

Headphone features
active noise cancellation
memory foam padding
30 hours battery life
multipoint connection

Call quality
built-in microphone
noise reduction
clear call sound

Music quality
deep bass
balanced treble
clear highs


Sentiment and Emotions:
Sentiment: Positive
Emotions detected: Interest, Satisfaction, Excitement, Confidence
');

INSERT INTO Reports (user_id, report_content)
VALUES (@UserId, N'Transcript:
Bot: Hello, I am Smart Service Chat. How can I help you?
User: Hi, I want a smartwatch that works well for workouts and some good headphones for calls.
Bot: Perfect. The smartwatch tracks heart rate, calories, sleep, and has multiple sports modes. Which headphones do you need?
User: Over-ear, noise cancelling, long battery.
Bot: Check out the NoiseCancel Pro series. Active noise cancellation, memory foam, 30 hours battery, multipoint Bluetooth.
User: Great. What about the smartwatch battery?
Bot: 7 days standard, 14 days in power-saving.
User: Also, do you have JBL ENCORE speakers?
Bot: Yes, JBL ENCORE provides high-powered sound and LED lights. Very popular for home parties.

Topics in report:
Smartwatch
workout tracking
heart rate tracking
calorie tracking
sleep tracking
multiple sports modes

Smartwatch battery
7 days standard battery
14 days power-saving battery

Headphones
over-ear headphones
noise cancelling headphones
long battery life
NoiseCancel Pro series

Headphone features
active noise cancellation
memory foam
30 hours battery
multipoint Bluetooth

JBL ENCORE
high-powered sound
LED lights
home party speaker

Sentiment and Emotions:
Sentiment: Positive
Emotions detected: Interest, Satisfaction, Excitement, Confidence
');

INSERT INTO Reports (user_id, report_content)
VALUES (@UserId, N'Transcript:
Bot: Hello, I am Smart Service Chat. How can I help you?
User: Hello, I need some clarifications about your smartwatches.
Bot: Sure! Which model are you interested in?
User: Mainly your latest one. I want a device that tracks workouts and sleep.
Bot: The latest model tracks heart rate, steps, sleep, has multiple sports modes, and built-in GPS. Notifications and calls are supported.
User: Battery life and water resistance?
Bot: Battery lasts 7 days standard, 14 in power-saving. Water-resistant up to 50 meters.
User: Colors available?
Bot: Black, silver, rose gold.
User: Also, I was looking at the JBL ENCORE and the JBL GO 4.
Bot: JBL ENCORE gives high-power audio with LED lights, JBL GO 4 is compact for casual use.
User: I’ll get the JBL ENCORE as well.
Bot: Great choice!

Topics in report:
Smartwatch
latest smartwatch model
workout tracking
sleep tracking
heart rate tracking
steps tracking
multiple sports modes
built-in GPS
notifications
calls support

Smartwatch battery
7 days standard battery
14 days power-saving battery

Water resistance
water-resistant up to 50 meters

Smartwatch colors
black
silver
rose gold

JBL ENCORE
high-power audio
LED lights

JBL GO 4
compact speaker
casual use

computer:
vivobook
14/15/17

Purchase
customer chose JBL ENCORE

Sentiment and Emotions:
Sentiment: Positive
Emotions detected: Interest, Satisfaction, Excitement, Confidence
');

INSERT INTO Reports (user_id, report_content)
VALUES (@UserId, N'Transcript:
Bot: Hello, I am Smart Service Chat. How can I help you?
User: Hi, I’m thinking about buying your latest smartwatch. Can you tell me all the details?
Bot: Absolutely! The GRT7 Smartwatch features a 1.78-inch AMOLED display, heart rate monitoring, sleep tracking, and 4G connectivity. Would you like to know more about fitness tracking or notifications first?
User: Fitness tracking mainly. I want precise workout monitoring.
Bot: Great! It has built-in GPS, over 20 sports modes, automatic activity recognition, calorie tracking, and weekly reports.
User: Battery life?
Bot: Up to 7 days normal usage, 14 days in power-saving mode.
User: Water resistance?
Bot: Up to 50 meters. Suitable for swimming.
User: Color options?
Bot: Black, silver, rose gold. Straps are interchangeable.
User: Warranty?
Bot: 2 years, covering hardware defects.
User: Also, I’m curious about your JBL GO 4 and JBL ENCORE speakers.
Bot: The JBL GO 4 is compact with Bluetooth, while the JBL ENCORE provides more powerful sound and LED lights.
User: I’ll buy the JBL ENCORE too.
Bot: Excellent choice!

Topics in report:
GRT7 Smartwatch
1.78-inch AMOLED display
heart rate monitoring
sleep tracking
4G connectivity

Fitness tracking
built-in GPS
over 20 sports modes
automatic activity recognition
calorie tracking
weekly reports

Smartwatch battery
up to 7 days normal usage
up to 14 days power-saving mode

Water resistance
up to 50 meters
suitable for swimming

Smartwatch colors
black
silver
rose gold
interchangeable straps

Warranty
2 years warranty
hardware defects coverage

JBL GO 4
compact Bluetooth speaker

JBL ENCORE
powerful sound
LED lights

computer
Asus
vivobook
14/15/17

Purchase
customer chose JBL ENCORE

Sentiment and Emotions:
Sentiment: Positive
Emotions detected: Curiosity, Excitement, Satisfaction, Confidence, Joy
');

INSERT INTO Reports (user_id, report_content)
VALUES (@UserId, N'Transcript:
Bot: Hello, I am Smart Service Chat. How can I help you?
User: Hello, I want to check my eligibility for social security benefits.
Bot: Of course! Are you interested in child benefits, disability, or unemployment?
User: Child benefits.
Bot: Please provide your ID number and number of children.
User: ID 123456789, two children.
Bot: You are eligible for full child benefits.
User: How do I receive the payments?
Bot: Transferred to your registered bank account at the start of each month.
User: What if the number of children changes later?
Bot: Update your information on the website or via the service center, and your benefits will adjust accordingly.

Topics in report:
Social security benefits
benefit eligibility
child benefits

Customer details
ID number 123456789
two children

Eligibility result
eligible for full child benefits

Payments
payments transferred to registered bank account
payments at the start of each month

Updating details
update number of children
update information on website
update through service center
benefits adjust after update

Sentiment and Emotions:
Sentiment: Positive
Emotions detected: Interest, Relief, Satisfaction, Confidence
');

COMMIT TRANSACTION;



SELECT @UserId = 1
FROM Users
WHERE username = N'mosh chen';

IF @UserId IS NULL
BEGIN
	THROW 50001, 'User mosh chen was not found in Users table.', 1;
END;

BEGIN TRANSACTION;


INSERT INTO Reports (user_id, report_content)
VALUES (@UserId, N'Transcript:
Bot: Hello, I am Smart Service Chat. How can I help you?
User: Hello, I need help choosing a laptop for programming studies.
Bot: Sure. Do you prefer a lightweight laptop or stronger performance?
User: Performance is more important. I will use Visual Studio, SQL Server, Python, and React.
Bot: I recommend at least Intel i5 or Ryzen 5, 16GB RAM, and 512GB SSD.
User: Is 8GB RAM enough?
Bot: It can work for basic use, but for programming with several tools open, 16GB is much better.
User: What about storage?
Bot: 512GB SSD is recommended. If you work with models or many projects, 1TB is even better.
User: Does it need a dedicated graphics card?
Bot: Not required for regular programming, but helpful for AI, image processing, or heavier tasks.

Topics in report:
Laptop choice
laptop for programming studies
performance preference

Programming tools
Visual Studio
SQL Server
Python
React

Recommended specifications
Intel i5 or Ryzen 5
16GB RAM
512GB SSD

RAM
8GB RAM basic use
16GB RAM recommended for programming

Storage
512GB SSD recommended
1TB better for many projects or models

Graphics card
not required for regular programming
helpful for AI
helpful for image processing
helpful for heavier tasks

Sentiment and Emotions:
Sentiment: Positive
Emotions detected: Interest, Focus, Confidence
');

INSERT INTO Reports (user_id, report_content)
VALUES (@UserId, N'Transcript:
Bot: Hello, I am Smart Service Chat. How can I help you?
User: Hi, I want to know if my order has already shipped.
Bot: I can help with that. Please provide your order number.
User: Order number is 784512.
Bot: Thank you. Your order was shipped yesterday and is currently in transit.
User: When should it arrive?
Bot: Estimated delivery is within 2 business days.
User: Can I change the delivery address?
Bot: Since the order has already shipped, address changes may be limited. You can contact delivery support with the tracking number.
User: What is the tracking number?
Bot: Tracking number: TRK-784512-IL.

Topics in report:
Order status
order number 784512
order already shipped
order in transit

Delivery
estimated delivery within 2 business days

Delivery address
address change may be limited after shipping
contact delivery support

Tracking
tracking number TRK-784512-IL

Sentiment and Emotions:
Sentiment: Neutral-Positive
Emotions detected: Concern, Relief, Satisfaction
');

INSERT INTO Reports (user_id, report_content)
VALUES (@UserId, N'Transcript:
Bot: Hello, I am Smart Service Chat. How can I help you?
User: Hello, I have a problem logging into my account.
Bot: What happens when you try to log in?
User: It says the password is incorrect, but I am sure it is right.
Bot: Try resetting the password using the “Forgot Password” option.
User: I did not receive the email.
Bot: Please check spam or promotions folders. Also make sure the email address is typed correctly.
User: The email is correct.
Bot: In that case, wait a few minutes and try again. If it still does not arrive, support can manually verify your account.
User: Can I still access my previous orders after reset?
Bot: Yes. Resetting the password does not delete order history or account data.

Topics in report:
Login problem
incorrect password message
customer believes password is correct

Password reset
use Forgot Password option
reset password process

Reset email
email not received
check spam folder
check promotions folder
verify email address

Manual support
wait a few minutes
support can manually verify account

Account data
previous orders remain accessible
password reset does not delete order history
password reset does not delete account data

Sentiment and Emotions:
Sentiment: Mixed
Emotions detected: Frustration, Concern, Relief
');

INSERT INTO Reports (user_id, report_content)
VALUES (@UserId, N'Transcript:
Bot: Hello, I am Smart Service Chat. How can I help you?
User: Hi, I want to return a product I bought last week.
Bot: I can help. What product would you like to return?
User: A Bluetooth speaker. It works, but it is not loud enough for me.
Bot: Returns are accepted within 14 days if the product is in good condition and includes the original packaging.
User: I still have the box.
Bot: Great. You can open a return request from your account under Orders.
User: Do I get a full refund?
Bot: If the product is returned complete and undamaged, you should receive a full refund.
User: How long does the refund take?
Bot: Usually 3 to 7 business days after the returned product is received.

Topics in report:
Product return
return product bought last week
Bluetooth speaker
speaker not loud enough

Return policy
returns accepted within 14 days
product must be in good condition
original packaging required

Return request
open return request from account
use Orders section

Refund
full refund if product is complete
full refund if product is undamaged

Refund time
3 to 7 business days
refund after returned product is received

Sentiment and Emotions:
Sentiment: Neutral
Emotions detected: Uncertainty, Calm, Satisfaction
');


COMMIT TRANSACTION;







--הכנסת נתונים לטבלת מה שיש לו.
INSERT INTO ThingsTheUserHas(user_id ,ThingsTheUserHas_content)
VALUES
(1,'Programming Laptop
Visual Studio
SQL Server
Python
React

Order
784512
TRK-784512-IL

Account
Previous orders
Account data

Bluetooth Speaker
Original box
'),
(3,'NoiseCancel Pro Headphones
Over-ear
Noise cancelling
Memory foam
30 hours battery
Multipoint Bluetooth
Built-in mic

Smartwatch
Workout tracking
Heart rate
Calories
Sleep tracking
Sports modes
GPS
7 days battery
14 days power-saving

Karaoke
JBL ENCORE
High-powered sound
LED lights

Speaker
JBL GO 4
Compact
Bluetooth

GRT7 Smartwatch
1.78-inch AMOLED
Heart rate monitoring
Sleep tracking
4G connectivity
GPS
20 sports modes
Calorie tracking
Weekly reports
50 meters water resistance
Black
Silver
Rose gold
Interchangeable straps
2 years warranty

Child Benefits
ID 123456789
Two children
Full eligibility
Registered bank account
Monthly payments

computer
asus
vivobook
14/15/17
')



--הכנסת נתונים קטגוריות
INSERT INTO Category(category_name)
VALUES
('food'),
('Candy'),
('Electrical products'),
('Flights'),
('Jewelry'),
('Transportation services')


--הכנסת קטגוריות לחברה
INSERT INTO CompanyCategories(company_id,category_id,priority)
VALUES
(1,4,3),
(2,3,2),
(3,1,1),
(3,2,1),
(4,5,3)




--שליפת סוגי מנויי חברה
SELECT * from Subscriptions where Subscriptions.subscription_type = 'Company';

--שליפת סוגי מנויי לקוח
SELECT * from Subscriptions where Subscriptions.subscription_type = 'Customer';

SELECT * from Users

SELECT user_id , report_content from Reports


SELECT * FROM ThingsTheUserHas
SELECT * from Users
SELECT * from Reports
SELECT * from Company
SELECT * from CompanyData
SELECT * from CompanyCategories



delete from Company
select report_id,report_content  FROM Reports
WHERE report_id = 23;


SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
ORDER BY TABLE_NAME;