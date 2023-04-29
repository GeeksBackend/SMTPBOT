from aiogram import Bot, Dispatcher, types, executor
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.dispatcher.storage import FSMContext
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from dotenv import load_dotenv
from email.message import EmailMessage
import smtplib, os, logging, sqlite3, time, random

load_dotenv('.env')

db = sqlite3.connect('database.db')
cursor = db.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users(
    id INT,
    first_name VARCHAR(255),
    last_name VARCHAR(255),
    username VARCHAR(255),
    email VARCHAR(255),
    chat_id INT,
    balance INT,
    created VARCHAR(255)
    );
""")
cursor.execute("""CREATE TABLE IF NOT EXISTS verify_codes(
    id INT, 
    code INT,
    email VARCHAR(255)
    );
""")
cursor.connection.commit()

bot = Bot(os.environ.get('token'))
dp = Dispatcher(bot, storage=MemoryStorage())
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()

@dp.message_handler(commands=['start'])
async def start(message:types.Message):
    cursor = db.cursor()
    cursor.execute(f"SELECT id FROM users WHERE id = {message.chat.id};")
    res = cursor.fetchall()
    if res == []:
        cursor.execute(f"""INSERT INTO users VALUES 
        ('{message.from_user.id}', 
        '{message.from_user.first_name}', 
        '{message.from_user.last_name}',
        '{message.from_user.username}',
        'NULL',
        {message.chat.id}, 
        0, 
        '{time.ctime()}');""")
    cursor.connection.commit()
    await message.answer("Start Bot")

@dp.message_handler(commands=['bonus'])
async def get_bonus(message:types.Message):
    random_balance = random.randint(1, 1000)
    cursor = db.cursor()
    cursor.execute(f"UPDATE users SET balance = balance + {random_balance} WHERE id = {message.from_user.id};")
    cursor.connection.commit()
    await message.answer(f"Вы получили бонус в размере {random_balance}$")

class VerifyState(StatesGroup):
    email = State()
    code = State()

@dp.message_handler(commands=['verify'])
async def verify_email(message:types.Message):
    await message.answer("Введите свою почту:")
    await VerifyState.email.set()

@dp.message_handler(state=VerifyState.email)
async def send_verify_mail(message:types.Message, state:FSMContext):
    await message.answer("Генерирую код")
    verify_code = random.randint(111111, 999999)
    sender = os.environ.get('smtp_email')
    password = os.environ.get('smtp_password')

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    msg = EmailMessage()
    msg['Subject'] = "Geeks Game Bot"
    msg['From'] = os.environ.get('SMTP_EMAIL')
    msg['To'] = message.text
    msg.set_content(f"Здраствуйте {message.from_user.full_name}. Вот код потверждения {verify_code}")

    try:
        server.login(sender, password)
        server.send_message(msg)
        cursor = db.cursor()
        cursor.execute(f"SELECT * FROM verify_codes WHERE id = {message.from_user.id};")
        res = cursor.fetchall()
        if res == []:
            cursor.execute(f"INSERT INTO verify_codes VALUES ({message.from_user.id}, {verify_code}, '{message.text}');")
        else:
            cursor.execute(f"UPDATE verify_codes SET code = {verify_code} WHERE id = {message.from_user.id};")
        cursor.connection.commit()
        await message.answer("Код потверждения отправлена на почту")
    except Exception as error:
        await message.answer("Ошибка отправления")
    await message.answer("Введите код потверждения:")
    await VerifyState.code.set()

@dp.message_handler(state=VerifyState)
async def check_code(message:types.Message, state:FSMContext):
    await message.answer("Начинаю проверку")
    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM verify_codes WHERE id = {message.from_user.id};")
    res = cursor.fetchall()
    if res != []:
        if int(message.text) == res[0][1]:
            cursor.execute(f"UPDATE users SET email = '{res[0][2]}' WHERE id = {message.from_user.id};")
            cursor.execute(f'UPDATE users SET balance = balance + 1000 WHERE id = {message.from_user.id};')
            cursor.connection.commit()
            await message.answer("Все данные верны и на ваш баланс зачислено 1000$")
        else:
            await message.reply("Неправильный код")
    else:
        await message.reply("Попробуйте еще раз")
    await state.finish()

@dp.message_handler(commands=['profile'])
async def get_profile(message:types.Message):
    cursor = db.cursor()
    cursor.execute(f'SELECT balance FROM users WHERE id = {message.from_user.id};')
    balance = cursor.fetchall()
    await message.answer(f"""{message.from_user.username}, ваш профиль:\n
♟{message.from_user.first_name}, {message.from_user.last_name}\n    
🔎 ID {message.from_user.id}\n
💰Balance: {balance[0][0]} $ \n
💳 В банке: 0 $\n
💽 Биткоинов: 0 B
""")

executor.start_polling(dp)