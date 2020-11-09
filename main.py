import cv2
import telebot
import requests
import json
import os
import numpy as np
from random import randint
from PIL import ImageFont, ImageDraw, Image
token = 'token'
bot = telebot.TeleBot(token=token)


@bot.message_handler(commands=['start'])
def command_start(message):
    bot.send_message(message.chat.id, "all ok")


@bot.message_handler(commands=['add'])
def command_add(message):
    path = "./Sentences.json"
    with open(path, "r") as file_read:
        data = json.load(file_read)
    text = message.text[5:]
    for i in data['sentences']:
        if i == text:
            return bot.send_message(message.chat.id, 'Такое уже есть, давай оригинальней)')
    data['sentences'].append(text)
    with open(path, "w") as file_write:
        json.dump(data, file_write, sort_keys=True)
    return bot.reply_to(message, 'Пожалуй, я это буду использовать')


@bot.message_handler(content_types=["photo"])
def handle_reply_photo(message):
    bot.send_chat_action(message.chat.id, "typing")
    name = '{}.jpg'.format(message.chat.id)
    path = './' + name
    try:
        raw = message.photo[0].file_id
        file_info = bot.get_file(raw)
        request = 'https://api.telegram.org/file/bot{0}/{1}'.format(token, file_info.file_path)
        response = requests.get(request)

        with open(name, 'wb') as code:
            code.write(response.content)
    except Exception as e:
        bot.reply_to(message, e)
    try:
        face_cascade_db = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

        img = cv2.imread(path)
        # (h, w, d) = img.shape
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        faces = face_cascade_db.detectMultiScale(img_gray, 1.1, 30)
        for (x, y, w, h) in faces:
            cv2.rectangle(img, (x, y), (x + w, y + w), (255, 250, 0), 2)
            fontpath = "./MyriadPro-BoldCond.ttf"
            font = ImageFont.truetype(fontpath, 32)
            img_pil = Image.fromarray(img)
            draw = ImageDraw.Draw(img_pil)
            draw.text((x - 10, y - 40), random_text(), font=font, fill=(30, 105, 210, 100))
            img = np.array(img_pil)
        cv2.imwrite(name, img)
        with open(path, 'rb') as f:
            bot.send_photo(message.chat.id, photo=f, timeout=50).photo
        path = os.path.join('./', name)
        os.remove(path)
        print("%s has been removed successfully" % path)
    except Exception as e:
        print(e)

        
def random_text():
    with open("./Sentences.json", "r") as read_file:
        data = json.load(read_file)
    return data['sentences'][randint(0, len(data['sentences'])-1)]


if __name__ == '__main__':
    bot.polling(none_stop=True)
