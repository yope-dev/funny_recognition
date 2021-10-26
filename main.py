from cv2 import CascadeClassifier as cv2_CascadeClassifier
from cv2 import imread as cv2_imread
from cv2 import cvtColor as cv2_cvtColor
from cv2 import COLOR_BGR2GRAY as cv2_COLOR_BGR2GRAY
from cv2 import rectangle as cv2_rectangle
from cv2 import imwrite as cv2_imwrite
from cv2 import data as cv2_data
from telebot import TeleBot as telebot_TeleBot
from requests import get as requests_get
from json import load as js_load
from json import dump as js_dump
from os import remove as os_remove
from numpy import array as np_array
from random import randint
import inspect
from PIL import ImageFont, ImageDraw, Image
token = '1442311253:AAF7zzwp1snLOU4-pQxUcxvYvGhbTFSQpLo'
bot = telebot_TeleBot(token=token)
fontpath = "./MyriadPro-BoldCond.ttf"
font = ImageFont.truetype(fontpath, 32)
sentences_path = "./Sentences.json"


def lineno():
    return inspect.currentframe().f_back.f_lineno


def get_data_from_file(file):
    data = ''
    with open(file, "r") as file_read:
        data = js_load(file_read)
    return data


@bot.message_handler(commands=['start'])
def command_start(message):
    bot.send_message(message.chat.id, "all ok")


@bot.message_handler(commands=['add'])
def command_add(message):
    data = get_data_from_file(sentences_path)
    text = message.text[5:]
    for i in data['sentences']:
        if i == text:
            return bot.send_message(message.chat.id, 'Такое уже есть, давай оригинальней)')
    data['sentences'].append(text)
    with open(sentences_path, "w") as file_write:
        js_dump(data, file_write, sort_keys=True)
    return bot.reply_to(message, 'Пожалуй, я это буду использовать')


@bot.message_handler(content_types=["photo"])
def handle_reply_photo(message):
    bot.send_chat_action(message.chat.id, "typing")
    name = f'{message.chat.id}.jpg'
    path = f'./{name}'
    name_photo = save_photo_by_telegramAPI(name, message)
    img = cv2_imread(name_photo)
    try:
        faces = find_faces(path)
        for (x, y, w, h) in faces:
            cv2_rectangle(img, (x, y), (x+w, y+h), (255, 250, 0), 2)
            img = draw_text_on_image(img, x, y)
        cv2_imwrite(name, img)
        with open(path, 'rb') as f:
            bot.send_photo(message.chat.id, photo=f, timeout=50).photo
        os_remove(path)
        print(f"{path} has been removed successfully")
    except Exception as e:
        print(f'{lineno()} {e}')


def save_photo_by_telegramAPI(name, message):
    try:
        raw = message.photo[-1].file_id
        file_info = bot.get_file(raw)
        request = f'https://api.telegram.org/file/bot{token}/{file_info.file_path}'
        response = requests_get(request)
        with open(name, 'wb') as code:
            code.write(response.content)
        return name
    except Exception as e:
        bot.reply_to(message, e)


def find_faces(path):
    face_cascade_db = cv2_CascadeClassifier(
        cv2_data.haarcascades + "haarcascade_frontalface_default.xml")
    img = cv2_imread(path)
    img_gray = cv2_cvtColor(img, cv2_COLOR_BGR2GRAY)
    return face_cascade_db.detectMultiScale(img_gray, 1.1, 30)


def draw_text_on_image(img, x, y):
    img_pil = Image.fromarray(img)
    draw = ImageDraw.Draw(img_pil)
    draw.text((x - 10, y - 40), random_text(),
              font=font, fill=(30, 105, 210, 100))
    img_with_text = np_array(img_pil)
    return img_with_text


def random_text():
    data = get_data_from_file(sentences_path)
    return data['sentences'][randint(0, len(data['sentences'])-1)]


if __name__ == '__main__':
    bot.polling(none_stop=True)
