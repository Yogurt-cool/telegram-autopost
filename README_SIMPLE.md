# 📸 Telegram Auto-Poster (Упрощенная версия)

Автоматическая публикация 5 случайных фото в Telegram канал каждый день.

**Упрощенная версия** - не требует API ID/Hash, работает только с Bot Token.

## 🚀 Быстрый старт

### Шаг 1: Подготовка фото

Положите все ваши фото (4000 штук) в папку `photos/`:

```bash
mkdir photos
# Скопируйте сюда все ваши фото
```

### Шаг 2: Загрузка фото в Telegram

Загрузите фото в канал-хранилище и сохраните file_id:

```bash
export TELEGRAM_BOT_TOKEN="8637424725:AAGp2aGn4wwTsdKe5MgBxSsC4i2yJSlL4mQ"
export STORAGE_CHANNEL_ID="-1003872286966"

python upload_photos.py --dir ./photos
```

Это займет время (4000 фото ≈ 30-60 минут с задержками).

Скрипт создаст файл `photo_file_ids.json` со всеми file_id.

### Шаг 3: Тестовая публикация

```bash
export TELEGRAM_BOT_TOKEN="8637424725:AAGp2aGn4wwTsdKe5MgBxSsC4i2yJSlL4mQ"
export PUBLIC_CHANNEL_ID="-1003748668450"

python telegram_poster_simple.py
```

Должно опубликовать 5 случайных фото в публичный канал.

### Шаг 4: GitHub Actions

1. Создайте репозиторий на GitHub
2. Добавьте файлы проекта
3. Добавьте в GitHub Secrets:
   - `TELEGRAM_BOT_TOKEN`
4. Обновите workflow чтобы использовать `telegram_poster_simple.py`

## 📁 Файлы

- `upload_photos.py` - загрузка фото в канал и сохранение file_id
- `telegram_poster_simple.py` - основной скрипт автопостинга
- `photo_file_ids.json` - база file_id (создается автоматически)
- `used_photos.json` - лог использованных фото (создается автоматически)

## 🔄 Как это работает

```
1. upload_photos.py
   └─> Загружает фото в приватный канал
   └─> Сохраняет file_id в photo_file_ids.json

2. telegram_poster_simple.py (каждый день)
   └─> Читает photo_file_ids.json
   └─> Выбирает 5 случайных неиспользованных
   └─> Публикует в публичный канал
   └─> Отмечает в used_photos.json
```

## 📊 Статистика

```bash
# Сколько фото в базе
cat photo_file_ids.json | jq '.photos | length'

# Сколько использовано
cat used_photos.json | jq '.used_file_ids | length'

# Сколько постов
cat used_photos.json | jq '.posts | length'
```

## ⚙️ Настройки

Переменные окружения:

- `TELEGRAM_BOT_TOKEN` - токен бота (обязательно)
- `STORAGE_CHANNEL_ID` - ID канала-хранилища (для upload_photos.py)
- `PUBLIC_CHANNEL_ID` - ID публичного канала (для telegram_poster_simple.py)
- `PHOTOS_PER_POST` - количество фото в посте (по умолчанию 5)

## 🆚 Сравнение версий

| Функция | Простая версия | Полная версия (Telethon) |
|---------|----------------|--------------------------|
| Требует API ID/Hash | ❌ Нет | ✅ Да |
| Загрузка фото | Вручную через скрипт | Автоматически из канала |
| Сложность настройки | Простая | Средняя |
| Зависимости | python-telegram-bot | + telethon |

## 🔧 Troubleshooting

### Ошибка "No photos in database"
Сначала запустите `upload_photos.py` для загрузки фото.

### Rate limit при загрузке
Скрипт автоматически ждет 60 секунд при rate limit. Просто подождите.

### Все фото использованы
Загрузите новые фото через `upload_photos.py` или очистите `used_photos.json`.

## 📝 TODO

- [ ] Загрузить 4000 фото через upload_photos.py
- [ ] Протестировать telegram_poster_simple.py локально
- [ ] Создать GitHub репозиторий
- [ ] Настроить GitHub Actions
- [ ] Добавить TELEGRAM_BOT_TOKEN в Secrets
