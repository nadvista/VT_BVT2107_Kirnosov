from ast import Str
from typing import List
import psycopg2
import telebot
import datetime
from typing import Dict
from telebot import types

conn = psycopg2.connect(database="bot_db",
                        user="postgres",
                        password="qwerty",
                        host="localhost",
                        port="5432")
cursor = conn.cursor()
token = '<enter your token here>'
bot = telebot.TeleBot(token)

unregistered_users: Dict[int, List[str]] = {}
unregistered_is_teacher: Dict[int, bool] = {}

@bot.message_handler(commands=['week'])
def week(message):
    bot.send_message(message.chat.id, text = 'Сейчас {} неделя'.format(get_week()))
@bot.message_handler(commands=['mtuci'])
def mtuci(message):
    bot.send_message(message.chat.id, text = 'Оффициальный сайт МТУСИ - https://mtuci.ru/')
@bot.message_handler(commands=['register_student'])
def register_student(message):
    current = get_user_byid(message.from_user.id)
    if (len(current) > 0):
        bot.send_message(message.chat.id, text='Вы уже зарегестрированы как {}'.format(current[0][1]))
        return
    unregistered_is_teacher[message.from_user.id] = False
    bot.send_message(message.chat.id, text='Введите свое имя', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_name)
@bot.message_handler(commands=['register_teacher'])
def register_teacher(message):
    current = get_user_byid(message.from_user.id)
    if (len(current) > 0):
        bot.send_message(message.chat.id, text='Вы уже зарегестрированы как {}'.format(current[0][1]))
        return
    unregistered_is_teacher[message.from_user.id] = True
    bot.send_message(message.chat.id, text='Введите свое имя', reply_markup=types.ReplyKeyboardRemove())
    bot.register_next_step_handler(message, get_name)
@bot.message_handler(commands = ['help'])
@bot.message_handler(commands=['start'])
@bot.message_handler(content_types=['new_chat_members'])
def greeting(message):
    user = get_user_byid(message.from_user.id)
    if (len(user) == 0):
        keyboard = types.ReplyKeyboardMarkup()
        keyboard.row("/register_student", "/register_teacher")
        bot.send_message(message.chat.id, text='Здравствуйте! Для работы с ботом вам необходимо зарегестрироваться.\n Если вы являетесь студентом - воспользуйтесь командой /register_student.\nЕсли вы являетесь преподавателем - воспользуйтесь командой /register_teacher', reply_markup=keyboard)
    else:
        commands = get_user_commands(user[0])
        commands_arr = get_user_commands_as_array(user[0])
        keyboard = types.ReplyKeyboardMarkup()
        for com in commands_arr:
            keyboard.add(com)
        bot.send_message(message.chat.id, text='Здравствуйте, {0}\nВам доступны следующие команды:\n{1}'.format(user[0][1],commands),reply_markup=keyboard)
@bot.message_handler(content_types=['text'])
def answer(message):
    user = get_user_byid(message.from_user.id)
    if(len(user) == 0):
        bot.send_message(message.chat.id, text = 'Вы не авторизованы')
        return
    user = user[0]
    answer = ''
    
    if (is_week_name(message.text)):
        bot.send_message(message.chat.id,text = get_day_rasp(message.text,user[2],False,False))
        return
    elif (message.text == 'Расписание на текущую неделю' or message.text == 'Расписание на следующую неделю'):
        week = get_week() + 0 if message.text == 'Расписание на текущую неделю' else 1
        ans = ''
        for num in range(1,7):
            day_name = get_day_by_num(num)
            
            ans += '-------{}-------\n'.format(day_name)
            ans += get_day_rasp(day_name,user[2],week//2 == 0,True)
        bot.send_message(message.chat.id,text = ans)

    else:
        bot.send_message(message.chat.id, text = 'Извините, я Вас не понял')
    pass
def get_name(message):
    unregistered_users[message.from_user.id] = []
    unregistered_users[message.from_user.id].append(message.text)
    if (unregistered_is_teacher[message.from_user.id]):
        unregistered_users[message.from_user.id].append('teacher')
        user = unregistered_users[message.from_user.id]
        add_user(user[0],user[1],message.from_user.id,True,message.chat.id)
    else:
        bot.send_message(message.chat.id, text='Введите свою группу транслитом.')
        bot.register_next_step_handler(message, get_group)
def get_group(message):
    is_teacher = unregistered_is_teacher[message.from_user.id]
    if (not is_teacher):
        unregistered_users[message.from_user.id].append(message.text.lower())
    user = unregistered_users[message.from_user.id]
    add_user(user[0],user[1],message.from_user.id,False,message.chat.id)
def get_user_byid(id):
    cursor.execute("SELECT * FROM bot.users WHERE tg_id = %s",(str(id),))
    user = list(cursor.fetchall())
    return user
def add_user(name,group,tg_id,is_teacher,chat_id):
    cursor.execute("INSERT INTO bot.users (full_name, group_name, role_name,tg_id) VALUES (%s,%s,%s,%s)", (str(name), str(group).lower(), str('verify' if is_teacher else 'student'), str(tg_id)))
    conn.commit()
    bot.send_message(chat_id, text = 'Вы успешно зарегестрировались.')
    if(is_teacher):
        bot.send_message(chat_id, text = 'Сейчас ваш аккаунт проверяется.')
def get_user_commands(user):
    user_role = user[3]
    answer = ''
    if (user_role == 'teacher'):
        answer += '/add_homework - добавить ДЗ\n/verify_teacher - '
    answer += '/start\n/mtuci\n/help\nПонедельник\nВторник\nСреда\nЧетверг\nПятница\nСуббота\nРасписание на текущую неделю\nРасписание на следующую неделю'
    return answer
def get_user_commands_as_array(user):
    user_role = user[3]
    answer = []
    if (user_role == 'teacher'):
        answer.append('/add_homework')
        answer.append('/verify_teacher')
    answer.append('/start')
    answer.append('/mtuci')
    answer.append('/help')
    answer.append('/week')
    answer.append('Понедельник')
    answer.append('Вторник')
    answer.append('Среда')
    answer.append('Четверг')
    answer.append('Пятница')
    answer.append('Суббота')
    answer.append('Расписание на текущую неделю')
    answer.append('Расписание на следующую неделю')
    return answer
def get_week():
    year = datetime.datetime.now().year
    firstSept = datetime.datetime(year,9,1).isocalendar().week
    currentWeek = datetime.datetime.now().isocalendar().week - firstSept+1
    return currentWeek
def get_day_rasp(day_str:str,group:str,week:bool,isp_weeks:bool):
    answer = ''
    day = ''
    if(day_str == 'Понедельник'):
        day='monday'
    elif(day_str == 'Вторник'):
        day='tuesday'
    elif(day_str == 'Среда'):
        day='wednesday'
    elif(day_str == 'Четверг'):
        day='thursday'
    elif(day_str == 'Пятница'):
        day='friday'
    elif(day_str == 'Суббота'):
        day='saturday'
    if (isp_weeks):
        cursor.execute("SELECT * FROM bot.timetable WHERE day=%s AND group_name=%s AND (type=%s or type = 'always') ORDER BY number",(day,group,'even' if week else 'odd'))
    else:
        cursor.execute("SELECT * FROM bot.timetable WHERE day=%s AND group_name=%s ORDER BY number",(day,group))
    records = list(cursor.fetchall())
    if(len(records) == 0):
        return 'СРС или не нейдено расписания на этот день для вашей группы.\n'
    for lesson in records:
        answer += '{0} пара - {1}, мигалка - {2}\n'.format(lesson[4],lesson[3], 'четн.' if lesson[5] == 'even' else 'всегда' if lesson[5] == 'always' else 'нечетн')
    return answer
def is_week_name(text:str):
    if(text == 'Понедельник'):
        return True
    elif(text == 'Вторник'):
        return True
    elif(text == 'Среда'):
        return True
    elif(text == 'Четверг'):
        return True
    elif(text == 'Пятница'):
        return True
    elif(text == 'Суббота'):
        return True
def get_day_by_num(num:int):
    if (num == 1): return 'Понедельник'
    elif (num == 2): return 'Вторник'
    elif (num == 3): return 'Среда'
    elif (num == 4): return 'Четверг'
    elif (num == 5): return 'Пятница'
    elif (num == 6): return 'Суббота'
bot.polling(none_stop=True)
