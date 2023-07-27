from django.shortcuts import render
import random
import re
import json
from django.shortcuts import redirect
from rest_framework.views import APIView
from django.http import HttpResponse
from .models import Moderators
from .models import Chats
from .models import Storys
from .models import Janras
import requests
from project.const import TOKEN_SH_DEV_BOT
from project.const import FREELANCE_GROUP_ID
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views import View
import telebot
from telebot.types import Update

MENU_BUTTON = {
        "inline_keyboard" :  [
            [
                {'text': 'Меню', 'callback_data': 'menu/'}
            ]
        ]
    }

MAIN_MENU = {
    "inline_keyboard" :  [
        [
            {'text': 'Прослушать историю', 'callback_data': 'menu_play/'}
        ],
        [
            {'text': 'Записать историю', 'callback_data': 'menu_record/'}
        ]
    ]
}




bot = telebot.TeleBot(TOKEN_SH_DEV_BOT)
@csrf_exempt
def webhook(request):
    if request.method == 'POST':
        update = update_parser(request)
        format = format_message(update)

        if format == "callback":
            callback_query = update.callback_query
            chat_id = callback_query.from_user.id
            # message_id = callback_query.message.message_id
        else:
            message = update.message
            chat_id = message.chat.id
            
        if str(chat_id) == FREELANCE_GROUP_ID:
            return JsonResponse({'status': 'ok'})
#############################################################
        if format == "text":
            if message.text == "/start":
                rout_start(message)

            elif message.text == "/chat_id":
                rout_chat_id(message)

            elif message.text == "/add":   #MODERATOR
                rout_add(message)

        elif format == "voice":
            rout_voice(message)

        elif format == "audio":   #MODERATOR
            rout_audio(message)
        
        elif format == "callback":
            pass

    return JsonResponse({'status': 'ok'})

#############################################################

def rout_start(message):
    chat_id = message.chat.id
    message_id = message.message_id

    new_chat = Chats(
        chat_id=chat_id,
        last_callback = "none",
        last_id = "none"
    )
    new_chat.save()

    text = "[какой-то текст приветствия]"
    keyboard = MAIN_MENU
    message_send(text=text, keyboard=keyboard, chat_id=chat_id)
    return

def rout_chat_id(message):
    chat_id = message.chat.id
    message_id = message.message_id

    text = f"Ваш телеграм id: {chat_id}"
    keyboard = MENU_BUTTON
    message_send(text=text, keyboard=keyboard, chat_id=chat_id)
    bot.delete_message(chat_id, message_id)
    return

def rout_add(message):
    chat_id = message.chat.id
    message_id = message.message_id

    if auth(chat_id):
        if Janras.objects.count() > 0:
            text = "Какой жанр истории хотите загрузить?"
            group_number = "1"
            keyboard = keyboard_add(group_number)
            message_send(chat_id=chat_id, keyboard=keyboard, text=text)
        
        else:
            text = "Жанры историй еще не добавлены"
            bot.send_message(chat_id, text)

    bot.delete_message(chat_id, message_id)
    return

def rout_voice(message):
    chat_id = message.chat.id
    message_id = message.message_id
    return

def rout_audio(message):
    chat_id = message.chat.id
    message_id = message.message_id
    return





#############################################################
def update_parser(request):
    json_str = request.body.decode('UTF-8')
    update = Update.de_json(json_str)
    print(update)
    return update

def format_message(update):

    status = True
    type_message = "None"

    if status:
        if str(update.callback_query) != "None" and status:
            type_message = "callback"
            status = False 
    if status:
        if str(update.message.content_type) == "text":
            type_message = "text"
            status = False

    if status:
        if str(update.message.content_type) == "voice":
            type_message = "voice"
            status = False
    if status:
        if str(update.message.content_type) == "photo":
            type_message = "photo"
            status = False
    if status:
        if str(update.message.content_type) == "audio":
            type_message = "audio"
            status = False
    if status:
        if str(update.message.content_type) == "video_note":
            type_message = "video_note"
            status = False
    if status:
        if str(update.message.content_type) == "video":
            type_message = "video"
            status = False
    if status:
        if str(update.message.content_type) == "document":
            type_message = "document"
            status = False

 
    print(type_message)###<<<###
    return type_message

def callback_text(callback_query):
    string = callback_query.split("/")
    text = string["0"]
    return text

def callback_number(callback_query):
    numbers_list = re.findall(r'\d+', callback_query.data)
    number = ''.join(numbers_list)
    return number   

def mp3_convert(file_id):
    # Download and save the file
    payload = {'file_id': file_id}
    url = f"https://api.telegram.org/bot{TOKEN_SH_DEV_BOT}/getFile"
    response = requests.get(url, params=payload)
    data = response.json()

    file_path = data['result']['file_path']
    file_url = f"https://api.telegram.org/file/bot{TOKEN_SH_DEV_BOT}/{file_path}"

    response = requests.get(file_url)
    with open("story.mp3", 'wb') as f:
        f.write(response.content)  

    #UPLOAD
    with open("story.mp3", 'rb') as file:
        response = bot.send_document(FREELANCE_GROUP_ID, file)
    mp3_id = response.audio.file_id
    return mp3_id

def auth(chat_id):
    status = False
    try:
        moderator = Moderators.objects.get(chat_id=chat_id)
        status = True
    except:
        pass
    return status    

def keyboard_add(group_number):
    group_number = int(group_number)
    all_elements = Janras.objects.all()
    element_count = int(len(all_elements))
    first_element_number = (6*(group_number - 1)) + 1
    amount = element_count - ( 6*group_number )
    count = 1
    array = []


    if amount <= 0:#last group
        for element in all_elements:
            if count >= first_element_number:
                janra = element
                janra_id = janra.id
                janra_name = janra.name
                array_element = [{'text': janra_name, 'callback_data': f'menu_add/{janra_id}'}]
                array.append(array_element)
            count =+ 1        
        
    else:#not last group
        for element in all_elements:
            last_element_counter = 7
            if count >= first_element_number:
                if count < last_element_counter:
                    janra = element
                    janra_id = janra.id
                    janra_name = janra.name
                    array_element = [{'text': janra_name, 'callback_data': f'menu_add/{janra_id}'}]
                    array.append(array_element)
            count =+ 1

    keyboard = {
        "inline_keyboard" :  array
    }   
    return keyboard


#######################
def message_send(chat_id, text, keyboard):
    data = { 
        "chat_id": chat_id,
        "text": text,
        "reply_markup" : json.dumps(keyboard)
    }
    response = requests.post(f"https://api.telegram.org/bot{TOKEN_SH_DEV_BOT}/sendMessage", data)
    return response

def audio_send(chat_id, text, keyboard, audio_id):
    url = f'https://api.telegram.org/bot{TOKEN_SH_DEV_BOT}/sendAudio'
    data = {
        'chat_id': chat_id, 
        'caption': text, 
        'audio': audio_id,
        "reply_markup" : json.dumps(keyboard)
    }

    response = requests.post(url, data=data)
    return response

