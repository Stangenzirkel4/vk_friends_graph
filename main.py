import networkx as nx
import vk_api
import os
import matplotlib.pyplot as plt

options = {
    'node_color': '#3AEBCA',  # цвет узла
    'node_size': 3500,  # размер узла
    'edge_color': '#101010',  # цвет соединений
    'font_size': 7,  # размер шрифта
    'with_labels': True  # печатать ли заголовки узлов
}


def make_gridlist(user_id):  # Метод для получения друзей через vk api и записи их в файл
    if not user_id:
        person = vk.method('users.get')  # Возвращает данные о пользователе, чей логин был введен
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

    # Теперь запишем друзей в файл

    # Открываем с правами на всё
    f = open('grid.edgelist', 'a', encoding='utf-8')
    for friend in friends_info:

        # Для каждого друга в списке берем нужные данные
        friend_name = friend['first_name']
        friend_last_name = friend['last_name']
        friend_id = str(friend['id'])

        # Записываем все в формате, удобном для последующего создания графа
        node = '{} {} {}:{} {} {}:'.format(person_name, person_last_name, person_id, friend_name, friend_last_name,
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
                node = '{} {} {}:{} {} {}:'.format(friend_name, friend_last_name, friend_id, mutual_name,
                                                   mutual_last_name, mutual_id) + '{}\n'
                f.write(node)
        except:
            print('Cant get mutuals of id' + str(person_id), 'with id' + str(friend['id']))
    f.close()


def draw_graph():  # Метод для отрисовки графа
    # Создаем граф, считывая данные о вершинах и ребрах из файла
    G = nx.read_edgelist(path="grid.edgelist", delimiter=":")

    # Рисуем граф с помощью функции draw
    nx.draw(G, **options)
    # вы также можете попробовать использовать следующие варианты
    # nx.draw_circular(G, **options) - в виде кружочка
    # nx.draw_shell(G, **options) - концентрическими кругами
    # nx.draw_spiral(G, **options) - в виде спиральки
    # nx.draw_spectral(G, **options) - со спектральной кластеризацией

    # устанавливаем размер изображения в дюймах
    plt.gcf().set_size_inches(30, 30)
    # Сохраняем граф в файл
    plt.savefig('graph.png')


def cluster_with_label_propagation():  # Функция для кластеризации графа методом Лувейна

    G = nx.read_edgelist(path="grid.edgelist", delimiter=":")  # Считываем граф

    communities = nx.community.asyn_lpa_communities(G)
    # Получаем список кластеров (кластер - список вершин)
    # Более подробное объяснение метода в отчете

    # Записываем в файл
    f = open('label_propagation.txt', 'a', encoding='utf-8')
    community_number = 0
    for cluster in communities:
        community_number += 1
        f.write('\n' + 'Люди, входящие в группу № {}'.format(community_number) + '\n')
        for node in cluster:
            f.write(node + "\n")
    f.close()


def cluster_with_girvan_newman():  # Функция для кластеризации графа методом Гирван - Ньюмена

    number_of_groups = 5        # Можно менять
    G = nx.read_edgelist(path="grid.edgelist", delimiter=":")   # Считываем граф
    iterator = nx.community.girvan_newman(G)
    # Получаем итератор
    # Чтобы обратиться к конкретному шагу нужно создать список по итератору и обратиться к нужному элементу
    communities = list(iterator)[number_of_groups - 1 - 1]
    # -1 потому что в первой итерации уже есть одна группа
    # еще -1 потому что нумерация с нуля

    # Записываем в файл
    f = open('girvan_newman.txt', 'a', encoding='utf-8')
    community_number = 0
    for cluster in communities:
        community_number += 1
        f.write('\n' + 'Люди, входящие в группу № {}'.format(community_number) + '\n')
        for node in cluster:
            f.write(node + "\n")
    f.close()


def get_laplacian():  # Метод для получения лапласиана графа
    # Создаем граф, считывая данные о вершинах и ребрах из файла
    G = nx.read_edgelist(path="grid.edgelist", delimiter=":")

    # С помощью метода библиотеки networkx получаем лапласиан графа
    L = nx.laplacian_matrix(G)

    # Переводим в numpy array
    L_array = L.toarray()
    # Здесь настроена запись в файл, настраивайте под себя
    # Сейчас сделана под формат чтения матриц matlab
    with open('Laplacian.txt', 'w') as f:
        for l in L_array:
            line = ""
            for i in l:
                line += (str(i)) + ","
            line += "\n"
            f.write(line)


if __name__ == "__main__":
    # Очистка данных от предыдущего запуска
    # os.remove("grid.edgelist")
    # os.remove("label_propagation.txt")
    # os.remove("girvan_newman.txt")

    # Использование данных для авторизации из файла (чтобы не удалять перед каждым комитом)
    with open('pas.txt') as f:
        temp = f.read().splitlines()
        login = temp[0]  # Логин и пароль для входа
        password = temp[1]
        user_id = temp[2]  # id человека, чьих друзей мы ищем

    # Вы можете записать логин и пароль в файл 'pas.txt' или просто присвоить переменным значения
    # login = '123123'
    # password = 'qwerty'
    # user_id = '000000001'

    # авторизация Вк
    vk = vk_api.VkApi(login=login, password=password, app_id=2685278)
    vk.auth()

    # Метод для получения друзей через vk api и записи их в файл
    make_gridlist(user_id)
    # Рекомендую один раз записать файл для нужного человека, потом закомментить

    draw_graph()    # Метод для отрисовки графа
    cluster_with_label_propagation()      # Функция для кластеризации графа методом Лувейна
    cluster_with_girvan_newman()        # Функция для кластеризации графа методом Гирван - Ньюмена

    # Метод для получения лапласиана графа
    get_laplacian()

    # Многое из того, что использовано, бралось отсюда
    # https://github.com/Jumas-Cola/simple_vk_friends_graph
    # По ссылке выше реализован более глубокий обход графа (друзья друзей и т.д) и несколько других фич
