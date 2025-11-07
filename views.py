import logging

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def some_function():
    logging.info('Функция some_function была вызвана')
    # Логика функции
from django.shortcuts import render

# Create your views here.

from django.shortcuts import render

def welcome(request):
    return render(request, 'library/welcome.html')
