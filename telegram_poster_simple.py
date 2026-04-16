#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Telegram Auto-Poster (Simplified Version)
Автоматическая публикация 5 случайных фото используя сохраненные file_id
Не требует API ID/Hash - работает только с Bot Token
"""

import os
import sys
import json
import random
import asyncio
from datetime import datetime
from telegram import Bot, InputMediaPhoto
from telegram.error import TelegramError

# Фикс кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Настройки
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
PUBLIC_CHANNEL_ID = int(os.getenv('PUBLIC_CHANNEL_ID', '-1003748668450'))
PHOTOS_PER_POST = int(os.getenv('PHOTOS_PER_POST', '5'))
FILE_IDS_JSON = 'photo_file_ids.json'
USED_LOG_FILE = 'used_photos.json'

def load_file_ids():
    """Загрузить список file_id"""
    if os.path.exists(FILE_IDS_JSON):
        with open(FILE_IDS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'photos': []}

def load_used_photos():
    """Загрузить список использованных фото"""
    if os.path.exists(USED_LOG_FILE):
        with open(USED_LOG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'used_file_ids': [], 'posts': []}

def save_used_photos(log):
    """Сохранить список использованных фото"""
    with open(USED_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

def select_random_photos(count=5):
    """Выбрать случайные неиспользованные фото"""

    # Загрузить все file_id
    file_ids_data = load_file_ids()
    all_photos = file_ids_data.get('photos', [])

    if not all_photos:
        print("❌ Нет доступных фото в базе")
        print(f"💡 Сначала загрузите фото: python upload_photos.py --dir ./photos")
        return None

    # Загрузить использованные
    log = load_used_photos()
    used_ids = set(log['used_file_ids'])

    # Отфильтровать использованные
    available_photos = [p for p in all_photos if p['file_id'] not in used_ids]

    print(f"📊 Всего фото: {len(all_photos)}")
    print(f"✅ Использовано: {len(used_ids)}")
    print(f"📥 Доступно: {len(available_photos)}")

    if len(available_photos) < count:
        print(f"⚠️  Недостаточно фото! Доступно: {len(available_photos)}, нужно: {count}")
        if len(available_photos) == 0:
            print("❌ Все фото использованы!")
            return None
        count = len(available_photos)

    # Выбрать случайные
    selected = random.sample(available_photos, count)

    print(f"🎲 Выбрано {len(selected)} случайных фото")
    return selected

async def post_to_channel(bot, photos, caption=None):
    """Опубликовать фото в публичный канал"""

    if not photos:
        return None

    print(f"\n📤 Публикация {len(photos)} фото в канал {PUBLIC_CHANNEL_ID}...")

    try:
        # Подготовить медиа-группу
        media_group = []
        for i, photo in enumerate(photos):
            # Добавить подпись только к первому фото
            if i == 0 and caption:
                media_group.append(InputMediaPhoto(media=photo['file_id'], caption=caption))
            else:
                media_group.append(InputMediaPhoto(media=photo['file_id']))

        # Отправить медиа-группу
        messages = await bot.send_media_group(
            chat_id=PUBLIC_CHANNEL_ID,
            media=media_group
        )

        print(f"✅ Успешно опубликовано {len(messages)} фото")
        return messages

    except TelegramError as e:
        print(f"❌ Ошибка публикации: {e}")
        return None

async def main():
    """Основная функция"""

    print("="*60)
    print("📸 TELEGRAM AUTO-POSTER")
    print("="*60)
    print(f"🕐 Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Проверка токена
    if not BOT_TOKEN:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен")
        return False

    # Создать бота
    bot = Bot(token=BOT_TOKEN)

    try:
        # Проверить бота
        me = await bot.get_me()
        print(f"🤖 Бот: @{me.username}")

        # Выбрать случайные фото
        selected_photos = select_random_photos(PHOTOS_PER_POST)

        if not selected_photos:
            print("❌ Не удалось выбрать фото")
            return False

        # Опубликовать без подписи
        messages = await post_to_channel(bot, selected_photos, caption=None)

        if not messages:
            print("❌ Не удалось опубликовать")
            return False

        # Обновить лог
        log = load_used_photos()

        # Добавить использованные file_id
        for photo in selected_photos:
            log['used_file_ids'].append(photo['file_id'])

        # Добавить запись о посте
        log['posts'].append({
            'date': datetime.now().isoformat(),
            'photos_count': len(selected_photos),
            'filenames': [photo['filename'] for photo in selected_photos],
            'file_ids': [photo['file_id'] for photo in selected_photos],
            'post_url': f"https://t.me/c/{str(PUBLIC_CHANNEL_ID)[4:]}/{messages[0].message_id}"
        })

        save_used_photos(log)

        print(f"\n{'='*60}")
        print("✅ УСПЕШНО ОПУБЛИКОВАНО!")
        print(f"{'='*60}")
        print(f"📸 Фото: {len(selected_photos)}")
        print(f"📊 Всего использовано: {len(log['used_file_ids'])}")
        print(f"📝 Всего постов: {len(log['posts'])}")
        print(f"🔗 URL: {log['posts'][-1]['post_url']}")
        print(f"{'='*60}")

        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
