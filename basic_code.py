import requests

import psycopg2

from pprint import pprint

from random import randrange

import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType

# token = input('Token: ')

token_group = ''
token_vk = ''


vk = vk_api.VkApi(token=token_group)
longpoll = VkLongPoll(vk)


def write_msg(user_id, message):
    vk.method('messages.send', {'user_id': user_id, 'message': message,  'random_id': randrange(10 ** 7),})


def create_db():
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id SERIAL PRIMARY KEY,
            first_name VARCHAR(40) NOT NULL,
            last_name VARCHAR(40) NOT NULL,
            city VARCHAR(80) NOT NULL
        );
        """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS photo(
        id SERIAL PRIMARY KEY,
        photo_id INTEGER NOT NULL,
        like_count INTEGER NOT NULL,
        user_id INTEGER NOT NULL REFERENCES users(user_id)
    );
    """)
    conn.commit()


def add_user(user_id, first_name, last_name, city):
    cur.execute("""
    INSERT INTO users(user_id, first_name, last_name, city)
    VALUES(%s, %s, %s, %s);
    """, (user_id, first_name, last_name, city))
    print('Пользователь добавлен')
    conn.commit()


def add_photo(photo_id, like_count, user_id):
    cur.execute("""
    INSERT INTO photo(photo_id, like_count, user_id)
    VALUES(%s, %s, %s);
    """, (photo_id, like_count, user_id))
    print('Фото добавлено')
    conn.commit()


def delete_table():
    cur.execute("""
    DROP TABLE photo;
    DROP TABLE users;
    """)
    print('Таблицы удалены!')


def delete_photo():
    cur.execute("""
    DELETE FROM photo;
    """)
    print('База чиста!')
    conn.commit()


def delete_users():
    cur.execute("""
    DELETE FROM users;
    """)
    print('База чиста!')
    conn.commit()


def all_info():
    cur.execute("""
    SELECT * FROM users u
    LEFT JOIN photo p ON u.user_id = p.user_id;
    """)
    # pprint(cur.fetchall())
    return cur.fetchall()


for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW:

        if event.to_me:
            request = event.text

            if request == "А":
                write_msg(event.user_id, f"Хай, {event.user_id}")

                URL = 'https://api.vk.com/method/users.get'
                params = {
                    'user_ids': f'{event.user_id}',
                    'access_token': token_group,
                    'v': '5.131',
                    'fields': 'sex, bdate, city, music, book, screen_name'
                }
                res = requests.get(URL, params=params).json()
                # pprint(res)

                resp = res['response'][0]
                bdate, sex, city = resp['bdate'], resp['sex'], resp['city']
                # print(bdate, sex, city)

                sex_dict = dict()
                sex_dict[1] = 2
                sex_dict[2] = 1

                by = bdate.split('.')
                if len(by) == 3:
                    birth_year = int(by[2])
                    age_from = 2023 - birth_year - 1
                    age_to = 2023 - birth_year + 1
                else:
                    birth_year = int(input('Введите год вашего рождения: '))
                    age_from = 2023 - birth_year - 1
                    age_to = 2023 - birth_year + 1

                params = {
                    'access_token': token_vk,
                    'v': '5.131',
                    'sort': '0',
                    'count': 10,
                    'city': city['id'],
                    'hometown': city['title'],
                    'age_from': age_from,
                    'age_to': age_to,
                    'sex': sex_dict[sex],
                    'fields': 'city, bdate, music, books, photo_id'
                }
                res = requests.get('https://api.vk.com/method/users.search', params=params).json()
                # pprint(res['response']['items'])
                # print(len(res['response']['items']))
                response = res['response']['items']
                people_list = list()
                for i in response:
                    max_like_1, max_like_2, max_like_3, = 0, 0, 0
                    if 'city' in i and i['can_access_closed'] is True:
                        print(i['first_name'], i['last_name'], i['id'], i['city']['title'])

                        params_1 = {
                            'access_token': token_vk,
                            'v': '5.131',
                            'owner_id': i['id'],
                            'extended': 1,
                            'photo_sizes': 1,
                            'count': 200
                        }
                        respo = requests.get('https://api.vk.com/method/photos.getAll', params=params_1).json()
                        # pprint(respo)
                        respo_1 = respo['response']['items']

                        file_name = list()
                        json_list = list()

                        for foto in respo_1:
                            like_count = foto['likes']['count']
                            file_name.append(like_count)
                            json_file = {'like': like_count, 'owner_id': foto['owner_id'], 'id': foto['id']}
                            json_list.append(json_file)

                            if like_count > max_like_1:
                                max_like_1, max_like_2, max_like_3 = like_count, max_like_1, max_like_2
                            elif like_count > max_like_2:
                                max_like_2, max_like_3, = like_count, max_like_2
                            elif like_count > max_like_3:
                                max_like_3 = like_count
                        # print(max_like_1, max_like_2, max_like_3)

                        j_list = list()
                        for k in json_list:
                            like_count = k['like']
                            if like_count == max_like_1 or like_count == max_like_2 or like_count == max_like_3:
                                j_list.append(k)
                        people_list.append(j_list)
                # print(people_list)

                with psycopg2.connect(database="diplom", user="postgres", password="postgres") as conn:
                    with conn.cursor() as cur:
                        # delete_table()
                        delete_photo()
                        delete_users()
                        create_db()
                        for i in response:
                            if 'city' in i and i['can_access_closed'] is True:
                                add_user(i['id'], i['first_name'], i['last_name'], i['city']['title'])
                        for people in people_list:
                            for j in people:
                                add_photo(j['id'], j['like'], j['owner_id'])
                        full = all_info()
                        pprint(full)
                        write_msg(event.user_id, f"{full[0][1]} {full[0][2]} \n {full[0][0]}")
                        # write_msg(event.user_id, f"{full[0][1]} {full[0][2]}")
                        # write_msg(event.user_id, f"{full[0][0]}")
                        write_msg(event.user_id, f'photo{full[0][0]}_{full[0][5]}')
                        for f in range(1, len(full)):
                            if full[f][0] == full[f - 1][0]:
                                write_msg(event.user_id, f'photo{full[f][0]}_{full[f][5]}')
                            else:
                                write_msg(event.user_id, f"{full[f][1]} {full[f][2]} \n {full[f][0]}")
                                # write_msg(event.user_id, f"{full[f][1]} {full[f][2]}")
                                # write_msg(event.user_id, f"{full[f][0]}")
                                write_msg(event.user_id, f'photo{full[f][0]}_{full[f][5]}')

                conn.close()

            elif request == "пока":
                write_msg(event.user_id, "Пока((")
            else:
                write_msg(event.user_id, "Не понял вашего ответа...")
