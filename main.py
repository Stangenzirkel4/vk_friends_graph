import vk_api

if __name__ == "__main__":

    # Нужно, чтобы не удалять пароль при каждом коммите
    with open('pas.txt') as f:
        login = f.readline()        # Логин и пароль для входа
        password = f.readline()
        id = f.readline()           # id человека, чьих друзей мы ищем

    # Вы можете записать логин и пароль в файл 'pas.txt' или просто присвоить переменным значения
    # login = '123123'
    # password = 'qwerty'
    # user_id = '000000001'

    # авторизация Вк
    vk = vk_api.VkApi(login=login, password=password, app_id=2685278)
    vk.auth()