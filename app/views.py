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
            
            if callback_text(callback_query) == "menu_add/":
                callback_menu_add(callback_query)
            
            elif callback_text(callback_query) == "menu_add_abort/":
                message_id = callback_query.message.message_id
                bot.delete_message(chat_id, message_id)
            
            elif callback_text(callback_query) == "menu/":
                callback_menu(callback_query)

            elif callback_text(callback_query) == "menu_play/":
                callback_menu_play(callback_query)

            elif callback_text(callback_query) == "menu_record/":
                callback_menu_record(callback_query)

            elif callback_text(callback_query) == "menu_add_group_up/":
                callback_menu_add_group_up(callback_query)

            elif callback_text(callback_query) == "menu_get_group_up/":
                callback_menu_get_group_up(callback_query)   

            elif callback_text(callback_query) == "menu_get/":
                callback_menu_get(callback_query)     
        
    return JsonResponse({'status': 'ok'})


#############################################################

def rout_start(message):
    chat_id = message.chat.id
    message_id = message.message_id

    new_chat = Chats(
        chat_id=chat_id,
        last_callback = "none/",
        last_id = "none/"
    )
    new_chat.save()

    text = " Главное  Меню "
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

    user = Chats.objects.get(chat_id=chat_id)
    if user.last_callback == "menu_record/":
        last_id = user.last_id

        user.last_id = "none/"
        user.last_callback = "none/"
        user.save()

        file_id = message.json["voice"]["file_id"]
        mp3_id = mp3_convert(file_id)
        text = "ваша история отправлена в модерацию"
        keyboard = MAIN_MENU
        message_send(text=text, keyboard=keyboard, chat_id=chat_id)
        last_id = str(int(message_id) - 1)
        bot.delete_message(chat_id, last_id)

    return

def rout_audio(message):
    tg_id = message.json["audio"]["file_id"]
    name = message.json["audio"]["file_name"]
    chat_id = message.chat.id
    message_id = message.message_id
    chat_id = message.chat.id
    message_id = message.message_id

    user = Chats.objects.get(chat_id=chat_id)
    callback = user.last_callback
    last_id = user.last_id
    user.last_callback = "none/"
    user.last_id = "none/"
    user.save()

    string = callback.split("/")
    callback_text = string[0] + "/"

    if callback_text == "menu_add/" and auth(chat_id):
        numbers_list = re.findall(r'\d+', callback)
        janra_id = ''.join(numbers_list)
        janra = Janras.objects.get(id=janra_id)
        new_story = Storys(
            janra = janra,
            name = name,
            tg_id = tg_id,
            moderator_id = chat_id
        )
        new_story.save()
        text = "История успешно загружена!"
        bot.send_message(chat_id, text)
        bot.delete_message(chat_id, message_id)

    else:
        bot.delete_message(chat_id, message_id)
        
    return


#############################################################
def callback_menu_add(callback_query):
    janra_id = callback_number(callback_query)
    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    callback = callback_query.data

    # bot.delete_message(chat_id, message_id)
    try:
        janra = Janras.objects.get(id=janra_id)
        user = Chats.objects.get(chat_id=chat_id)
        user.last_callback = callback
        user.last_id = chat_id
        user.save()

        text = "Отлично! Теперь отправьте мне озвученную историю!"
    except:
        text = "Ошибка! Жанр был удален, попробуйте еще раз ввести команду /add"
    bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id)
    return

def callback_menu(callback_query):
    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    text = "Главное  Меню"
    keyboard = MAIN_MENU
    message_send(chat_id=chat_id, text=text, keyboard=keyboard)
    bot.delete_message(chat_id, message_id)

def callback_menu_play(callback_query):
    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id

    if Janras.objects.count() > 0:
        text = "Какой жанр истории хотите послушать?"
        group_number = "1"
        keyboard = keyboard_get(group_number)
        message_send(chat_id=chat_id, keyboard=keyboard, text=text)
    
    else:
        text = "Жанров еще нет :("
        message_send(chat_id=chat_id, text=text, keyboard=MENU_BUTTON)

    bot.delete_message(chat_id, message_id)
    return

def callback_menu_get_group_up(callback_query):
    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    group_number = callback_number(callback_query)
    keyboard = keyboard_get(group_number)
    text = "Какой жанр истории хотите выбрать?"
    message_edit(chat_id=chat_id, text=text, keyboard=keyboard, message_id=message_id)
    return

def callback_menu_add_group_up(callback_query):
    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    group_number = int(callback_number(callback_query))
    keyboard = keyboard_add(group_number)
    text = "Какой жанр истории хотите загрузить?"
    message_edit(chat_id=chat_id, text=text, keyboard=keyboard, message_id=message_id)
    return

def callback_menu_get(callback_query):
    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id
    janra_id = int(callback_number(callback_query))
    janra = Janras.objects.get(id=janra_id)
    storys = Storys.objects.filter(janra=janra)
    if storys.exists():
        random_story = random.choice(storys)
        audio_id = random_story.tg_id
        caption = "Вот ваша история!"
        keyboard = MAIN_MENU
        text = " Главное  Меню"
        bot.send_audio(chat_id, audio_id, caption)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
        message_send(chat_id=chat_id, keyboard=keyboard, text=text)
    else:
        text="Историй этого жанра еще не добавили :("
        keyboard = MENU_BUTTON
        message_send(chat_id=chat_id, text=text, keyboard=keyboard)
        bot.delete_message(chat_id=chat_id, message_id=message_id)
    return

def callback_menu_record(callback_query):
    message_id = callback_query.message.message_id
    chat_id = callback_query.message.chat.id

    user = Chats.objects.get(chat_id=chat_id)
    user.last_callback = callback_query.data
    user.last_id = message_id
    user.save()

    text= "Пришлите мне вашу историю голосовым сообщением"
    bot.send_message(chat_id, text)
    bot.delete_message(chat_id, message_id)  
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
    callback = callback_query.data
    string = callback.split("/")
    text = string[0] + "/"
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
    print(group_number, element_count, first_element_number, amount)

    if amount <= 0:#last group
        for element in all_elements:
            if count >= first_element_number:
                janra = element
                janra_id = janra.id
                janra_name = janra.name
                array_element = [{'text': janra_name, 'callback_data': f'menu_add/{janra_id}'}]
                array.append(array_element)
            count += 1 

        navigation = [
            {'text': "Отмена", 'callback_data': f'menu_add_abort/'}
        ]       
    else:#not last group
        for element in all_elements:
            last_element_counter = (6*group_number)+1
            if count >= first_element_number:
                if count < last_element_counter:
                    janra = element
                    janra_id = janra.id
                    janra_name = janra.name
                    array_element = [{'text': janra_name, 'callback_data': f'menu_add/{janra_id}'}]
                    array.append(array_element)
            count += 1
        next_group = group_number + 1
        navigation = [
            {'text': "Отмена", 'callback_data': f'menu_add_abort/'},
            {'text': "Еще жанры", 'callback_data': f'menu_add_group_up/{next_group}'}
        ]

    array.append(navigation)
    keyboard = {
        "inline_keyboard" :  array
    }   
    return keyboard

def keyboard_get(group_number):
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
                array_element = [{'text': janra_name, 'callback_data': f'menu_get/{janra_id}'}]
                array.append(array_element)
            count += 1 

        if group_number > 1:
            back_group = group_number - 1
            back = f"menu_get_group_up/{back_group}"
        else:
            back = "menu/"
        navigation = [
            {'text': "Назад", 'callback_data': back }
        ]
  
    else:#not last group
        for element in all_elements:
            last_element_counter = (6*group_number)+1
            if count >= first_element_number:
                if count < last_element_counter:
                    janra = element
                    janra_id = janra.id
                    janra_name = janra.name
                    array_element = [{'text': janra_name, 'callback_data': f'menu_get/{janra_id}'}]
                    array.append(array_element)
            count += 1
        next_group = group_number + 1

        if group_number > 1:
            back_group = group_number - 1
            back = f"menu_get_group_up/{back_group}"
        else:
            back = "menu/"
        navigation = [
            {'text': "Назад", 'callback_data': back },
            {'text': "Еще жанры", 'callback_data': f'menu_get_group_up/{next_group}'}
        ]

    array.append(navigation)
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

def message_edit(chat_id, message_id, text, keyboard):
    data = { 
        "chat_id": chat_id,
        "text": text,
        "message_id" : message_id,
        "reply_markup" : json.dumps(keyboard)
    }
    response = requests.post(f"https://api.telegram.org/bot{TOKEN_SH_DEV_BOT}/editMessageText", data)
    return response