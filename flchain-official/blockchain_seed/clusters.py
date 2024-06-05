import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
from queue import PriorityQueue, Queue

graph = {}
file_path = 'data/roads.csv'
circle_area = 3
uncompleted_area = 2
leaders = []

def append_edge(source, destination):
    if source not in graph:
        graph[source] = {'neighbours': [], 'circle': set(), 'layer': -1, 'leaders': set()}
    graph[source]['neighbours'].append(destination)


def create_graph():
    df = pd.read_csv(file_path)

    for row in df.values:
        source = int(row[0])
        destination = int(row[1])
        append_edge(source=source, destination=destination)
        append_edge(source=destination, destination=source)


def show_graph(graph, fullscreen = False):
    G = nx.Graph()
    for source, data in graph.items():
        for destination in data['neighbours']:
            G.add_edge(source, destination)

    pos = nx.spring_layout(G)

    node_colors = ['skyblue' if node not in leaders else 'red' for node in G.nodes()]

    nx.draw(G, pos, with_labels=True, node_color=node_colors, node_size=500, font_size=8, font_weight='bold')

    if fullscreen:
        figManager = plt.get_current_fig_manager()
        figManager.full_screen_toggle()

    plt.title('Graph Visualization')
    plt.show()



def initiate_circle(node, area):
    leaders.append(node)
    bfs_queue = Queue()
    graph[node]['layer'] = 0
    graph[node]['leaders'] = {node}
    bfs_queue.put((node, graph[node]['layer']))

    while not bfs_queue.empty():
        curren_node, layer = bfs_queue.get()
        for neighbour in graph[curren_node]['neighbours']:
            neighbour_layer = graph[neighbour]['layer']
            if neighbour_layer == -1 or neighbour_layer >= layer + 1:
                
                if neighbour_layer > layer + 1:
                    graph[neighbour]['leaders'].clear()

                graph[neighbour]['leaders'].add(node)
                graph[neighbour]['layer'] = layer + 1
                graph[neighbour]['circle'].add(curren_node)
                graph[curren_node]['circle'].add(neighbour)
                if layer + 1 < area and area > layer + 1:
                    bfs_queue.put((neighbour, graph[neighbour]['layer']))


def create_circles():
    pq = PriorityQueue()
    eq = Queue()

    for node, data in graph.items():
        no_neighbours = len(data['neighbours'])
        pq.put((-no_neighbours, node))
    
    while not pq.empty():
        priority, node = pq.get()
        priority = abs(priority)
        current_layer = graph[node]['layer']
        if current_layer == -1:
            initiate_circle(node, circle_area)
        elif current_layer == circle_area:
            eq.put(node)

    while not eq.empty():
        node = eq.get()
        data = graph[node]
        if data['layer'] == circle_area and set(data['neighbours']) != data['circle']:
            initiate_circle(node, uncompleted_area)

    # condition = lambda data:  data['layer'] == circle_area and set(data['neighbours']) != data['circle']
    # count = sum(1 for node, data in graph.items() if condition(data))
    # print(count)


def create_infrastructure():
    create_graph()
    create_circles()
    return graph, leaders

# if __name__ == '__main__':
#     create_graph()
#     create_circles()
    # current_leader = 141
    # ceva = {source:attribute for source, attribute in graph.items() if current_leader in attribute['leaders']}
    # for source, attribute in ceva.items():
    #     print(f"{source}  {attribute}")
    # show_graph(graph=graph)

  