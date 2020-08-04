import requests
import urllib
import os
import datetime
import shutil
import json
import time
from progress.bar import Bar #необходимо установить модуль progress.bar 'pip install progress'

VK_ACCESS_TOKEN = "958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008"

id = input("Введите id пользователя: ")
count = int(input("Введите количество фотографий: "))
YA_OAUTH_TOKEN = input("Введите ключ Яндекс Диска: ")


def backup_photos(id, count=5):
    #Запускаем Progress bar
    bar = Bar('Processing', max=7)
    
    #Получаем информацию о фотографиях пользователя VK
    params = {
        "user_id": id,
        "access_token": VK_ACCESS_TOKEN,
        "extended": 1,
        "album_id": "profile",
        "photo_sizes": 1,
        "count": count,
        "v": "5.21"
    }
    
    bar.next()
    
    response = requests.get('https://api.vk.com/method/photos.get', params=params)
    resp_json = response.json()

    bar.next()
    
    #Создаем директорию для скачивания фото
    os.mkdir(id)
    
    bar.next()
    
    #Создаем папку на Яндекс Диске, имя папки = id
    headers = {
        "Authorization": YA_OAUTH_TOKEN
    }
    params_yamkdr = {
        "path": id
    }

    requests.put('https://cloud-api.yandex.net/v1/disk/resources', headers=headers, params=params_yamkdr)
    photos_info = []
    
    bar.next()

    files = [] # Создаем список файлов

    # Проходим итератором по фото, получаем необходимую информацию
    for i in range(len(resp_json["response"]["items"])):
        photo = {}
        photo_url = str(resp_json["response"]["items"][i]["sizes"][len(resp_json["response"]["items"][i]["sizes"])-1]["src"])
        file_name = str(resp_json["response"]["items"][i]['likes']['count']) + '.jpg'
        file_path = str(id) + '/' + file_name
        photo_size = resp_json["response"]["items"][i]["sizes"][len(resp_json["response"]["items"][i]["sizes"])-1]["type"]
        
        # сохраняем фотографии в папку на комп, в качестве имени используем количество лайков, проверяем емена файлов на совпадение. В случае совпадения добавляем к имени файла текущую дату.
        if not os.path.isfile(file_path):
            urllib.request.urlretrieve(photo_url, file_path)
            files.append(file_path)
            photo['file_name'] = file_name
            photo['size'] = photo_size
            photos_info.append(photo)
        else:
            name = str(id) + '/' + str(resp_json["response"]["items"][i]['likes']['count']) + '_' + str(datetime.date.today().strftime("%d%m%Y")) + '.jpg'
            urllib.request.urlretrieve(photo_url, name)
            files.append(name)
            photo['file_name'] = str(resp_json["response"]["items"][i]['likes']['count']) + '_' + str(datetime.date.today().strftime("%d%m%Y")) + '.jpg'
            photo['size'] = photo_size
            photos_info.append(photo)
            
    bar.next()
    
    # Открываем каждый файл для сохранения на Яндекс Диске
    for file in files:
        with open(file, 'rb') as f:
            response_get = requests.get("https://cloud-api.yandex.net/v1/disk/resources/upload", headers=headers, params={"path": file, "overwrite": "true"})
            href = response_get.json()['href']
            operation_id = response_get.json()['operation_id']
            requests.put(href, files={"file": f}, headers=headers)
            status = requests.get(f"https://cloud-api.yandex.net/v1/disk/operations/{operation_id}", headers=headers)
            if status.status_code == 200:
                print("Фото загружено.")
            else:
                print(f"Ошибка {status.status_code} при загрузке.")
    bar.next()
    
    #Удаляем папку с компа
    shutil.rmtree(id)
    
    bar.next()

    #Сохраняем информацию о сохраненных файлах в json формате
    with open('photos_info.json', 'w') as f:
        json.dump(photos_info, f, indent=2, ensure_ascii=False)
    
    bar.finish()
    
backup_photos(id, count)