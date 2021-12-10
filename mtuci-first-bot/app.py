import telebot
from random import randint
from telebot import types

token = '<TOKEN>'

bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def start(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Хочу", "/help")
    bot.send_message(
        message.chat.id, 'Привет! Хочешь узнать свежую информацию о МТУСИ?', reply_markup=keyboard)


@bot.message_handler(commands=['random'])
def random(message):
    bot.send_message(message.chat.id, str(randint(0, 100)))


@bot.message_handler(commands=['sayhi'])
def sayhi(message):
    bot.send_message(message.chat.id, 'Hi ' +
                     str(message.from_user.first_name))


@bot.message_handler(commands=['saygoodbye'])
def saygb(message):
    bot.send_message(message.chat.id, 'Bye ' +
                     str(message.from_user.first_name))


@bot.message_handler(commands=['help'])
def start_message(message):
    keyboard = types.ReplyKeyboardMarkup()
    keyboard.row("Хочу", "/help", "/random", "/sayhi", "/saygoodbye")
    bot.send_message(message.chat.id, 'Вот список моих команд',
                     reply_markup=keyboard)


@bot.message_handler(content_types=['text'])
def answer(message):
    if(message.text.lower() == "хочу"):
        bot.send_message(message.chat.id, 'Тогда тебе сюда - https://mtuci.ru')
    elif(message.text.lower() == token):
        bot.send_message(message.chat.id, 'Ты где это взял? Убери')
    elif(message.text.lower() == 'Кто твой создатель?'):
        bot.send_message(
            message.chat.id, 'Студент БВТ2107 Кирносов Егор Романович')
    else:
        bot.send_message(
            message.chat.id, 'Я тебя не понял, напиши что-то другое')


bot.polling(none_stop=True)
