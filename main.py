import itertools

import networkx as nx
import vk
import vk_api
import os
import matplotlib.pyplot as plt

options = {
    'node_color': '#3AEBCA',  # цвет узла
    'node_size': 3500,  # размер узла
    'edge_color': '#F0F0F0',  # цвет соединений
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
                                                   mutual_last_name, mutual_id) + '{}\n'
                f.write(node)
        except:
            print('Cant get mutuals of id' + str(person_id), 'with id' + str(friend['id']))
    f.close()


def draw_standart_graph():  # Метод для отрисовки стандартного графа
    # Создаем граф, считывая данные о вершинах и ребрах из файла
    G = nx.read_edgelist(path="grid.edgelist", delimiter=":")

    # Рисуем граф с помощью функции draw
    nx.draw(G, **options)
    # вы также можете попробовать использовать следующие варианты
    # nx.draw_circular(G, **options) -
    # nx.draw_shell(G, **options) -
    # nx.draw_spiral(G, **options) -
    # nx.draw_spectral(G, **options) -

    # устанавливаем размер изображения в дюймах
    plt.gcf().set_size_inches(30, 30)
    # Сохраняем граф в файл
    plt.savefig('graph.png')


def draw_louvain_graph():
    def show_graph(graph): # Вывод вершин и их кластеров
        node_cluster_map = nx.get_node_attributes(clustered_graph, 'cluster')
        for node, cluster in node_cluster_map.items():
            print(f"Вершина {node} в кластере {cluster}")

    G = nx.read_edgelist(path="grid.edgelist", delimiter=":")
    # Выполнение кластеризации методом Лувейна
    communities = nx.community.greedy_modularity_communities(G)

    # Преобразование результата в словарь, где ключи - вершины, значения - номера кластеров
    clustered_graph = nx.Graph()
    cluster_id = 0
    for cluster in communities:
        for node in cluster:
            clustered_graph.add_node(node, cluster=cluster_id)
        cluster_id += 1
    for u, v in G.edges():
        if u in clustered_graph.nodes() and v in clustered_graph.nodes():
            clustered_graph.add_edge(u, v)
    show_graph(clustered_graph)
    # Рисование и сохранение кластеризованного графа
    nx.draw(clustered_graph, **options)
    plt.gcf().set_size_inches(30, 30)
    plt.savefig('louvain_graph.png')


def draw_girvan_newman_graph(): # Метод для отрисовки графа, используя кластеризацию "Girvan-Newman"
    def show_clusters(comp, k):
        clusters1 = []
        for communities in itertools.islice(comp, k-1):
            clusters1 = list(communities)

        # Формирование списка, показывающего кластеры для каждой вершины
        node_clusters = {}
        for i, cluster1 in enumerate(clusters1):
            for node in cluster1:
                node_clusters[node] = i

        for i in range(5):
            print("people from " + str(i + 1) + " cluster")
            nodes = [key for key, value in node_clusters.items() if value == i]
            print(nodes)

    G = nx.read_edgelist(path="grid.edgelist", delimiter=":")
    comp = nx.community.girvan_newman(G)
    k = 5  # Количество кластеров
    show_clusters(comp, k)


    # Определяем сообщества в графе
    limited = tuple(sorted(c) for c in next(itertools.islice(comp, k - 1)))
    clusters = {node: cid for cid, cluster in enumerate(limited) for node in cluster}

    # Создаем копию графа и присваиваем кластеры узлам
    clustered_graph = G.copy()
    for node in clustered_graph.nodes():
        clustered_graph.nodes[node]['cluster'] = clusters.get(node)
    nx.draw(clustered_graph, **options)
    plt.gcf().set_size_inches(30, 30)
    plt.savefig('gnm_graph.png')
    return comp


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
    try:
        os.remove("grid.edgelist")
    except:
        print("Nothing to delete")

    # Использование авторизационных данных из файла
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

    # Блок отрисовок графа
    #draw_standart_graph()
    draw_louvain_graph()
    #draw_girvan_newman_graph()

    # Метод для получения лапласиана графа
    get_laplacian()

    # Многое из того, что использовано, бралось отсюда
    # https://github.com/Jumas-Cola/simple_vk_friends_graph
    # По ссылке выше реализован более глубокий обход графа (друзья друзей и т.д) и несколько других фич
