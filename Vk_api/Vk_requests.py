import requests

import time


class VkUser:
    URL = "https://api.vk.com/method/"

    def __init__(self, user_id, token_group):
        self.params = {"user_ids": user_id, "access_token": token_group, "v": "5.131"}

    def info_user(self):
        url = self.URL + "users.get"
        params = {"fields": "sex, bdate, city"}
        res = requests.get(url, params={**self.params, **params}).json()
        resp = res["response"][0]
        if "bdate" and "city" not in resp:
            return 0
        else:
            birth_date, sex, city = resp["bdate"], resp["sex"], resp["city"]
            date = birth_date.split(".")
            birth_year = int(date[2])
            return birth_year, sex, city

    def name_user(self):
        url = self.URL + "users.get"
        res = requests.get(url, params=self.params).json()
        name = res["response"][0]["first_name"]
        return name


class VkUsers:
    URL = "https://api.vk.com/method/"

    def __init__(self, token_vk):
        self.params = {"access_token": token_vk, "v": "5.131"}

    def info_all_users(self, birth_year, sex, city):
        sex_dict = {1: 2, 2: 1}
        response = list()
        for year in range(birth_year - 2, birth_year + 2):
            params = {
                "sort": "0",
                "count": 1000,
                "city": city["id"],
                "hometown": city["title"],
                "birth_year": year,
                "sex": sex_dict[sex],
                "online": 1,
                "has_photo": 1,
                "fields": "city, bdate, photo_id",
            }
            url = self.URL + "users.search"
            res = requests.get(url, params={**self.params, **params}).json()
            response += res["response"]["items"]
        return response


class VkPhoto:
    URL = "https://api.vk.com/method/"

    def __init__(self, token_vk, owner_id):
        self.params = {"owner_id": owner_id, "access_token": token_vk, "v": "5.131"}

    def get_photos(self):
        params = {"extended": 1, "photo_sizes": 1, "count": 200}
        url = self.URL + "photos.getAll"
        res = requests.get(url, params={**self.params, **params}).json()
        time.sleep(0.33)
        response = res["response"]["items"]
        return response

    def get_sort_photos(self):
        photo_list = list()
        photo_list_all = self.get_photos()
        for photo in photo_list_all:
            json_photo = {
                "like": photo["likes"]["count"],
                "owner_id": photo["owner_id"],
                "id": photo["id"],
            }
            photo_list.append(json_photo)
        photo_list.sort(key=lambda dictionary: dictionary["like"], reverse=True)
        return photo_list

    def most_like_photos(self, count_of_photo=3):
        like_photo = list()
        photo_list_sort = self.get_sort_photos()
        for photo in photo_list_sort:
            if len(like_photo) == count_of_photo:
                break
            else:
                like_photo.append(photo)
        return like_photo
