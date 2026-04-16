#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Upload photos to Telegram storage channel
Загрузка фото в канал-хранилище и сохранение file_id
"""

import os
import sys
import json
import asyncio
from pathlib import Path
from telegram import Bot
from telegram.error import TelegramError

# Фикс кодировки для Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Настройки
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
STORAGE_CHANNEL_ID = int(os.getenv('STORAGE_CHANNEL_ID', '-1003872286966'))
PHOTOS_DIR = os.getenv('PHOTOS_DIR', './photos')
FILE_IDS_JSON = 'photo_file_ids.json'

def load_file_ids():
    """Загрузить сохраненные file_id"""
    if os.path.exists(FILE_IDS_JSON):
        with open(FILE_IDS_JSON, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {'photos': []}

def save_file_ids(data):
    """Сохранить file_id"""
    with open(FILE_IDS_JSON, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

async def upload_photos(photos_dir):
    """Загрузить все фото из папки в канал"""

    print("="*60)
    print("📤 ЗАГРУЗКА ФОТО В TELEGRAM")
    print("="*60)

    if not BOT_TOKEN:
        print("❌ Ошибка: TELEGRAM_BOT_TOKEN не установлен")
        return False

    # Проверить папку
    photos_path = Path(photos_dir)
    if not photos_path.exists():
        print(f"❌ Папка не найдена: {photos_dir}")
        return False

    # Получить список фото
    photo_extensions = ['.jpg', '.jpeg', '.png', '.webp']
    photo_files = set()  # Используем set чтобы избежать дубликатов

    for ext in photo_extensions:
        photo_files.update(photos_path.glob(f'*{ext}'))
        photo_files.update(photos_path.glob(f'*{ext.upper()}'))

    photo_files = sorted(list(photo_files))

    print(f"📁 Папка: {photos_dir}")
    print(f"📸 Найдено фото: {len(photo_files)}")

    if not photo_files:
        print("❌ Нет фото для загрузки")
        return False

    # Загрузить существующие file_id
    data = load_file_ids()
    uploaded_names = {p['filename'] for p in data['photos']}

    # Фильтровать уже загруженные
    photos_to_upload = [p for p in photo_files if p.name not in uploaded_names]

    print(f"✅ Уже загружено: {len(uploaded_names)}")
    print(f"📤 К загрузке: {len(photos_to_upload)}")

    if not photos_to_upload:
        print("✅ Все фото уже загружены!")
        return True

    # Создать бота
    bot = Bot(token=BOT_TOKEN)

    try:
        me = await bot.get_me()
        print(f"🤖 Бот: @{me.username}")
        print(f"📢 Канал: {STORAGE_CHANNEL_ID}")
        print("="*60)

        # Загрузить фото
        uploaded_count = 0
        failed_count = 0

        for i, photo_path in enumerate(photos_to_upload, 1):
            print(f"\n[{i}/{len(photos_to_upload)}] 📤 {photo_path.name}")

            try:
                # Отправить фото
                with open(photo_path, 'rb') as photo_file:
                    message = await bot.send_photo(
                        chat_id=STORAGE_CHANNEL_ID,
                        photo=photo_file
                    )

                # Сохранить file_id
                file_id = message.photo[-1].file_id  # Самое большое фото

                data['photos'].append({
                    'filename': photo_path.name,
                    'file_id': file_id,
                    'message_id': message.message_id,
                    'file_size': photo_path.stat().st_size
                })

                uploaded_count += 1
                print(f"  ✅ Загружено (file_id: {file_id[:20]}...)")

                # Сохранять каждые 10 фото
                if uploaded_count % 10 == 0:
                    save_file_ids(data)
                    print(f"  💾 Сохранено {uploaded_count} file_id")

                # Небольшая задержка чтобы не словить rate limit
                await asyncio.sleep(1.5)  # Увеличено до 1.5 сек

            except TelegramError as e:
                print(f"  ❌ Ошибка: {e}")
                failed_count += 1

                # Если rate limit - подождать
                if "Flood control" in str(e) or "Too Many Requests" in str(e):
                    # Извлечь время ожидания из ошибки
                    import re
                    match = re.search(r'Retry in (\d+)', str(e))
                    if match:
                        wait_time = int(match.group(1)) + 5  # +5 сек для надежности
                    else:
                        wait_time = 60

                    print(f"  ⏳ Flood control, ожидание {wait_time} сек...")
                    await asyncio.sleep(wait_time)

                    # Повторить попытку
                    try:
                        with open(photo_path, 'rb') as photo_file:
                            message = await bot.send_photo(
                                chat_id=STORAGE_CHANNEL_ID,
                                photo=photo_file
                            )

                        file_id = message.photo[-1].file_id
                        data['photos'].append({
                            'filename': photo_path.name,
                            'file_id': file_id,
                            'message_id': message.message_id,
                            'file_size': photo_path.stat().st_size
                        })

                        uploaded_count += 1
                        failed_count -= 1  # Убираем из failed
                        print(f"  ✅ Загружено после повтора")

                    except Exception as retry_error:
                        print(f"  ❌ Повтор не удался: {retry_error}")

        # Финальное сохранение
        save_file_ids(data)

        print(f"\n{'='*60}")
        print("📊 ИТОГИ ЗАГРУЗКИ")
        print(f"{'='*60}")
        print(f"✅ Успешно: {uploaded_count}")
        print(f"❌ Ошибок: {failed_count}")
        print(f"📁 Всего в базе: {len(data['photos'])} фото")
        print(f"💾 Сохранено в: {FILE_IDS_JSON}")
        print(f"{'='*60}")

        return True

    except Exception as e:
        print(f"\n❌ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Upload photos to Telegram storage')
    parser.add_argument('--dir', default=PHOTOS_DIR, help='Directory with photos')

    args = parser.parse_args()

    success = asyncio.run(upload_photos(args.dir))
    sys.exit(0 if success else 1)
