# coding: utf-8
# Python 3

import json
import os
from datetime import datetime, timedelta
import requests

archive_ip_port = '10.215.160.41:8000'
sjc_ip_port = '10.215.160.41:6543'
# archive_ip_port = '10.218.8.34:8989'
# sjc_ip_port = '10.218.8.32:8000'
creator_username = 'wang_yt'

time_str = datetime.now().strftime('%Y-%m-%dT%H-%M-%S')

cannot_get_wp_info_pk_list = []
get_wp_info_by_code_error_code_list = []
already_archived_wp_code_list = []
assemble_request_data_error_wp_code_list = []
archive_error_wp_code_list = []
ftp_failed_wp_code_list = []
summary_failed_wp_code_list = []
success_wp_code_list = []


def batch_archive(wp_code_list: list):
    """
    根据施工包编码列表批量组件。
    :param wp_code_list:
    :return:
    """
    for wp_code in wp_code_list:
        wp_info = get_wp_info_by_pk(wp_code, 'code')
        if not wp_info:
            get_wp_info_by_code_error_code_list.append(wp_code)
            continue

        # 检测是否已经组件或者提交过，如果已组件或者已提交，则 continue
        is_archived = is_wp_archived(wp_info)
        if is_archived:
            already_archived_wp_code_list.append(wp_code)
            continue

        request_data = assemble_request_data_by_wp_info(wp_info)
        if not request_data:
            assemble_request_data_error_wp_code_list.append(wp_code)
            continue

        # 这里组件
        archive_info = perform_archive(request_data)
        if not archive_info:
            archive_error_wp_code_list.append(wp_code)
            continue

        # 这里推送归档包
        ftp_result = transfer_ftp(archive_info)
        if ftp_result is False:
            ftp_failed_wp_code_list.append(wp_code)
            continue

        # 这里传输概要信息
        summary_result = transfer_summary_info(archive_info)
        if summary_result is False:
            summary_failed_wp_code_list.append(wp_code)
            continue

        success_wp_code_list.append(wp_code)

    log_result()


def show_and_save_msg(msg='', file_name='', flush=True):
    """
    打印信息到屏幕和文件中。
    :param msg:
    :param file_name:
    :param flush:
    :return:
    """
    print(msg)
    if file_name:
        print(msg, file=open(f'{file_name}', mode='a'), flush=flush)


def log_result():
    """
    记录结果。
    :return:
    """
    msg = f'''get_wp_info_by_code_error_code_list: len: {len(get_wp_info_by_code_error_code_list)}, content: {get_wp_info_by_code_error_code_list}
already_archived_wp_code_list: len: {len(already_archived_wp_code_list)}, content: {already_archived_wp_code_list}
assemble_request_data_error_wp_code_list: len: {len(assemble_request_data_error_wp_code_list)}, content: {assemble_request_data_error_wp_code_list}
archive_error_wp_code_list: len: {len(archive_error_wp_code_list)}, content: {archive_error_wp_code_list}
ftp_failed_wp_code_list: len: {len(ftp_failed_wp_code_list)}, content: {ftp_failed_wp_code_list}
summary_failed_wp_code_list: len: {len(summary_failed_wp_code_list)}, content: {summary_failed_wp_code_list}
success_wp_code_list: len: {len(success_wp_code_list)}, content: {success_wp_code_list}
'''
    show_and_save_msg(msg=msg, file_name=f'{time_str}-result.log')


def transfer_summary_info(archive_info: dict) -> bool:
    """
    传输概要信息到紫光。
    :param archive_info:
    :return:
    """
    archive_id = archive_info.get('id')
    url = f'http://{archive_ip_port}/main/api/transfer-summary/'
    headers = {'content-type': 'application/json'}
    data = {'id_list': [archive_id]}
    res = requests.post(url=url, data=json.dumps(data), headers=headers)

    if res.status_code != 200:
        return False

    result_list = json.loads(res.content.decode('utf-8'))
    for result in result_list:
        if not isinstance(result, dict):
            return False

        if not result.get('res.content') or not isinstance(result.get('res.content'), str):
            return False

        if "value='true'" in result.get('res.content'):
            return True

        return False

    return False


def transfer_ftp(archive_info: dict) -> bool:
    """
    通过 FTP 传输归档包到紫光。
    :param archive_info:
    :return:
    """
    archive_id = archive_info.get('id')
    url = f'http://{archive_ip_port}/main/api/transfer-ftp/'
    headers = {'content-type': 'application/json'}
    data = {'id_list': [archive_id]}
    res = requests.post(url=url, data=json.dumps(data), headers=headers)

    if res.status_code != 200:
        return False

    result_list = json.loads(res.content.decode('utf-8'))
    for result in result_list:
        if result.get('result', '') == 'success':
            return True
        return False

    return False


def perform_archive(request_data: dict) -> dict:
    """
    执行组件动作。
    :param request_data:
    :return:
    """
    url = f'http://{archive_ip_port}/main/api/archives/'
    headers = {'content-type': 'application/json'}
    res = requests.post(url=url, data=json.dumps(request_data), headers=headers)

    if res.status_code != 201:
        return {}

    try:
        archive_info = json.loads(res.content.decode('utf-8'))
    except (json.decoder.JSONDecodeError, TypeError) as e:
        msg = f'perform_archive error, exception: {e}'
        show_and_save_msg(msg, f'{time_str}-perform_archive.log')
        return {}

    return archive_info


def is_wp_archived(wp_info: dict) -> bool:
    """
    组件前检查组件状态，如果已经组件过或者提交过返回 True。
    :param wp_info:
    :return:
    """
    extra_params = wp_info.get('extra_params', {})
    archives_state = extra_params.get('archives_state')
    transfer_state = extra_params.get('transfer_state')

    if archives_state == 2 or transfer_state == 1:
        return True

    return False


def assemble_request_data_by_wp_info(wp_info: dict) -> dict:
    """
    根据施工包信息组装请求参数。
    :param wp_info:
    :return:
    """
    data = {}

    wp_code = wp_info.get('code')
    if not wp_code:
        return {}

    segment_code = '-'.join(wp_code.split('-')[:2])
    segment_info = get_wp_info_by_pk(segment_code, 'code')
    if not segment_info:
        return {}

    form_list, msg = get_form_list(wp_info)
    if form_list is False:
        msg = f'get_form_list error, wp_code: {wp_code}, ' + msg
        show_and_save_msg(msg, f'{time_str}-assemble_request_data_by_wp_info.log')
        return {}

    unit_type = get_unit_type(wp_info)
    if not unit_type:
        msg = f'get_unit_type error, wp_code: {wp_code}'
        show_and_save_msg(msg, f'{time_str}-assemble_request_data_by_wp_info.log')
        return {}

    extra_params = wp_info.get('extra_params', {})
    pass_percent, msg = process_pass_percent(extra_params.get('qr_count', {}).get('percent'))
    if pass_percent is False:
        msg = f'process_pass_percent error, wp_code: {wp_code}, msg: {msg}'
        show_and_save_msg(msg, f'{time_str}-assemble_request_data_by_wp_info.log')
        return {}

    unit_name = segment_info.get('parent', {}).get('name')
    segment_name = segment_info.get('name', '')
    discipline_name = wp_info.get('parent', {}).get('name')
    wp_name = wp_info.get('name', '')

    station_scope = extra_params.get('桩号范围') if '现场' not in extra_params.get('桩号范围') else ''
    elevation_scope = extra_params.get('高程') if '现场' not in extra_params.get('高程') else ''
    construction_start = slice_date_str_from_datetime_str(wp_info.get('tech_parmas', {}).get('actual_process', {}).get('start_time', ''))
    construction_end = slice_date_str_from_datetime_str(wp_info.get('tech_parmas', {}).get('actual_process', {}).get('end_time', ''))

    quality_level = {None: None, '不合格': 0, '合格': 1, '优良': 2}.get(extra_params.get('qr_count', {}).get('grade'))
    data_from = f'雅砻江杨房沟水电站设计施工BIM管理系统'
    static_files = get_static_file_list(wp_info)

    data['name'] = f'雅砻江杨房沟水电站{unit_name}{elevation_scope}{segment_name}{discipline_name}{wp_name}'
    data['unit'] = unit_name
    data['segment'] = segment_name
    data['discipline'] = discipline_name
    data['unit_project'] = f'{wp_code} {wp_name}'
    data['station_scope'] = station_scope
    data['elevation_scope'] = elevation_scope
    data['construction_start'] = construction_start
    data['construction_end'] = construction_end
    data['pass_percent'] = pass_percent
    data['quality_level'] = quality_level
    data['data_from'] = data_from
    data['static_files'] = static_files
    data['forms'] = form_list
    data['creator_username'] = creator_username
    data['unit_type'] = unit_type
    data['work_package_code'] = wp_code
    data['unit_engineering_code'] = wp_code

    msg = f'"{wp_code}": {json.dumps(data).encode("utf-8").decode("unicode_escape")},'
    show_and_save_msg(msg)
    return data


def get_unit_type(wp_info: dict) -> str:
    """
    从施工包信息中提取单元工程类型。
    :param wp_info:
    :return:
    """
    unit_type = ''

    form_list = wp_info.get('qic_documents', [])
    if not form_list:
        return ''

    form = form_list[0]
    attributes = form.get('attributes', '{}')
    try:
        attributes = json.loads(attributes)
    except json.decoder.JSONDecodeError:
        return ''

    # serial_code 的格式为 Z01-05-02-0002-KL01
    serial_code = attributes.get('basic', {}).get('serial_code')
    if not serial_code or len(serial_code.split('-')) < 5 or len(serial_code.split('-')[4]) < 1:
        return ''

    unit_type_pre = serial_code.split('-')[4][0]
    unit_type_dict = {'K': 'kwgc', 'M': 'mpzhgc', 'Y': 'yylmgms', 'H': 'hntgc', 'J': 'jdgc'}
    unit_type = unit_type_dict.get(unit_type_pre, '')
    return unit_type


def get_form_list(wp_info: dict):
    """
    从施工包信息中获取表单列表。
    :param wp_info:
    :return:
    """
    form_list, pdf_file_name_dict = [], {}
    wp_code = wp_info.get('code')

    for raw_form in wp_info.get('qic_documents', []):
        form_id = raw_form.get('pk')
        if not form_id:
            continue

        form = {'id': form_id}

        form_name = raw_form.get('name', '')
        pdf_file_name = f'{wp_code}-{form_name}'
        form['pdf_file_name'] = pdf_file_name
        if pdf_file_name in pdf_file_name_dict.keys():
            form['pdf_file_name'] = f'{pdf_file_name}({pdf_file_name_dict.get(pdf_file_name)})'

        form['files'] = []
        attributes = raw_form.get('attributes', '{}')
        try:
            attributes = json.loads(attributes)
        except json.decoder.JSONDecodeError:
            return False, f'form_id: {form_id}'

        form_static_file_list = attributes.get('extra', {}).get('detail', {}).get('tableAttachments', [])
        for form_static_file in form_static_file_list:
            static_file_id = form_static_file.get('response', {}).get('id')
            if not static_file_id:
                continue

            static_file_name = f"{form['pdf_file_name']}-附件"

            form['files'].append({'id': static_file_id, 'name': static_file_name})

        form_list.append(form)
        pdf_file_name_dict[pdf_file_name] = pdf_file_name_dict.get(pdf_file_name, 0) + 1

    return form_list, ''


def get_static_file_list(wp_info: dict) -> list:
    """
    从施工包信息中获取静态文件列表。
    :param wp_info:
    :return:
    """
    static_file_list = []

    # 1. 从 wp_info.tech_parmas 中获取静态文件
    tech_file_list_list = wp_info.get('tech_parmas', {}).get('info', {}).get('fileList', [])
    for tech_file_list in tech_file_list_list:
        if not tech_file_list:
            continue

        tech_file_type = ['', '检验资料', '监测资料', '测量资料'][tech_file_list_list.index(tech_file_list)]
        for tech_file in tech_file_list:
            tech_file_id = tech_file.get('response', {}).get('id')
            if not tech_file_id:
                continue

            # tech_file.get('name', '') 的格式为 左岸拱肩槽1-2评定附表.pdf
            tech_file_name = os.path.splitext(os.path.basename(tech_file.get('name', '')))[0]
            if not tech_file_name:
                tech_file_name = tech_file.get('response', {}).get('name', 'undefined')

            static_file_list.append({'id': tech_file_id, 'name': f'{tech_file_type}-{tech_file_name}'})

    # 2. 从 wp_info.extra_params.video_upload 中获取静态文件
    video_file_list = wp_info.get('extra_params', {}).get('video_upload', [])
    for video_file in video_file_list:
        video_file_id = video_file.get('file', {}).get('id')
        if not video_file_id:
            continue

        video_file_name = video_file.get('gxms', 'undefined')
        static_file_list.append({'id': video_file_id, 'name': f'{video_file_name}'})

    # 3. 从 wp_info.extra_params.static_files 中获取静态文件
    extra_static_file_list = wp_info.get('extra_params', {}).get('static_files', [])
    for extra_static_file in extra_static_file_list:
        extra_static_file_id = extra_static_file.get('file', {}).get('id')
        if not extra_static_file_id:
            continue

        extra_static_file_name = os.path.splitext(os.path.basename(extra_static_file.get('file', {}).get('name', 'undefined')))[0]
        static_file_list.append({'id': extra_static_file_id, 'name': f'{extra_static_file_name}'})

    return static_file_list


def process_pass_percent(raw_pass_percent):
    """
    处理合格率。如果为 None，返回 None；如果不能解析成 float，报错；如果可以解析成 float，返回两位小数的 float 值。
    :param raw_pass_percent:
    :return:
    """
    if raw_pass_percent is None:
        return raw_pass_percent, ''

    try:
        raw_pass_percent = float(raw_pass_percent)
        return round(raw_pass_percent, 2), ''
    except ValueError:
        return False, raw_pass_percent


def slice_date_str_from_datetime_str(datetime_str: str) -> str:
    """
    根据日期时间字符串获取日期字符串，如果日期时间字符串为空字符串或不满 10 位则返回空字符串。返回的日期字符串格式为 YYYY-mm-dd。
    :param datetime_str:
    :return:
    """
    if not datetime_str or not isinstance(datetime_str, str) or len(datetime_str) < 19:
        return ''
    datetime_str = datetime_str[:19]  # 2017-12-30T16:00:00.000Z
    date_str = (datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S') + timedelta(hours=8)).strftime('%Y-%m-%d')
    return date_str


def get_wp_info_by_pk(pk: str, pk_type: str) -> dict:
    """
    通过施工包编码获取施工包信息。
    @param pk:
    @param pk_type:
    """
    if not pk.strip():
        return {}

    if pk_type == 'code':
        url = f'http://{sjc_ip_port}/api/workpackages/code/{pk}/?all=true'
    elif pk_type == 'id':
        url = f'http://{sjc_ip_port}/api/workpackages/{pk}/'
    else:
        return {}

    res = requests.get(url=url)

    # 记录无法根据施工包 code 获取到施工包信息的情况
    if res.status_code != 200:
        cannot_get_wp_info_pk_list.append(pk)
        msg = f'get_wp_info_by_id error, wp_id: {pk}, res.status_code: {res.status_code}, res.content: {res.content}'
        show_and_save_msg(msg=msg, file_name=f'{time_str}-cannot_get_wp_info_id_list.log')
        return {}

    wp_info = json.loads(res.content.decode('utf-8'))
    return wp_info


def count_wp_by_is_completed(wp_id_list: list):
    """
    通过 id 列表以 is_completed 为依据统计施工包。
    :param wp_id_list:
    :return:
    """
    is_completed_0, is_completed_1, is_completed_2, is_completed_3, is_completed_4, is_completed_5, is_completed_6 =\
        [], [], [], [], [], [], []
    is_completed_result_list = [is_completed_0, is_completed_1, is_completed_2, is_completed_3, is_completed_4,
                                is_completed_5, is_completed_6]

    for wp_id in wp_id_list:
        wp_info = get_wp_info_by_pk(wp_id, 'id')
        is_completed = wp_info.get('is_completed')
        print(f'wp_id: {wp_id}, is_completed: {is_completed}, progress: {wp_id_list.index(wp_id)}/{len(wp_id_list)}, '
              f'{round(wp_id_list.index(wp_id) / len(wp_id_list) * 100, 2)}%')

        """
        只有 2 需要进行批量组件。
        * 0 未配置表单 灰色
        * 1 已配置部分表单并且已提交部分表单 黄色
        * 2 提交流程表单 结束流程表单 绿色
        * 3 历史表单 已验评 绿色
        * 4 已配置表单 均未提交表单 蓝色
        * 5 表单提交到流程后 暂未审批通过 红色
        """
        if is_completed == 0:
            is_completed_0.append(wp_id)
        elif is_completed == 1:
            is_completed_1.append(wp_id)
        elif is_completed == 2:
            is_completed_2.append(wp_id)
        elif is_completed == 3:
            is_completed_3.append(wp_id)
        elif is_completed == 4:
            is_completed_4.append(wp_id)
        elif is_completed == 5:
            is_completed_5.append(wp_id)
        else:
            is_completed_6.append(wp_id)

    for is_completed_result in is_completed_result_list:
        result_index = is_completed_result_list.index(is_completed_result)
        msg = f'is_completed_{result_index}: len: {len(is_completed_result)}, rate: ' \
              f'{round(len(is_completed_result) / len(wp_id_list) * 100, 2)}%, content: {is_completed_result}'
        show_and_save_msg(msg=msg, file_name=f'{time_str}-count_wp_by_is_completed.log')


if __name__ == '__main__':
    print(f'{datetime.now()}: ----------main----------')
    # wp_code_list_ = ['Z01-05-02-0001', 'Z01-05-02-0002', 'Z01-05-02-0003', 'Z01-05-02-0004', 'Z01-05-02-0005']
    # 宗岳提供的批量组件参数：
    # wp_code_list_ = ['Z01-05-02-0003', 'Z01-05-02-0004', 'Z01-05-02-0005', 'Z01-05-02-0006', 'Z01-05-02-0007', 'Z01-05-02-0008', 'Z01-05-02-0009', 'Z01-05-02-0010', 'Z01-05-02-0012', 'Z01-05-02-0013', 'Z01-05-03-0001', 'Z01-05-03-0002', 'Z01-05-03-0003', 'Z01-05-03-0004', 'Z01-05-03-0005', 'Z01-05-03-0006', 'Z01-05-03-0007', 'Z01-05-03-0008', 'Z01-05-03-0009', 'Z01-05-03-0010', 'Z01-05-03-0011', 'Z01-05-03-0012', 'Z01-05-03-0013', 'Z01-05-03-0014', 'Z01-05-03-0015']
    # wp_code_list_ = ['Z01-05-02-0003']
    # batch_archive(wp_code_list_)

    # wp_id_list_ = []
    # count_wp_by_is_completed(wp_id_list_)
