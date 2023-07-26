from django.db import models
from django.utils import timezone
from django.dispatch import receiver
from django.db.models.signals import post_save
from project.const import FREELANCE_GROUP_ID
from project.const import TOKEN_SH_DEV_BOT
import telebot
import requests

class Chats(models.Model):
    chat_id = models.CharField(
        verbose_name="Telegram chat id", 
        primary_key=True,
        max_length=56, 
        unique=True
    )

    last_callback = models.CharField(
        verbose_name="Последний callback",
        max_length=56,
        default="none"
    )

    last_id = models.CharField(
        verbose_name="Последний callback ID",
        max_length=56,
        default="none"
    )

    def __str__(self):
        return self.chat_id
    
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

class Janras(models.Model):
    janra = models.CharField(
        verbose_name="Название жанра", 
        max_length=56, 
    )  

    def __str__(self):
        return self.janra
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'

class Storys(models.Model):

    janra = models.ForeignKey(
        Janras,
        on_delete= models.CASCADE
    )

    name= models.CharField(
        verbose_name="Название", 
        max_length=56, 
        default="История без названия"
    )

    tg_id = models.CharField(
        verbose_name="ID в телеграмме", 
        max_length=256, 
    )

    time_date = models.DateTimeField(
        verbose_name='Время и дата создания',
        default=timezone.now
    )

    moderator_id = models.CharField(
        verbose_name="Автор озвучки", 
        max_length=56
    )

    def __str__(self):
        return self.name
    class Meta:
        verbose_name = 'История'
        verbose_name_plural = 'Истории'


class Moderators(models.Model):
    chat_id = models.CharField(
        verbose_name="Telegram chat id", 
        primary_key=True,
        max_length=56, 
        unique=True
    )

    name = models.CharField(
        verbose_name="ФИО модератора", 
        default="none",
        max_length=56, 
    )    

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = 'Модератор'
        verbose_name_plural = 'Модераторы'

