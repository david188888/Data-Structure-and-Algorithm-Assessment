import random
from collections import defaultdict
import json
class stack():
    def __init__(self):
        self.items = []

    def append(self, item):
        self.items.append(item)

    def pop(self):
        return self.items.pop()

    def is_empty(self):
        return self.items == []

    def size(self):
        return len(self.items)

    def peek(self):
        return self.items[-1]



class Node():
    def __init__(self,value):
        self.value = value
        self.adjacent = {} # list of adjacent nodes

    def add_adjacent(self, node, weight):
        self.adjacent[node.value] = weight



class Graph():
    def __init__(self):
        self.nodes = {} # dictionary of nodes

    def add_node(self, value):
        if value not in self.nodes:
            self.nodes[value] = Node(value)

    def add_edge(self, value1, weight, value2):
        if value1 in self.nodes and value2 in self.nodes:
            self.nodes[value1].add_adjacent(self.nodes[value2],weight)
            self.nodes[value2].add_adjacent(self.nodes[value1],weight)
        else:
            print("Error: Node not found")



    def length(self):
        return len(self.nodes)
    

        
    def print_graph(self):
        for key in list(self.nodes.keys()):
            print(key, " --> ", end=" ")
            for node, weight in self.nodes[key].adjacent.items():
                print(node, "(",weight,")", end=" | ")
            print()


    def save_to_json(self,filepath):
        graph_data = {}
        for key, node in self.nodes.items():
            graph_data[key] = node.adjacent
        with open(filepath, 'w') as f:
            json.dump(graph_data, f, indent=4)



    def load_from_json(self,filepath):
        with open(filepath, 'r') as f:
            graph_data = json.load(f)
            self.nodes.clear()
        for key, adjacent in graph_data.items():
            self.add_node(key)
            for node, weight in adjacent.items():
                self.add_node(node)
                self.nodes[key].add_adjacent(self.nodes[node], weight)



    def save_node(self):
        with open("station.txt", "r+",encoding="utf-8") as f:
            node = f.read()
            stations = node.split("\n")
            # print(stations)
        lines = [[], [], []]  # Assuming there are three lines as mentioned
        current_line = -1
        for station in stations:
            if '号线' in station:
                current_line += 1
            elif station.strip() != '':
                lines[current_line].append(station.strip())

            # print(node)
        for i in stations[1:17]:
                self.add_node(i)
        for i in stations[19:43]:
                self.add_node(i)
        for i in stations[45:]:
                self.add_node(i)

        return lines


    def add_edges_with_random_weights(self,stations):
        for line in stations:
            for i in range(len(line) - 1):
                weight = random.randint(1, 20)  # Random weight between 1 and 20
                self.add_edge(line[i], weight, line[i + 1])




    def Dijkstra(self, start):
        distance = {}
        for key in self.nodes.keys():
            distance[key] = float('inf')
        distance[start] = 0
        visited = []
        unvisited = list(self.nodes.keys())
        while unvisited:
            min_node = None
            for node in unvisited:
                if min_node is None:
                    min_node = node
                elif distance[node] < distance[min_node]:
                    min_node = node
            for node, weight in self.nodes[min_node].adjacent.items():
                if node not in visited:
                    new_distance = distance[min_node] + weight
                    if new_distance < distance[node]:
                        distance[node] = new_distance
            visited.append(min_node)
            unvisited.remove(min_node)
        return distance
    
    def find_shortest_path(self, start, end):
        distance = self.Dijkstra(start)
        path = [end]
        while end != start:
            for node, weight in self.nodes[end].adjacent.items():
                if distance[node] + weight == distance[end]:
                    path.append(node)
                    end = node
        return path[::-1], distance[path[0]]
    



# if __name__ == "__main__":
#     g = Graph()
#     # g.save_to_json("graph.json")
#     g.load_from_json("graph.json")
#     g.print_graph()
#     print(g.Dijkstra("西塱"))
#     print(g.find_shortest_path("西塱","梅花园"))



