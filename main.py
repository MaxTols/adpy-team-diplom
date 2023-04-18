import os

from dotenv import load_dotenv

from random import randrange

import vk_api

from vk_api.longpoll import VkLongPoll, VkEventType
from Vk_api.Vk_requests import VkUser, VkUsers, VkPhoto

from DataBase.database_session import (
    add_user,
    add_photo,
    add_favorite,
    get_random,
    favorites_list,
    add_black,
    del_user,
)


load_dotenv()
token_vk = os.getenv("TOKEN_VK")
token_group = os.getenv("TOKEN_GROUP")
vk = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk)


def write_msg(vk_send, user_id, message):
    message = {"user_id": user_id, "message": message, "random_id": randrange(10**7)}
    vk_send.method("messages.send", message)


def write_photo(vk_send, user_id, attachment):
    message = {
        "user_id": user_id,
        "attachment": attachment,
        "random_id": randrange(10**7),
    }
    vk_send.method("messages.send", message)


def get_love():
    photo_set = set()
    id_set = set()
    people_now = tuple()
    command_list = (
        "\n1:   Начать"
        "\n3:   Дальше"
        "\n5:   Добавить в избранные"
        "\n7:   Список избранных"
        "\n9:   Добавить в черный список"
    )

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            request = event.text
            vk_user = VkUser(event.user_id, token_group=token_group)
            user_name = vk_user.name_user()

            if request == "Привет":
                write_msg(vk, event.user_id, f"Привет, {user_name}")
                write_msg(
                    vk,
                    event.user_id,
                    "Для корректной работы приложения убедитесь, что:\n"
                    "- ваш аккаунт в открытом доступе;\n"
                    "- указан город вашего местоположения;\n"
                    "- год рождения виден всем;\n"
                    "- указан ваш пол.\n"
                    'Если все условия выполнены, напишите: "Начать"',
                )

            elif request in ("1", "Начать"):
                write_msg(vk, event.user_id, f"Идет поиск подходящих пользователей...")
                user = vk_user.info_user()
                if user == 0:
                    write_msg(vk, event.user_id, f"НЕ ВЫПОЛНЕНЫ ВСЕ УСЛОВИЯ!")
                else:
                    vk_users = VkUsers(token_vk=token_vk)
                    response = vk_users.info_all_users(user[0], user[1], user[2])

                    for people in response:
                        if "city" in people and people["can_access_closed"] is True:
                            if people["id"] not in id_set:
                                add_user(
                                    people["id"],
                                    people["first_name"],
                                    people["last_name"],
                                )
                                id_set.add(people["id"])
                    write_msg(
                        vk, event.user_id, f"Подходящих пользователей: {len(id_set)}"
                    )
                    write_msg(
                        vk,
                        event.user_id,
                        f'Для просмотра подходящих пользователей напишите: "3" или "Дальше"\n'
                        f"Также можно использовать сокращенные команды вызова: {command_list}",
                    )

            elif request in ("3", "Дальше"):
                random_id = get_random()
                write_msg(
                    vk,
                    event.user_id,
                    f"{random_id[1]} {random_id[2]} \nvk.com/id{random_id[0]}",
                )
                vk_photo = VkPhoto(token_vk=token_vk, owner_id=random_id[0])
                max_like = vk_photo.most_like_photos()
                people_now = random_id

                for photo in max_like:
                    write_photo(
                        vk, event.user_id, f"photo{photo['owner_id']}_{photo['id']}"
                    )
                    if photo["owner_id"] not in photo_set:
                        add_photo(photo["id"], photo["like"], photo["owner_id"])
                photo_set.add(random_id[0])

            elif request in ("5", "Добавить в избранные"):
                favorites_id = [i[0] for i in favorites_list()]
                if people_now[0] not in favorites_id:
                    add_favorite(people_now[0], people_now[1], people_now[2])
                    write_msg(
                        vk,
                        event.user_id,
                        f"vk.com/id{people_now[0]} добавлен в избранные",
                    )
                else:
                    write_msg(vk, event.user_id, f"Пользователь уже в списке избранных")

            elif request in ("7", "Список избранных"):
                if len(favorites_list()) == 0:
                    write_msg(
                        vk,
                        event.user_id,
                        f"Список избранных пуст",
                    )
                else:
                    for favorite in favorites_list():
                        write_msg(
                            vk,
                            event.user_id,
                            f"{favorite[1]} {favorite[2]} vk.com/id{favorite[0]}",
                        )

            elif request in ("9", "Добавить в черный список"):
                add_black(people_now[0], people_now[1], people_now[2])
                del_user(people_now[0])
                write_msg(
                    vk,
                    event.user_id,
                    f"vk.com/id{people_now[0]} добавлен в черный список",
                )

            elif request == "Пока":
                write_msg(vk, event.user_id, "До скорого!")
                break

            else:
                write_msg(vk, event.user_id, "Не понял вашего ответа...")

    return "Программа завершила свою работу"


if __name__ == "__main__":
    get_love()
