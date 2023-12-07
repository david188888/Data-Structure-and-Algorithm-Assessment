from pywebio.input import *
from pywebio.output import *

from graph import Map




def get_station_name():
    stations = []
    with open("./graph/station.txt", "r+",encoding="utf-8") as f:
        station_read = f.readlines()
        for i in station_read:
            if '号线' in i:
                pass
            elif i.strip() != '':
                stations.append(i.strip())
    return stations


def get_station_mapping():
    with open("./graph/station.txt", "r+",encoding="utf-8") as f:
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
            current_line = lines_at_station[0:3] if lines_at_station else '未知线路'
            # 将线路转换信息添加到grouped_path
            grouped_path.append({'line_change': current_line, 'stations': [station]})
        else:
            # 如果没有发生线路转换，继续添加站台到当前线路的分组中
            grouped_path[-1]['stations'].append(station)

    return grouped_path


def generate_table_data(grouped_path):
    table_data = []
    headers = []
    for lines in grouped_path:
        line = lines['line_change']
        stations = lines['stations']
        headers.append(line)
        row = []
        for station in stations:
            row.append(station)
        table_data.append(row)
    return table_data, headers



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



def main(grouped_path,mapping_dict):
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
        put_html("您选择的起点站是：<b><span style='font-size:20px;' >%s</span></b> , 终点站是：<b><span style='font-size:20px;'>%s</span></b>" % (start, end)).style('margin-top: 10px;')
    g = Map.Graph()
    g.load_from_json("./graph/graph.json")

    path, distance = g.find_shortest_path(start, end)

    use_scope('wait', clear=True)
    grouped_path = group_stations_by_line(path, mapping_dict)
    put_markdown("## 最短路线为：")
    put_html(create_station_table(grouped_path))

    put_html("最短路线长度为: <b><span style='font-size:20px;'>%s</span></b> km" % distance).style('position: absolute; left: 50%; transform: translateX(-50%);')


if __name__ == '__main__':
    mapping_dict = get_station_mapping()
    station_path = get_station_name()
    grouped_path = group_stations_by_line(station_path, mapping_dict)
    # print(grouped_path)
    # print(generate_table_data(grouped_path))
    main(grouped_path,mapping_dict)

