import telebot
import requests
import re
import time

TOKEN = '8874070552:AAGECYQjxFyIG2c5dkX1UYt656_XpwoI4Ew'
bot = telebot.TeleBot(TOKEN)

# Регулярное выражение для проверки, что ссылка ведет именно на TikTok
TIKTOK_RE = re.compile(r'(https?://\S*(?:tiktok)\S*)')

@bot.message_handler(commands=['start'])
def start_message(message):
    bot.send_message(
        message.chat.id, 
        "👋 **Привет! Я твой личный бот для скачивания из TikTok!**\n\n"
        "Просто отправь мне ссылку на любое видео (обычную или короткую `vm.tiktok.com`), "
        "и я пришлю его тебе в максимальном качестве и **без водяного знака**! 🎬",
        parse_mode="Markdown"
    )

@bot.message_handler(content_types=['text'])
def handle_text(message):
    url_match = TIKTOK_RE.search(message.text)
    
    if not url_match:
        bot.send_message(message.chat.id, "❌ Пожалуйста, отправь мне корректную ссылку на видео TikTok.")
        return

    tiktok_url = url_match.group(1)
    status_msg = bot.send_message(message.chat.id, "⏳ *Пожалуйста, подождите... Очищаю видео от водяного знака...*", parse_mode="Markdown")

    try:
        # Используем быстрое и открытое API Tikwm для получения прямой ссылки на видео
        api_url = f"https://www.tikwm.com/api/?url={tiktok_url}"
        response = requests.get(api_url, timeout=10).json()

        if response.get("code") == 0:
            video_data = response.get("data", {})
            # Ссылка на видео без водяного знака
            clean_video_url = "https://www.tikwm.com" + video_data.get("play")
            video_title = video_data.get("title", "TikTok Video")

            # Бот удаляет сообщение со статусом загрузки, чтобы не засорять чат
            bot.delete_message(message.chat.id, status_msg.message_id)

            # Отправляем видео файлом прямо в Телеграм
            bot.send_video(
                message.chat.id, 
                clean_video_url, 
                caption=f"🎬 **Вот твоё видео без водяного знака!**\n\n💬 _Описание:_ {video_title}\n\n🤖 Скачано через @{bot.get_me().username}",
                parse_mode="Markdown"
            )
        else:
            bot.edit_message_text("❌ Не удалось скачать видео. Возможно, оно приватное или удалено.", message.chat.id, status_msg.message_id)

    except Exception as e:
        print(f"Ошибка: {e}")
        bot.edit_message_text("❌ Произошла ошибка при обработке видео. Попробуйте еще раз позже.", message.chat.id, status_msg.message_id)

if __name__ == '__main__':
    print("🚀 Бот-скачиватель TikTok успешно запущен и готов к работе!")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            time.sleep(3)
          
