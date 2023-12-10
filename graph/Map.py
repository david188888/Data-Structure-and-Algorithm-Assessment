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
    def __init__(self, value):
        self.value = value
        self.adjacent = {}  # list of adjacent nodes

    def add_adjacent(self, node, weight):
        self.adjacent[node.value] = weight


class Graph():
    def __init__(self):
        self.nodes = {}  # dictionary of nodes

    def add_node(self, value):
        if value not in self.nodes:
            self.nodes[value] = Node(value)

    def add_edge(self, value1, weight, value2):
        if value1 in self.nodes and value2 in self.nodes:
            self.nodes[value1].add_adjacent(self.nodes[value2], weight)
            self.nodes[value2].add_adjacent(self.nodes[value1], weight)
        else:
            print("Error: Node not found")

    def delete_edge(self, value1, value2):
        if value1 in self.nodes and value2 in self.nodes:
            if value2 in self.nodes[value1].adjacent:
                del self.nodes[value1].adjacent[value2]
            if value1 in self.nodes[value2].adjacent:
                del self.nodes[value2].adjacent[value1]
        else:
            print("Error: Node not found")

    def length(self):
        return len(self.nodes)

    def print_graph(self):
        for key in list(self.nodes.keys()):
            print(key, " --> ", end=" ")
            for node, weight in self.nodes[key].adjacent.items():
                print(node, "(", weight, ")", end=" | ")
            print()

    def save_to_json(self, filepath):
        graph_data = {}
        for key, node in self.nodes.items():
            graph_data[key] = node.adjacent
        with open(filepath, 'w') as f:
            json.dump(graph_data, f, indent=4)

    def load_from_json(self, filepath):
        with open(filepath, 'r') as f:
            graph_data = json.load(f)
            self.nodes.clear()
        for key, adjacent in graph_data.items():
            self.add_node(key)
            for node, weight in adjacent.items():
                self.add_node(node)
                self.nodes[key].add_adjacent(self.nodes[node], weight)

    def save_node(self):
        with open("graph/station.txt", "r+", encoding="utf-8") as f:
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
        for i in stations[1:16]:
            self.add_node(i)
        for i in stations[18:41]:
            self.add_node(i)
        for i in stations[43:]:
            self.add_node(i)

        return lines

    def add_edges_with_random_weights(self, stations):
        for line in stations:
            for i in range(len(line) - 1):
                # Random weight between 1 and 20
                weight = random.randint(1, 20)
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

    def get_station_mapping(self):
        with open("graph/station.txt", "r+", encoding="utf-8") as f:
            station_read = f.readlines()
            lines = [[], [], []]  # Assuming there are three lines as mentioned
            current_line = -1
            for station in station_read:
                if '号线' in station:
                    current_line += 1
                elif station.strip() != '':
                    lines[current_line].append(station.strip())
            # print(lines)
            dist = {}
            for i in lines[0]:
                dist[i] = "一号线"
            for i in lines[1]:
                if dist.get(i):
                    dist[i] = "[一号线,二号线]"
                else:
                    dist[i] = "二号线"

            for i in lines[2]:
                if dist.get(i):
                    if "二号线" in dist[i]:
                        dist[i] = "[二号线,三号线]"
                    else:
                        dist[i] = "[一号线,三号线]"
                else:
                    dist[i] = "三号线"

            return dist

    def group_stations_by_line(self, stations, station_line_map):
        # 存储分组后的站台和线路转换信息
        grouped_path = []
        current_line = None
        for i in stations:
            for station in i:
                lines_at_station = station_line_map.get(station)
                # 如果当前线路不在该站的线路列表中，说明发生了线路转换
                if not current_line or current_line not in lines_at_station:
                    current_line = lines_at_station[0:
                                                    4] if lines_at_station else '未知线路'
                    # 将线路转换信息添加到grouped_path
                    grouped_path.append(
                        {'line_change': current_line, 'stations': [station]})
                else:
                    # 如果没有发生线路转换，继续添加站台到当前线路的分组中
                    grouped_path[-1]['stations'].append(station)

        return grouped_path

    def find_all_paths(self, start, end, path=[]):
        path = path + [start]
        if start == end:
            return [path]
        paths = []
        for node in self.nodes[start].adjacent.keys():
            if node not in path:
                new_paths = self.find_all_paths(node, end, path)
                for new_path in new_paths:
                    paths.append(new_path)
        return paths

    def find_least_station_path(self, start, end):
        paths = self.find_all_paths(start, end)
        least_station_path = paths[0]
        for path in paths:
            if len(path) < len(least_station_path):
                least_station_path = path
        length = len(least_station_path)
        return least_station_path, length

    def find_least_transfer_path(self, start, end):
        paths = self.find_all_paths(start, end)
        all_transfer_path = self.group_stations_by_line(
            paths, self.get_station_mapping())
        # print(all_transfer_path)
        result = []
        way = []
        for path in all_transfer_path:
            way.append(path)
            if end in path["stations"]:
                result.append(way)
                way = []
        result = sorted(result, key=lambda x: len(x))[:2]
        if len(result[0]) == len(result[-1]):
            len0 = len(result[0][0]["stations"]) + \
                len(result[0][1]["stations"])
            len1 = len(result[1][0]["stations"]) + \
                len(result[1][1]["stations"])
            if len0 < len1:
                merged_stations = []
                [merged_stations.extend(item["stations"])
                 for item in result[0]]
                return merged_stations
            else:
                merged_stations = []
                [merged_stations.extend(item["stations"])
                 for item in result[1]]
                return merged_stations
        else:
            merged_stations = []
            [merged_stations.extend(item["stations"]) for item in result[1]]
            return merged_stations


if __name__ == "__main__":
    g = Graph()
    # g.save_node()
    # g.add_edges_with_random_weights(g.save_node())
    # g.delete_edge("天河客运站","林和西")
    # g.add_edge("体育西路", 5, "林和西")
    # g.save_to_json("graph/graph.json")
    g.load_from_json("graph/graph.json")
    # g.print_graph()
    # print(g.Dijkstra("西塱"))
    # print(g.find_shortest_path("西塱","梅花园"))
    # print(g.find_all_paths("机场南","西塱"))
    # print(g.get_station_mapping())
    # print(g.find_least_station_path("机场南","西塱"))
    # g.find_least_transfer_path("机场南","西塱")
    # print(f"最短线路：{g.find_shortest_path('机场南', '西塱')}\n")
    # print(f"最少站点：{g.find_least_station_path('机场南', '西塱')}\n")
    print(f"最少换乘：{g.find_least_transfer_path('机场南', '西塱')}\n")
