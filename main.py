from DataBase.database_session import add_user, add_photo, add_favorite, get_random, favorites_list

from Vk_api.Vk_requests import VkUser, VkUsers, VkPhoto

from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType


token_group = input()
token_vk = input()


vk = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk)


def write_msg(vk_send, user_id, message):
    message = {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7)}
    vk_send.method("messages.send", message)


def write_photo(vk_send, user_id, attachment):
    message = {'user_id': user_id, 'attachment': attachment,  'random_id': randrange(10 ** 7)}
    vk_send.method("messages.send", message)


def get_love():
    photo_set = set()
    id_set = set()
    people_now = tuple()

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            request = event.text

            if request == "0":
                write_msg(vk, event.user_id, f"Привет, {event.user_id}")
                vk_user = VkUser(event.user_id, token_group=token_group)
                user = vk_user.info_user()
                vk_users = VkUsers(token_vk=token_vk)
                response = vk_users.info_all_users(user[0], user[1], user[2])

                for people in response:
                    if 'city' in people and people['can_access_closed'] is True:
                        if people['id'] not in id_set:
                            add_user(people['id'], people['first_name'], people['last_name'])
                            id_set.add(people['id'])
                print(f'Подходящих пользователей: {len(id_set)}')

            elif request == "1":
                random_id = get_random()
                write_msg(vk, event.user_id, f"{random_id[1]} {random_id[2]} \nvk.com/id{random_id[0]}")
                vk_photo = VkPhoto(token_vk=token_vk, owner_id=random_id[0])
                max_like = vk_photo.most_like_photos()
                people_now = random_id

                for photo in max_like:
                    write_photo(vk, event.user_id, f"photo{photo['owner_id']}_{photo['id']}")
                    if photo['owner_id'] not in photo_set:
                        add_photo(photo['id'], photo['like'], photo['owner_id'])
                photo_set.add(random_id[0])

            elif request == "3":
                favorites_id = [i[0] for i in favorites_list()]
                if people_now[0] not in favorites_id:
                    add_favorite(people_now[0], people_now[1], people_now[2])
                    write_msg(vk, event.user_id, f"vk.com/id{people_now[0]} добавлен в избранные")
                else:
                    write_msg(vk, event.user_id, f"Пользователь уже в списке избранных")

            elif request == "5":
                for favorite in favorites_list():
                    write_msg(vk, event.user_id, f"{favorite[1]} {favorite[2]} vk.com/id{favorite[0]}")

            elif request == "Пока":
                write_msg(vk, event.user_id, "До скорого!")
                break

            else:
                write_msg(vk, event.user_id, "Не понял вашего ответа...")


if __name__ == '__main__':
    get_love()
