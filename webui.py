from pywebio.input import *
from pywebio.output import *
from pywebio.session import hold
from graph import Map
from graph.Map import *


def get_station_name():
    stations = []
    with open("./graph/station.txt", "r+", encoding="utf-8") as f:
        station_read = f.readlines()
        for i in station_read:
            if '号线' in i:
                pass
            elif i.strip() != '':
                stations.append(i.strip())
    return stations


def get_station_mapping():
    with open("./graph/station.txt", "r+", encoding="utf-8") as f:
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


def group_stations_by_line(stations, station_line_map):
    # 存储分组后的站台和线路转换信息
    grouped_path = []
    current_line = None

    for station in stations:
        lines_at_station = station_line_map.get(station)

        # 如果当前线路不在该站的线路列表中，说明发生了线路转换
        if not current_line or current_line not in lines_at_station:
            current_line = lines_at_station[0:
                                            3] if lines_at_station else '未知线路'
            # 将线路转换信息添加到grouped_path
            grouped_path.append(
                {'line_change': current_line, 'stations': [station]})
        else:
            # 如果没有发生线路转换，继续添加站台到当前线路的分组中
            grouped_path[-1]['stations'].append(station)

    return grouped_path


def create_station_table(grouped_path):
    html_content = "<div style='white-space: nowrap;'>"
    for i, segment in enumerate(grouped_path):
        line_name = segment['line_change']
        stations = segment['stations']

        # Add the line name header
        html_content += f"<div><strong>{line_name}</strong></div><table><tr>"

        # Add stations for this line
        for station in stations:
            html_content += f"<td>{station}</td>"
            if station != stations[-1]:  # If it's not the last station, add an arrow
                html_content += "<td>➡️</td>"

        # Close the current line table
        html_content += "</tr></table>"

        # If it's not the last segment, add a downward arrow to indicate a line change
        if i < len(grouped_path) - 1:
            html_content += "<td>⬇️</td>"
        # Close the outer div
        html_content += "</div>"

    return html_content


def crate_show_path(start, end, g):
    def show_path(path_type):
        shortest_distance_path, distance = g.find_shortest_path(start, end)
        least_station_path, length = g.find_least_station_path(start, end)
        least_transfer_path = g.find_least_transfer_path(start, end)
        if path_type == '最少站点数':
            less_path = least_station_path
            path = group_stations_by_line(less_path, mapping_dict)
        elif path_type == '最短距离':
            short_path = shortest_distance_path
            path = group_stations_by_line(short_path, mapping_dict)
        else:
            timeless_path = least_transfer_path
            path = group_stations_by_line(timeless_path, mapping_dict)

        with use_scope('wait', clear=True):
            put_markdown("## %s路线为:" % path_type)
            if path_type == '最短距离':
                put_html(create_station_table(path))
                put_html("最短路线长度为: <b><span style='font-size:20px;'>%s</span></b> km" %
                         distance).style('position: absolute; left: 50%; transform: translateX(-50%);')
            elif path_type == '最少站点数':
                put_html(create_station_table(path))
                put_html("最少站点数为: <b><span style='font-size:20px;'>%s</span></b> 站" %
                         length).style('position: absolute; left: 50%; transform: translateX(-50%);')
            else:

                put_html(create_station_table(path))
    return show_path


def main():
    put_markdown("# 乘车路线查询")
    with use_scope('first'):
        put_text("请选择起点和终点站：").style('margin-top: 10%;,font-size:20px;')
    img = open('map.jpg', 'rb').read()
    put_image(img, width='auto', height='auto').style('position: center;')

    inputs = input_group("选择起点和终点", [
        select("起点", options=get_station_name(), name='start'),
        select("终点", options=get_station_name(), name='end')
    ])

    start = inputs['start']
    end = inputs['end']

    with use_scope('first', clear=True):
        put_html("您选择的起点站是：<b><span style='font-size:20px;' >%s</span></b> , 终点站是：<b><span style='font-size:20px;'>%s</span></b>" %
                 (start, end)).style('margin-top: 10px;')
    g = Map.Graph()
    g.load_from_json("./graph/graph.json")
    use_scope('wait', clear=True)
    put_buttons(['最短距离', '最少站点数', '最少换乘'], onclick=crate_show_path(start, end, g)).style(
        'position: absolute; left: 50%; transform: translateX(-50%);')
    hold()


if __name__ == '__main__':
    mapping_dict = get_station_mapping()
    station_path = get_station_name()
    grouped_path = group_stations_by_line(station_path, mapping_dict)
    # print(grouped_path)
    main()
