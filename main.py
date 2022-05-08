with open('vk_token.txt', 'r') as file_object:
    VK_TOKEN = file_object.read().strip()

import datetime
import os
from os import path
import requests
import time
from tqdm import tqdm
import json
from pprint import pprint

class VK:

    def __init__(self, VK_USER_ID, VK_TOKEN, album_id="profile"):

        self.VK_USER_ID = VK_USER_ID
        self.VK_TOKEN = VK_TOKEN
        self.album_id = album_id
        self.photo_json = []
        self.photo_list = []


    def get_photo_info(self, offset=0, count=5):
        self.offset = offset
        self.count = count
        api = requests.get('https://api.vk.com/method/photos.get',
                           params={
                               'owner_id': self.VK_USER_ID,
                               'access_token': self.VK_TOKEN,
                               'album_id': self.album_id,
                               'extended': '1',
                               'count': self.count,
                               'offset': self.offset,
                               'photo_sizes': '1',
                               'v': '5.131'})
        return json.loads(api.text)

    def get_photo(self, photos_folder):
        self.photos_folder = photos_folder
        data = self.get_photo_info()
        count_photo = data['response']['count']
        index = 0
        count = 5
        photos = []

        while index <= count_photo:
            if index != 0:
                data = self.get_photo_info(offset=index, count=count)
            for files in tqdm(data['response']['items']):
                photo_data = {}
                upload_time = time.ctime(files['date'])
                ch_time_1 = upload_time.replace(' ', '_')
                h_upload_time = ch_time_1.replace(":", "_")
                photo_data['size'] = data['response']['items'][-1]['sizes'][-1]['type']
                file_url = files['sizes'][-1]['url']
                photo_big_size = file_url.split("/")[-1]
                filename = photo_big_size.split("?")[0]
                new_filename = filename.replace(filename, (format(files['likes']['count']) + ".jpg"))
                if new_filename in self.photo_list:
                    photos.append(new_filename)
                    time.sleep(0.1)
                    api = requests.get(file_url)
                    file_name_orig = new_filename.replace(".jpg", "_" + h_upload_time)
                    photo_data['filename'] = file_name_orig
                    self.photo_list.append(file_name_orig)
                    with open(os.path.join(photos_folder, "Likes_number_{}.jpg".format(file_name_orig)), "wb") as file:
                        print(file_name_orig)
                        file.write(api.content)
                else:
                    photos.append(filename)
                    time.sleep(0.1)
                    api = requests.get(file_url)
                    photo_data['filename'] = new_filename
                    self.photo_list.append(new_filename)
                    with open(os.path.join(photos_folder, "Likes_number_{}".format(new_filename)), "wb") as file:
                        print(new_filename)
                        file.write(api.content)
                        print()
                self.photo_json.append(photo_data)

            index += count
        pprint(len(photos))
        pprint(f'Фотографии пользователя {self.VK_USER_ID}  загружены в папку {photos_folder} список фотографий и их '
               f'размер  {self.photo_json}')


class YaDisk:
    def __init__(self, token, photos_folder, ya_folder):
        self.photos_folder = photos_folder
        self.token = token
        self.ya_folder = ya_folder

    def get_headers(self):
        return {'Content-type': 'application/json', 'Authorization': 'OAuth {}'.format(self.token)}

    def create_folder(self):
        folder_url = "https://cloud-api.yandex.net/v1/disk/resources/"
        headers = self.get_headers()
        params = {"path": self.ya_folder}
        response_folder = requests.put(folder_url, headers=headers, params=params)
        return response_folder.json().get("href", "")

    def upload(self):
        upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = self.get_headers()
        index = 0
        arr = os.listdir(self.photos_folder)
        for file in tqdm(arr):
            params = {
                "path": f'{self.ya_folder}/' + arr[index],
                "overwrite": "true",
                "templated": "false"}
            response_upload = requests.get(upload_url, headers=headers, params=params)
            res = response_upload.json().get("href", "")
            try:
                response_url = requests.put(res, data=open("{}\\{}".format(self.photos_folder, arr[index]), 'rb'))
                print(arr[index])
                response_url.raise_for_status()
                if response_url.status_code == 201:
                    log_time = datetime.datetime.now()
                    message = f'{log_time}: Фото "{arr[index]}" загружено на Yandex.Disk в папку {self.ya_folder}'
                    print(message)

            except FileNotFoundError:
                print("Файл не найден")

            index += 1


def create_folder(folder_name):
    try:
        if os.path.exists(folder_name):
            answer_yes = input(f'Директория {folder_name} уже существует, хотите перезаписать? Да/Нет? ').lower()
            if answer_yes == 'Да':
                os.makedirs(folder_name, exist_ok=True)
                folder_place = os.path.abspath(folder_name)
                print(f'Folder was created {folder_name} full path {os.path.abspath(folder_name)}')
            else:
                folder_place = os.path.abspath(folder_name)
        else:
            os.mkdir(folder_name)
            folder_place = os.path.abspath(folder_name)

    except OSError as error:
        print(f'Директория {folder_name} не может быть создана')

    return folder_place


def menu():
    folder_name = input(f'Введите название папки: ')
    photos_folder = create_folder(folder_name)
    VK_USER_ID = input(f'Введите VK ID откуда загрузить фото: ')
    ya_token = input(f'Введите токен Яндекс.Полигон: ')
    ya_folder = input(f'Имя папки для Яндекс.Диска :')

    user1 = VK(VK_USER_ID, VK_TOKEN)
    user1.get_photo(photos_folder)
    user1 = YaDisk(ya_token, photos_folder, ya_folder)
    user1.create_folder()
    user1.upload()


def main_p():
    print(menu())

if __name__ == "__main__":
    main_p()