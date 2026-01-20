# src/bot.py
import os
import random
from dotenv import load_dotenv
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from src.vk_client import VKClient
from src.storage import add_to_favorites, get_favorites

load_dotenv()
GROUP_TOKEN = os.getenv("VK_GROUP_TOKEN")
USER_TOKEN = os.getenv("VK_USER_TOKEN")

if not GROUP_TOKEN or not USER_TOKEN:
    raise ValueError("Укажите оба токена в .env")

# Инициализация
vk_group = vk_api.VkApi(token=GROUP_TOKEN)
vk_send = vk_group.get_api()
longpoll = VkLongPoll(vk_group)
vk_search = VKClient(USER_TOKEN)

# Хранилище состояний: {user_id: {"params": ..., "current": {...}}}
user_sessions = {}


def send_msg(user_id, message, attachment=""):
    vk_send.messages.send(
        user_id=user_id,
        message=message,
        attachment=attachment,
        random_id=random.randint(1, 10**9),
        keyboard=get_keyboard()
    )


def get_keyboard():
    kb = VkKeyboard(one_time=False)
    kb.add_button("Следующий", color=VkKeyboardColor.PRIMARY)
    kb.add_button("В избранное", color=VkKeyboardColor.POSITIVE)
    kb.add_line()
    kb.add_button("Избранные", color=VkKeyboardColor.SECONDARY)
    return kb.get_keyboard()


def handle_start(user_id):
    try:
        info = vk_search.get_user_info(user_id)
        bdate = info.get("bdate", "")
        if len(bdate.split(".")) != 3:
            send_msg(user_id, "Укажите полную дату рождения (ДД.ММ.ГГГГ) в профиле.")
            return

        birth_year = int(bdate.split(".")[2])
        age = 2026 - birth_year
        city_id = info.get("city", {}).get("id")
        if not city_id:
            send_msg(user_id, "Укажите город в профиле.")
            return

        search_sex = 1 if info["sex"] == 2 else 2
        user_sessions[user_id] = {
            "params": {"age": age, "city_id": city_id, "sex": search_sex},
            "current": None
        }
        send_msg(user_id, "Подбираю анкеты...")
        show_next(user_id)
    except Exception as e:
        send_msg(user_id, "Ошибка при получении данных. Проверьте настройки профиля.")


def show_next(user_id):
    session = user_sessions.get(user_id)
    if not session:
        handle_start(user_id)
        return

    params = session["params"]
    candidates = vk_search.search_users(
        age_from=params["age"] - 2,
        age_to=params["age"] + 2,
        sex=params["sex"],
        city_id=params["city_id"]
    )

    if not candidates:
        send_msg(user_id, "Анкеты не найдены.")
        return

    candidate = candidates[0]
    photos = vk_search.get_top_photos(candidate["id"], 3)
    profile_url = f"https://vk.com/id{candidate['id']}"

    user_sessions[user_id]["current"] = {
        "vk_id": candidate["id"],
        "first_name": candidate["first_name"],
        "last_name": candidate["last_name"],
        "profile_url": profile_url,
        "photos": photos
    }

    msg = f"{candidate['first_name']} {candidate['last_name']}\n{profile_url}"
    att = ",".join(photos) if photos else ""
    send_msg(user_id, msg, att)


def handle_add_favorite(user_id):
    current = user_sessions.get(user_id, {}).get("current")
    if not current:
        send_msg(user_id, "Нет текущей анкеты.")
        return
    add_to_favorites(current)
    send_msg(user_id, "✅ Добавлено в избранное!")


def handle_show_favorites(user_id):
    favs = get_favorites()
    if not favs:
        send_msg(user_id, "Избранных нет.")
        return
    msg = "❤️ Избранные:\n"
    for f in favs[-5:]:
        msg += f"- {f['first_name']} {f['last_name']}\n{f['profile_url']}\n\n"
    send_msg(user_id, msg)


def main():
    print("✅ Бот запущен. Ожидание сообщений...")
    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            uid = event.user_id
            text = event.text.strip().lower()

            if text in ["привет", "start", "начать", ""]:
                handle_start(uid)
            elif text == "следующий":
                show_next(uid)
            elif text == "в избранное":
                handle_add_favorite(uid)
            elif text in ["избранные", "показать избранных"]:
                handle_show_favorites(uid)
            else:
                send_msg(uid, "Используйте кнопки.")


if __name__ == "__main__":
    main()