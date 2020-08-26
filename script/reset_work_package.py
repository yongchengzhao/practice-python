# coding: utf-8
# Python 3

import json
from datetime import datetime
import requests
from .batch_archive import show_and_save_msg, time_str

sjc_ip_port = '10.215.160.41:6543'
# sjc_ip_port = '10.218.8.32:8000'

global_unit_list, global_segment_list, global_discipline_list, global_wp_list = [], [], [], []
global_unit_id_list, global_segment_id_list, global_discipline_id_list, global_wp_id_list = [], [], [], []
cannot_get_wp_info_id_list, need_reset_wp_id_list = [], []
reset_wp_error_id_list = []


def get_about_unit_info():

    print(f'{datetime.now()}: reset_work_package()')
    unit_id_dict = {}

    get_unit_segment_id(unit_id_dict)  # 获取单位工程和分部工程 id

    get_discipline_id(unit_id_dict)  # 获取分项工程 id

    get_unit_id(unit_id_dict)  # 获取单元工程 id

    # print(f'len(global_unit_list): {len(global_unit_list)}, global_unit_list: {global_unit_list}')
    # print(f'len(global_segment_list): {len(global_segment_list)}, global_segment_list: {global_segment_list}')
    # print(f'len(global_discipline_list): {len(global_discipline_list)}, global_discipline_list: {global_discipline_list}')
    # print(f'len(global_wp_list): {len(global_wp_list)}, global_wp_list: {global_wp_list}')

    msg = f'''unit_id_dict: len: {len(unit_id_dict)}, content: {json.dumps(unit_id_dict)}
global_unit_id_list: len: {len(global_unit_id_list)}, content: {global_unit_id_list}
global_segment_id_list: len: {len(global_segment_id_list)}, content: {global_segment_id_list}
global_discipline_id_list: len: {len(global_discipline_id_list)}, content: {global_discipline_id_list}
global_wp_id_list: len: {len(global_wp_id_list)}, content: {global_wp_id_list}'''
    show_and_save_msg(msg=msg, file_name=f'{time_str}-unit_pk.log')


def get_unit_segment_id(unit_id_dict):
    url = f'http://{sjc_ip_port}/api/wpunitlist/?t=1595129570585&children=true&all=true'
    res = requests.get(url=url)

    if res.status_code != 200:
        print(f'get_unit_segment_id() error, res.status_code is {res.status_code}')
        return unit_id_dict

    unit_list = json.loads(res.content).get('result', [])
    # print(unit_list)

    for unit in unit_list:
        unit_id = unit.get('pk')
        # print(f'unit_id: {unit_id}, type: {type(unit_id)}')
        if not unit_id or not isinstance(unit_id, str):
            continue

        unit_id_dict[unit_id] = {}

        global_unit_list.append(unit)
        global_unit_id_list.append(unit_id)

        segment_list = unit.get('children_wp')
        if not segment_list or not isinstance(segment_list, list):
            continue

        for segment in segment_list:
            segment_id = segment.get('pk')
            if not segment_id or not isinstance(segment_id, str):
                continue

            unit_id_dict[unit_id][segment_id] = {}

            global_segment_list.append(segment)
            global_segment_id_list.append(segment_id)

    return unit_id_dict


def get_discipline_id(unit_id_dict: dict):
    for unit_id, segment_id_dict in unit_id_dict.items():
        for segment_id, discipline_id_dict in segment_id_dict.items():
            url = f'http://{sjc_ip_port}/api/workpackages/{segment_id}/?children=true&t=1595129742597'
            res = requests.get(url=url)
            segment = json.loads(res.content)

            discipline_list = segment.get('children_wp')
            if not discipline_list or not isinstance(discipline_list, list):
                continue

            for discipline in discipline_list:
                discipline_id = discipline.get('pk')
                if not discipline_id or not isinstance(discipline_id, str):
                    continue

                discipline_id_dict[discipline_id] = {}

                global_discipline_list.append(discipline)
                global_discipline_id_list.append(discipline_id)
                print(f'discipline_id: {discipline_id}, counter: {len(global_discipline_id_list)}')


def get_unit_id(unit_id_dict: dict):
    for unit_id, segment_id_dict in unit_id_dict.items():
        for segment_id, discipline_id_dict in segment_id_dict.items():
            # wp_id_dict 是 work_package_id_dict，即施工包单元 id
            for discipline_id, wp_id_dict in discipline_id_dict.items():
                url = f'http://{sjc_ip_port}/api/workpackages/{discipline_id}/?children=true&t=1595129742597'
                res = requests.get(url=url)
                discipline = json.loads(res.content)

                wp_list = discipline.get('children_wp')
                if not wp_list or not isinstance(wp_list, list):
                    continue

                for wp in wp_list:
                    wp_id = wp.get('pk')
                    if not wp_id or not isinstance(wp_id, str):
                        continue

                    wp_id_dict[wp_id] = wp.get('code')

                    global_wp_list.append(wp)
                    global_wp_id_list.append(wp_id)
                    print(f'wp_id: {wp_id}, counter: {len(global_wp_id_list)}')


def reset_wp_info(wp_id_list):
    """
    重置单元工程（施工包）信息。
    :param wp_id_list:
    :return:
    """
    reset_wp_info_by_id_list(wp_id_list)


def reset_wp_info_by_id_list(wp_id_list):
    """
    根据提供的施工包 id 列表重置单元工程信息。
    :param wp_id_list:
    :return:
    """
    for wp_id in wp_id_list:

        is_need_reset, archives_state, transfer_state = wp_is_need_reset(wp_id)
        print(f'wp_id: {wp_id}, is_need_reset: {is_need_reset}, archives_state: {archives_state}, '
              f'transfer_state: {transfer_state}, {wp_id_list.index(wp_id)}/{len(wp_id_list)}: '
              f'{round(wp_id_list.index(wp_id)/len(wp_id_list)*100, 2)}%')

        if is_need_reset:
            need_reset_wp_id_list.append(wp_id)
            # reset_wp_info_by_id(wp_id)

    print(f'cannot_get_wp_info_id_list: {cannot_get_wp_info_id_list}')
    print(f'need_reset_wp_id_list: {need_reset_wp_id_list}')
    print(f'reset_wp_error_id_list: {reset_wp_error_id_list}')


def wp_is_need_reset(wp_id: str) -> tuple:
    """
    判断是否需要重置。
    :param wp_id:
    :return:
    """
    # 加上 all=true 会把 parent 和 qic_documents 也序列化出来，此处这两个不用获取。
    # url = f'http://{sjc_ip_port}/api/workpackages/{wp_id}/?all=true'
    url = f'http://{sjc_ip_port}/api/workpackages/{wp_id}/'
    res = requests.get(url=url)

    if res.status_code != 200:
        cannot_get_wp_info_id_list.append(wp_id)
        print(f'is_need_reset error, wp_id: {wp_id}, res.status: {res.status_code}')
        return False, None, None

    wp_info = json.loads(res.content)

    archives_state = wp_info.get('extra_params', {}).get('archives_state')
    transfer_state = wp_info.get('extra_params', {}).get('transfer_state')
    if (archives_state is not None and archives_state != 0) or (transfer_state is not None and transfer_state != 0):
        return True, archives_state, transfer_state

    return False, None, None


def reset_wp_info_by_id(wp_id):
    """
    根据提供的施工包 id 重置单元工程信息。
    :param wp_id:
    :return:
    """
    url = f'http://{sjc_ip_port}/api/workpackages/{wp_id}/'
    patch_data = {'extra_params': {
        'archives_state': 0,
        'archives_time': "",
        'transfer_state': 0,
        'transfer_time': "",
        'four_features_detection': ""
    }}
    headers = {'content-type': 'application/json'}

    res = requests.patch(url=url, data=json.dumps(patch_data).encode('utf-8'), headers=headers)
    if res.status_code != 200:
        reset_wp_error_id_list.append(wp_id)
        print(f'reset_wp_info_by_id error, wp_id: {wp_id}, res.status_code: {res.status_code}')


def get_wp_info_by_id(wp_id):
    """
    根据施工包 id 获取施工包信息。
    :param wp_id:
    :return:
    """
    url = f'http://{sjc_ip_port}/api/workpackages/{wp_id}/'
    res = requests.get(url=url)

    if res.status_code != 200:
        return {}

    wp = json.loads(res.content.decode('utf-8'))
    return wp


def check_wp_info(wp_id_list):
    """
    检查施工包信息。
    :param wp_id_list:
    :return:
    """
    for wp_id in wp_id_list:
        wp_info = get_wp_info_by_id(wp_id)

        archives_state = wp_info.get('extra_params', {}).get('archives_state')
        archives_time = wp_info.get('extra_params', {}).get('archives_time')
        transfer_state = wp_info.get('extra_params', {}).get('transfer_state')
        transfer_time = wp_info.get('extra_params', {}).get('transfer_time')
        print(f'archives_state: {archives_state}, archives_time: {archives_time}, transfer_state: {transfer_state}, '
              f'transfer_time: {transfer_time}, {wp_id_list.index(wp_id)}/{len(wp_id_list)}: '
              f'{round(wp_id_list.index(wp_id)/len(wp_id_list)*100, 2)}%')


if __name__ == '__main__':
    print(f'{datetime.now()}: ----------main----------')

    # get_about_unit_info()
    #
    # wp_id_list_ = []
    # reset_wp_info(wp_id_list_)
    #
    # check_wp_info(wp_id_list_)
