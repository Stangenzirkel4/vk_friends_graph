import networkx as nx
import vk_api
import os
import matplotlib.pyplot as plt


if __name__ == "__main__":
    # Удаляет данные от предыдущего запуска
    os.remove("grid.edgelist")

    # Нужно, чтобы не удалять пароль при каждом коммите
    with open('pas.txt') as f:
        temp = f.read().splitlines()
        login = temp[0]       # Логин и пароль для входа
        password = temp[1]
        user_id = temp[2]         # id человека, чьих друзей мы ищем

    # Вы можете записать логин и пароль в файл 'pas.txt' или просто присвоить переменным значения
    # login = '123123'
    # password = 'qwerty'
    # user_id = '000000001'

    # авторизация Вк
    vk = vk_api.VkApi(login=login, password=password, app_id=2685278)
    vk.auth()

    if not user_id:
        person = vk.method('users.get')     # Возвращает данные о пользователе, чей логин был введен
        user_id = person[0]['id']
    else:
        person = vk.method('users.get', {'user_ids': user_id})  # Возвращает человека по его id

    # person состоит из полей:
    # id (integer) - Идентификатор пользователя
    # first_name (string) - Имя
    # last_name (string) - Фамилия
    # deactivated (string) Поле возвращается, если страница пользователя удалена/заблокирована, содержит deleted/banned
    # is_closed (boolean) - Скрыт ли профиль пользователя настройками приватности
    # can_access_closed (boolean) - Может ли текущий пользователь видеть профиль

    person_name = person[0]['first_name']
    person_last_name = person[0]['last_name']
    person_id = str(person[0]['id'])

    # Возвращает список из id друзей вида
    # {'count': 3, 'items': [0000001, 0000002, 0000003]}
    friends = vk.method('friends.get', {'user_id': user_id})

    # Получаем информацию о всех друзьях
    friends_info = vk.method('users.get', {'user_ids': ','.join([str(i) for i in friends['items']])})

    # Теперь пишем друзей в файл

    # Открываем с правами на всё
    f = open('grid.edgelist', 'a', encoding='utf-8')
    for friend in friends_info:

        # Для каждого друга в списке берем нужные данные
        friend_name = friend['first_name']
        friend_last_name = friend['last_name']
        friend_id = str(friend['id'])

        # Записываем все в формате, удобном для последующего создания графа
        node = '{}/{}/{}:{}/{}/{}:'.format(person_name, person_last_name, person_id, friend_name, friend_last_name,
                                           friend_id) + '{}\n'
        f.write(node)

        try:
            # Получаем информацию о связях текущего друга (try нужен на случай отсутствия доступа к странице)
            mutuals = vk.method('friends.getMutual', {'source_uid': person_id, 'target_uid': friend['id']})
            # Метод getMutual возвращает общих друзей у пользователей с source_uid и target_uid в виде списка id

            # Теперь получаем информацию обо всех общих друзьях
            mutuals_info = vk.method('users.get', {'user_ids': ','.join([str(i) for i in mutuals])})

            for mutual in mutuals_info:
                # И повторяем для них процесс записи
                mutual_name = mutual['first_name']
                mutual_last_name = mutual['last_name']
                mutual_id = str(mutual['id'])
                node = '{}/{}/{}:{}/{}/{}:'.format(friend_name, friend_last_name, friend_id, mutual_name,
                                                   mutual_last_name, mutual_id) + '\n'
                f.write(node)
        except:
            print('Cant get mutuals of id' + str(person_id), 'with id' + str(friend['id']))
    f.close()

