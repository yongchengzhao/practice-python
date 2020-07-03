# coding: utf-8

import sys
import os
import shutil
import time
import datetime
import re
import random
import uuid
import _thread
import ftplib
import json

import requests
from rest_framework.response import Response
from PyPDF2 import PdfFileReader

from decorators import BaseDecorator, ElapseDecorator, LogArgDecorator, LogResultDecorator, EnterExitDecorator
from decorators import enter_decorator, exit_decorator, duration, log_args


def test_standardize_form_file_names():
    """
    测试 standardize_form_file_names() 函数（在上面）是否正确。
    :return:
    """

    def standardize_form_file_names(forms, unit_type):
        """
        一键归档时需要对封装包内文件排序，规则就是下面的 standard_sequence_dict 中各 value 中的顺序，key 对应单元工程类型。
        :param forms:
        :param unit_type:
        :return:
        """
        if not forms:
            return -1

        standard_sequence_dict = {
            # 开挖工程
            'kw': [
                '岩石边坡开挖单元工程质量评定表',
                '岩石地基开挖单元工程质量评定表',
                '岩石地下平洞开挖单元工程质量评定表',
                '岩石竖井(斜井)开挖单元工程质量评定表',
                '岩石地下开挖单元工程质量评定表',
                '软基及岸坡开挖单元工程质量评定表',
                '单元工程质量评定表（附表）',
                '开挖（或隐蔽工程基础）单元工程验收合格证',
                '地质及施工缺陷处理联合检验认定表(通用)',
                '岩石开挖工程重要部位爆破造孔工序质量检查签证表',
                '爆破数据检测记录',
                '岩石开挖工程重要部位爆破造孔装药工序质量检查表',
                '起爆网络图/爆破炮孔布置图/爆破联网示意图/预裂孔布置图',
                '边坡预裂（光面）爆破开挖质量检查记录表',
                '边坡开挖爆破后效果评价表',
                '洞室光面（预裂）爆破开挖质量检查记录表',
                '洞室光面（预裂）开挖爆破后效果评价表',
                '施工测量成果报审单',
                '水工建筑物岩石基础验收证书',
                '水工建筑物岩石基础验收申报表',
                '岩石地基开挖工程联合检验签证表',
                '测量放样成果表(洞挖)',
            ],
            # 锚喷支护工程
            'mpzh': [
                '喷、锚支护单元工程质量评定表',
                '锚杆束单元工程质量评定表',
                '锚喷支护锚杆（束）工程质量检验与验收表',
                '锚喷支护锚杆（束）工程质量检验与验收表（附表）',
                '锚杆束安装工序验收及质量评定表',
                '锚筋桩分布位置示意图',
                '喷锚支护锚杆（束）孔钻孔工序验收及质量评定表',
                '喷锚支护锚杆安装工序验收及质量评定表',
                '锚喷支护锚杆施工展示图/锚喷支护锚杆布置图表',
                '喷、锚支护钢筋网安装工序验收及质量评定表',
                '钢支撑工序验收及质量评定表',
                '锚喷支护钢筋格栅工序验收及质量评定表',
                '喷射混凝土开仓申请（许可）单',
                '锚喷支护喷射混凝土开仓证',
                '喷射混凝土检查表',
                '喷、锚支护喷射混凝土工序验收及质量评定表',
                '砂浆抗压强度试验检测报告',
                '混凝土抗压强度试验检测报告',
                '锚杆无损检测报告',
                '基础排水单元工程质量等级评定表',
                '锚喷支护排水孔(管)工序质量验收表',
                '排水孔工程质量检验与验收表附表',
            ],
            # 预应力锚杆锚索工程
            'yyl': [
                '预应力锚杆单元工程质量评定表',
                '预应力锚杆工序施工验收及质量评定表',
                '预应力锚杆旁站记录表',
                '预应力锚杆施工展示图',
                '锚杆无损检测成果报告',
                '预应力锚索单元（单束）工程质量评定表',
                '钻孔灌浆班报',
                '锚索孔造孔工序验收及质量评定表',
                '锚索钻孔孔斜检测成果表',
                '预应力锚索预埋管道安装验收及质量评定表',
                '预应力锚索编制合格证',
                '预应力锚索制作安装工序验收及质量评定表',
                '预应力锚索锚墩混凝土验收及质量评定表',
                '预应力锚索注浆作业申请（许可）单',
                '灌浆施工记录表',
                '锚索孔灌浆记录表',
                '预应力锚索注浆工序验收及质量评定表',
                '锚索单循环验收试验张拉记录表',
                '荷载-位移曲线图',
                '预应力锚索张拉作业申请（许可）单',
                '锚索张拉预紧及整体张拉记录表',
                '锚索（端头锚）张拉工序验收及质量评定表',
                '锚索（对穿锚）张拉工序验收及质量评定表',
                '预应力锚索外锚头验收及质量评定表',
                '混凝土抗压强度试验检测报告',
                '砂浆抗压强度试验检测报告',
                '水泥净浆抗压强度试验检测报告',
                '施工强制性条文检查记录表',
                '锚索孔特殊情况处理表',
            ],
            # 混凝土工程
            'hnt': [
                '混凝土单元工程质量评定表',
                '基础面或混凝土施工缝处理工序验收及质量评定表',
                '混凝土建基面验收联合检验签证表',
                '混凝土模板工序验收及质量评定表',
                '清水混凝土模板工序验收及质量评定表',
                '混凝土滑膜工序验收及质量评定表',
                '混凝土模板测量检测成果表',
                '混凝土钢筋工序验收及质量评定表',
                '钢筋机械连接试验检测报告',
                '钢筋焊接试验检测报告',
                '钢筋接头现场验收合格证',
                '预埋件工序安装质量评定表',
                '铁件安装验收及质量评定表',
                '排水设施安装质量评定表',
                '止水片（带）安装验收及质量评定表',
                '伸缩缝材料安装验收及质量评定表',
                '冷却及接缝灌浆管路安装验收及质量评定表',
                '混凝土工程冷却水管通水检查记录表',
                '冷却水管布置示意图',
                '混凝土单元工程结构验收签证表',
                '内部观测仪器安装验收及质量评定表',
                '重要工程施工质量联合检验合格（开工、开仓）证',
                '混凝土（开工、仓）申请（许可）单',
                '混凝土单元工程浇筑工艺设计申报（审签）单',
                '混凝土浇筑前仓内重要结构埋件联合验收单',
                '混凝土单元工程开仓浇筑通知单',
                '混凝土浇筑工序质量检验签证表',
                '混凝土外观质量评定表',
                '大坝混凝土形体测量成果表',
                '清水混凝土外观质量评定表',
                '清水混凝土形体尺寸及表面平整度检查表',
                '混凝土抗压强度试验检测报告',
                '混凝土施工缺陷检查情况报告表',
                '混凝土入仓温度检测成果表',
                '混凝土浇筑温度检测成果表',
                '混凝土坝体内部温度检测成果表',
                '混凝土单元工程通水冷却检测成果表',
                '混凝土单元工程通水冷却闷温检测成果表',
                '混凝土工程接缝灌浆管道通水检查记录表',
                '混凝土单元工程养护记录表',
            ]
        }

        standard_sequence = standard_sequence_dict.get(unit_type)
        if not standard_sequence:
            return -1
        # print(datetime.datetime.now())
        count = 1
        for standard in standard_sequence:
            for form in forms:
                pdf_file_name = form.get('pdf_file_name')
                if standard == pdf_file_name.split('-')[-1]:
                    form['pdf_file_name'] = str(count) + '.' + form['pdf_file_name']
                    count += 1
                    if form.get('files'):
                        for i in range(len(form.get('files'))):
                            form.get('files')[i]['name'] = str(count) + '.' + form.get('files')[i]['name']
                            count += 1
        # print(datetime.datetime.now())
        return 1

    forms = [
        {
            'pdf_file_name': 'Z01-01-09-0044-喷、锚支护单元工程质量评定表',
            'files': []
        },
        {
            'pdf_file_name': 'Z01-01-09-0044-喷射混凝土开仓申请（许可）单',
            'files': []
        },
        {
            'pdf_file_name': 'Z01-01-09-0044-喷、锚支护钢筋网安装工序验收及质量评定表',
            'files': []
        },
        {
            'pdf_file_name': 'Z01-01-09-0044-喷、锚支护喷射混凝土工序验收及质量评定表',
            'files': [
                {
                    'name': 'Z01-01-09-0044-喷、锚支护喷射混凝土工序验收及质量评定表-附件'
                },
                {
                    'name': 'Z01-01-09-0044-喷、锚支护喷射混凝土工序验收及质量评定表-附件'
                }
            ]
        },
        {
            'pdf_file_name': 'Z01-01-09-0044-锚喷支护锚杆（束）工程质量检验与验收表',
            'files': [{
                'name': 'Z01-01-09-0044-锚喷支护锚杆（束）工程质量检验与验收表-附件'
            }]
        },
        {
            'pdf_file_name': 'Z01-01-09-0044-喷射混凝土检查表',
            'files': []
        },
    ]
    print(forms)
    standardize_form_file_names(forms, 'mpzh')
    print(forms)


def test_regular_expression():
    """
    练习正则表达式。
    :return:
    """
    str_list = ['1.', '34.', '', '检验资料-t-01-01', '3.监测资料-t-01-01', '999.']

    for str_ in str_list:
        print(re.match(r'^\d{1,3}\.$', str_))


def test_random():
    """
    练习随机模块。
    :return:
    """
    rand1 = random.random()
    print('rand1:', rand1)
    rand_uniform = random.uniform(0.0, 2)
    print('rand_uniform:', rand_uniform)
    rand_int1 = random.randint(10000000, 99999999)
    print('rand_int1:', rand_int1)
    rand_int2 = random.randint(10000000, 99999999)
    print('rand_int2:', rand_int2)
    print(rand_int1 > rand_int2)
    for i in range(10):
        rr = random.randint(0, 9)
        print(rr)


def test_coin_tossing():
    """
    假装抛硬币
    :return:
    """
    for i in range(1000):
        j = random.randint(0, 1)
        print(j, end='')


def test_file():
    """
    练习操作文件。
    :return:
    """
    file_dir = 'media/word/'
    filename = 'ad7b4b56-9c63-4186-bab9-b53471e99c03.docx'

    if not os.path.exists(file_dir):
        os.makedirs(file_dir)

    file_path = file_dir + filename
    temp_file = open(file_path, mode='wb+', buffering=4096)
    temp_file.write(b'a')
    temp_file.flush()
    temp_file.close()

    print(os.path.exists(file_path))
    print(os.path.basename(file_path))
    print(os.path.splitext(file_path))
    print(os.path.split(file_path))
    print(os.path.splitunc(file_path))
    print(os.path.splitdrive(file_path))
    print(os.path.splitext(os.path.basename(file_path))[0])


def test_multi_threading():
    """
    练习函数式多线程。
    :return:
    """
    print(f'Enter test_multi_threading.')

    def show_time(thread_name, delay):
        counter = 0

        while counter < 5:
            time.sleep(delay)
            counter += 1
            print(f'{thread_name}:{time.ctime(time.time())}')

    try:
        print('try')
        _thread.start_new_thread(show_time, ('thread-1', 1,))
        _thread.start_new_thread(show_time, ('thread-2', 2,))
    except KeyError:
        print('Can not start new thread.')

    while 1:
        pass


def test_range():
    """
    练习 range() 内置函数。
    :return:
    """
    for i in range(0, 10, 2):
        print(i)


def test_conversion_of_number_system():
    """
    练习进制转换。
    @return:
    """
    print(int('10'))
    print(int('1000', 2))
    print(int('100', 3))
    print(int('011', 8))
    print(int('11', 8))
    print(int('0x11', 16))
    print(int('11', 16))

    print(bin(4))
    print(bin(8))

    print(oct(10))
    print(oct(16))

    print(hex(10))
    print(hex(16))
    print(str(hex(10))[-1])


def calculate_compound(principal, annual_interest_rate, years):
    """
    计算本利和。
    :param principal: 本金。
    :param annual_interest_rate: 年利率。
    :param years: 年数。
    :return:
    """
    amount = principal
    for i in range(1, years + 1):
        amount *= (1 + annual_interest_rate)
        print(f'本利和： {amount}, 利息： {amount - principal}')


def test_dir():
    """
    练习操作文件夹。
    :return:
    """
    path = './2020-01-14'
    shutil.rmtree(path, ignore_errors=True)


def test_timestamp():
    """
    练习时间戳。
    :return:
    """
    print(datetime.datetime.timestamp(datetime.datetime.now()))
    print(time.time())
    print(int(time.time() * 10 ** 3))
    print(time.time() * 10 ** 3)
    print(str(int(time.time() * 10 ** 3)), 'adam')


def test_f():
    """
    练习 f 声明。
    :return:
    """
    pp = [2, 3, 4]
    print(f'This line is too long for the format, it may be cut to 2 lines. Is it?                               pp is '
          f'{pp}')

    dc = {
        'id': 2,
        'name': 'Adam',
        'age': 25
    }

    f_str = f'''
this is a f string, dc is {dc}
'''
    print(f_str)
    print(type(f_str))


def test_exception():
    """
    练习异常。
    :return:
    """
    try:
        print('try')
        raise IndexError
    except OSError:
        print('OSError')
    # else:
    #     print('else')
    finally:
        print('finally')


def test_dict():
    """
    练习字典。
    :return:
    """

    def update_gender(dd):
        """
        更新 gender。
        :param dd:
        :return:
        """
        dd.update(gender='female')

    dd = {'kw': 'kw', 'zl': 'zl', 'zcy': 'zcy'}
    print(dd, 'original')

    # for key, value in dd.items():
    #     print(key, value)

    dd['zcy'] = 'Adam'
    print(dd, 'modify zcy')

    dd.update(name='Eve', age=24)
    print(dd, 'add name and age')

    update_gender(dd)
    print(dd, 'add gender via function')

    print('-' * 60)
    dd2 = {'a': 1, 'b': 2, 'c': 3}
    for item in dd2.items():
        print(item)
    dd2['e'] = 5
    dd2['d'] = 4
    for item in dd2.items():
        print(item)


def test_none():
    """
    练习 None。
    :return:
    """
    # print(0 == None)
    # print('' == None)
    print(len(''))


# def test_serializer():
#     settings.configure()
#     archive_base_info = models.ArchiveBaseInfo.objects.get(pk=1)
#     serializer = serializers.ArchiveSummarySerializer(instance=archive_base_info)
#     print(type(serializer))
#     print(serializer)
#     print(type(serializer.data))
#     print(serializer.data)
#     print(type(serializer.validated_data))
#     print(serializer.validated_data)


def test_dict_update():
    """
    练习更新字典。
    :return:
    """
    dic = {}
    print(dic)
    dic.update(name='Adam')
    print(dic)
    dic.update(age=25)
    print(dic)
    dic.update({'gender': 'male'})
    print(dic)


def test_time_delta():
    """
    练习时间差 timedelta。
    :return:
    """
    today_datetime = datetime.datetime.today()
    print(f'today_datetime: {today_datetime}')
    date = datetime.date(2020, 3, 10)
    print(f'date: {date}')

    # haircut
    for i in range(11):
        print(date)
        date += datetime.timedelta(days=36)

    # 距今天数
    # delta = datetime.date(today_datetime.year, today_datetime.month, today_datetime.day) - date
    # print(delta)


def test_format():
    """
    练习字符串格式化。
    :return:
    """
    dic = [
        {
            "id": 3,
            'name': 'god.zip'
        },
        {
            'id': 2,
            'name': 'Adam.zip'
        }
    ]
    ss = 'test dict: {0}'.format(dic).replace("'", '"').encode('utf-8')
    print(ss.decode('utf8'))

    ii = 7
    print('格式化数字：%03d' % ii)


def test_time_format():
    """
    练习时间格式化。
    :return:
    """
    today = datetime.datetime.today()
    ss = today.strftime('%Y-%m')
    year_month = today.strftime('%Y-%m').split('-')
    print(today.year)
    print(today.month)
    print(year_month[0])
    print(year_month[1])
    print(ss)


def test_ftp():
    """
    练习 ftp。
    :return:
    """
    with ftplib.FTP(host='58.87.98.108') as ftp:
        ftp.login(user='unis', passwd='unis1234')
        # ftp.set_pasv(False)
        # 此行保证文件名为汉字的文件不会出现乱码的情况。
        ftp.encoding = 'utf-8'

        # ls .
        print(ftp.nlst())

        # ls 2020-03
        ftp.cwd('2020-03')
        print(ftp.nlst())
        print(ftp.pwd())

        # ls .
        ftp.cwd('..')
        print(ftp.pwd())

        print(ftp.nlst(f'2020-03/'))
        print(ftp.nlst(f'2020-03/04/'))


def test_list_add():
    """
    练习列表的添加。
    :return:
    """
    ll = [1]
    lll = [3, 4, 5]
    print(ll)
    ll += lll
    print(ll)
    for li in ll:
        if li == 4:
            ll[ll.index(li)] = 2
    print(ll)


def test_list_reduce():
    """
    练习列表间的差集。
    :return:
    """
    subtrahend = [
            'id', 'name', 'unit', 'segment', 'discipline', 'unit_project', 'station_scope', 'elevation_scope',
                  'work_package_code', 'construction_start', 'construction_end', 'pass_percent', 'quality_level',
                  'content', 'static_files', 'forms', 'size', 'code', 'md5', 'file_md5s', 'relative_path',
                  'absolute_path', 'detect_status', 'transfer_status', 'source_from', 'data_from', 'unit_info',
                  'file_list', 'keywords', 'creator_username', 'create_organization', 'create_time', 'retention_period',
                  'security_classification', 'security_deadline', 'last_modify_time', 'is_modified', 'archive_format',
                  'language']

    minuend = [
            'id', 'name', 'unit', 'segment', 'discipline', 'unit_project', 'station_scope', 'elevation_scope',
            'work_package_code',
            'construction_start', 'construction_end', 'pass_percent', 'quality_level', 'content', 'static_files',
            'forms', 'size', 'code', 'md5', 'file_md5s', 'relative_path', 'absolute_path',
            'detect_status', 'transfer_status', 'source_from',
            'data_from', 'unit_info', 'file_list', 'keywords', 'creator', 'creator_username', 'create_organization',
            'create_time', 'retention_period', 'security_classification', 'security_deadline', 'last_modify_time',
            'is_modified', 'archive_format', 'language'
        ]

    for sub in subtrahend:
        if sub in minuend:
            minuend.remove(sub)
    print(minuend)
    print(len(minuend))


def test_str():
    """
    练习操作字符串。
    :return:
    """
    ss = '012345'
    print(ss[2])  # 2

    print(f'ss.split("-"): {ss.split("-")}')  # ss.split("-"): ['012345']
    print(f'type(ss.split("-")): {type(ss.split("-"))}')  # type(ss.split("-")): <class 'list'>

    first_arg = 'first_arg'
    second_arg = 'second_arg'
    ss2 = (' ' * 32 + '我打算找一个很长的字符串用来格式化，并且在过程中代码会换行。这是第一个格式化：{}， 这是第二个{}。').\
        format(first_arg, second_arg)
    #                                 我打算找一个很长的字符串用来格式化，并且在过程中代码会换行。这是第一个格式化：first_arg， 这是第二个second_arg。
    print(ss2)


def test_sys():
    """
    练习 sys 模块。
    :return:
    """
    print(sys.version)
    print(sys.version_info)


def test_response_status():
    """
    练习响应码。
    :return:
    """
    res = Response('test')
    print(res.status_code)
    print(res.data)


def test_type():
    """
    练习 type() 内置函数。
    :return:
    """
    ff = 1.2
    print(f'type(ff): {type(ff)}')
    print(f'type(type(ff)): {type(type(ff))}')
    print(f'type(ff) in (float, int, str): {type(ff) in (float, int, str)}')


def test_out_index_error():
    """
    练习索引错误。
    :return:
    """
    ll = [0, 1, 2]
    print(ll[2])


def test_encode_decode():
    print("type('Adam'.encode('utf-8')):", type('Adam'.encode('utf-8')))
    print("'Adam'.encode('utf-8'):", 'Adam'.encode('utf-8'))
    print("type(b'Z'.decode('utf-8')):", type(b'Z'.decode('utf-8')))
    print("b'Z'.decode('utf-8'):", b'Z'.decode('utf-8'))
    print("type(b'a'):", type(b'a'))
    print("b'97':", b'97')
    print("type(0x61):", type(0x61))
    print("0x61:", 0x61)


def test_del_dir():
    # path = './test/' + str(int(time.time()*10**3)) + '/'
    path = './test/'
    # print(11111111)
    print(path)
    if os.path.exists(path):
        shutil.rmtree(path)


def test_finally():
    try:
        for i in range(10):
            print(i)
            # if i >= 7:
            #     raise ValueError()
    except ValueError:
        print('ValueError')
    finally:
        print('finally')


# def test_md5_insert():
#     md5 = '6dc9559d9a0af7efce0e09ab18e19d0e'
#     my_print('md5', md5)
#
#     salted_md5 = salt_md5(md5)
#     my_print('salted_md5', salted_md5)
#
#     desalted_md5, salt = desalt_md5(salted_md5)
#     my_print('desalted_md5', desalted_md5)
#     my_print('salt', salt)


def salt_md5(md5):
    if not isinstance(md5, str) or len(md5) != 32:
        return None

    salted_md5 = ''
    for i in range(0, 32, 2):
        salted_md5 += md5[i: i + 2] + hex(random.randint(0, 15))[-1]
    return salted_md5


# def desalt_md5(salted_md5):
#     """
#     将加盐后的 md5 值去盐。如果没有加盐，则返回 md5 本身。
#     @param salted_md5:
#     @return: 返回去盐后的 md5 值和盐，二者都是 str 类型。
#     """
#     md5_length, salted_md5_length = 32, 48
#
#     if not isinstance(salted_md5, str):
#         return None, None
#     elif salted_md5_length == len(salted_md5):
#         desalted_md5 = ''
#         for i in range(0, 48, 3):
#             desalted_md5 += salted_md5[i: i + 2]
#         salt = ''.join([salted_md5[3 * i - 1] for i in range(1, 17)])
#
#         return desalted_md5, salt
#     elif md5_length == len(salted_md5):
#         return salted_md5, None
#     else:
#         return None, None


def my_print(para_name, para_value):
    print(f'{para_name}: {para_value}')


def test_print():
    aa = 'aaa'
    bb = 'bbb'
    ii = 1234
    print(aa, bb, ii)


def test_uuid():
    # 第 13 位相同
    for i in range(0):
        uu1 = str(uuid.uuid4()).replace('-', '')
        uu2 = str(uuid.uuid4()).replace('-', '')
        result_list = []
        for j, k in zip(uu1, uu2):
            if j == k:
                result_list.append(True)
            else:
                result_list.append(False)
        print(result_list)

    # 获取 16 位 16 进制数
    # result = ''.join([random.choice(str(uuid.uuid4()).replace('-', '')) for i in range(13)])
    result = ''.join([hex(random.randint(0, 15))[-1] for i in range(16)])
    print(result)
    print(str(uuid.uuid4()).replace('-', '')[:16])


def test_char():

    for i in range(65, 69):
        ch = chr(i)
        ch_lower = chr(i + 32)
        print(f'{ch}oo{ch_lower}le')

    print(ord('a'))


def test_pdf():
    print(f'----------test_pdf----------')
    pdf = PdfFileReader('ppp.pdf')
    page_amount = pdf.getNumPages()
    print(page_amount)


class Account:

    def __init__(self, code: str, name: str = None, age: int = None) -> None:
        self.__code = code
        self.__name = name
        self.__age = age

    def __str__(self) -> str:
        return f'Account[' \
               f'code={self.__code}' \
               f', name={self.__name}' \
               f', age={self.__age}' \
               f']'

    def __unicode__(self):
        print(f"{'-' * 10}__unicode__方法{'-' * 10}")

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value: str) -> None:
        self.__name = value


def test_print_obj():
    adam = Account(name='Adam', code='001')
    eve = Account(age=24, code='002')
    print(adam)
    print(eve)
    print(adam.name)
    adam.name = 'God'
    print(adam.name)


def test_data_type():
    print(0 == -1)
    print(0 == "")
    # print(0 == None)


def test_operator():
    html = '''<html>'''
    html += '''
    <div>'''
    html += '''
    </div>'''
    html += '''
</html>
'''
    print(html)


def test_function_elapse_time():
    enter_time = datetime.datetime.now()
    print(enter_time)
    time.sleep(3)
    print(f'function test_function_elapse_time() elapse {datetime.datetime.now() - enter_time}')


def test_requests():
    url = f'http://10.215.160.41:6540/api/user/files/3517'
    auth = ('yfg', 'yfg')
    res = requests.get(url=url, auth=auth)
    print(res.status_code)
    print(res.content.decode('utf-8'))
    print(f'type(res.content.decode("utf-8")): {type(res.content.decode("utf-8"))}')
    print(json.loads(res.content).get('id'))
    print(f"type(json.loads(res.content).get('id')): {type(json.loads(res.content).get('id'))}")
    print(res.elapsed)
    print(res.next)
    print(res.text)
    print(res.raise_for_status())


def test_type_hints(user_id: int or str) -> dict:
    print(user_id)
    print(str(user_id))
    print(repr(user_id))
    return {}


class ModifyFormAuditOperator:

    def __init__(self, base_url='http://10.215.160.41:6544/main/modify-form-audit/', auth=('admin', 'adminadmin')):
        self.__base_url = base_url
        self.__auth = auth

    def get_obj_list(self):
        obj_list = json.loads(requests.get(url=self.__base_url, auth=self.__auth).content)
        return obj_list

    def get_id_list(self):
        obj_list = self.get_obj_list()
        id_list = [obj.get('id', 0) for obj in obj_list]
        return id_list

    def del_by_id(self, _id):
        url = self.__base_url + f'{_id}'
        res = requests.delete(url=url, auth=self.__auth)
        print(f'{_id}: {res.status_code}')

    def clear(self):
        id_list = self.get_id_list()
        for _id in id_list:
            self.del_by_id(_id)


@ElapseDecorator
@LogArgDecorator
@EnterExitDecorator
@LogResultDecorator
def test_class_base_decorators(a):
    print(f'Function test_class_base_decorators(), {a}.')


@enter_decorator
@exit_decorator
@duration
@log_args
def test_func_base_decorators(a):
    print(f'Function test_func_base_decorators(), {a}, {"-" * 40}.')
    return a, a


@duration
class Foo:

    def __init__(self):
        print(f'Foo.__init__()')

    @duration
    def bar(self):
        pass


def test_collect_args(*args, **kwargs):
    print(args)
    print(kwargs)


def test_write():
    with open(file='a.xml', mode='w', buffering=True, encoding='UTF-8') as meta_file:
        temp = f'''<?xml version="1.0" encoding="UTF-8"?>
    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
    xmlns="http://www.saac.gov.cn/standards/ERM/encapsulation"
    targetNamespace="http://www.saac.gov.cn/standards/ERM/encapsulation"
    elementFormDefault="qualified">

    <xs:element name="电子文件封装包">
        <xs:annotation>
            <xs:documentation>eep 根元素</xs:documentation>
        </xs:annotation>
        <xs:complexType>
            <xs:sequence>
                <xs:element ref="封装包格式描述"/>
                <xs:element ref="版本"/>
                <xs:element ref="被签名对象"/>
            </xs:sequence>
        </xs:complexType>
    </xs:element>
    <xs:element name="封装包格式描述" type="xs:string" default="本EEP根据中华人民共和国档案行业标准DA/T 48-2009《基于XML的电子文件封装规范》生成"/>
    <xs:element name="版本" type="xs:gYear" fixed="2009">\n'''
        meta_file.write(temp)


def init_procedure_sequence():
    # 混凝土工程
    data_list_hntgc = [
        '混凝土建基面验收联合检验签证表',
        '基础面或混凝土施工缝处理工序验收及质量评定表',
        '混凝土模板工序验收及质量评定表',
        '混凝土滑模工序验收及质量评定表',
        '清水混凝土模板工序验收及质量评定表',
        '钢筋接头现场验收合格证',
        '混凝土钢筋工序验收及质量评定表',
        '止水片（带）安装验收及质量评定表',
        '排水设施安装质量评定表',
        '铁件安装验收及质量评定表',
        '混凝土浇筑前仓内重要结构埋件联合验收单',
        '伸缩缝材料安装验收及质量评定表',
        '混凝土（开工、仓）申请（许可）单',
        '冷却及接缝灌浆管路安装验收及质量评定表',
        '混凝土工程冷却水管通水检查记录表',
        '预埋件工序安装质量评定表',
        '混凝土外观质量评定表',
        '清水混凝土外观质量评定表',
        '混凝土浇筑工序质量检验签证表',
        '混凝土单元工程质量评定表'
    ]

    # 预应力锚杆锚索-中孔锚索工序顺序
    data_list_yylmgms_zk = [
        '混凝土结构锚索管道安装质量检验签证表',
        '混凝土结构预应力锚索制作安装工序质量检验签证表',
        '混凝土结构预应力锚索张拉作业申请（许可）表',
        '混凝土结构预应力锚索张拉预紧记录表',
        '混凝土结构预应力锚索整体张拉记录表',
        '混凝土结构预应力锚索张拉作业工序质量检验签证表（主锚索，3800kN）',
        '混凝土结构预应力锚索张拉作业工序质量检验签证表（次锚索，2400kN）',
        '混凝土结构预应力锚索注浆工序质量检验签证表',
        '混凝土结构预应力锚索单元工程质量等级评定表',
    ]

    # 预应力锚杆锚索-预应力锚索工序顺序
    data_list_yylmgms_yyl = [
        '锚索孔造孔工序验收及质量评定表',
        '预应力锚索编制合格证',
        '预应力锚索预埋管道安装验收及质量评定表',
        '预应力锚索制作安装工序验收及质量评定表',
        '预应力锚索注浆作业申请（许可）单',
        '预应力锚索注浆工序验收及质量评定表',
        '预应力锚索锚墩混凝土验收及质量评定表',
        '预应力锚索张拉作业申请（许可）单',
        '锚索单循环验收试验张拉记录表',
        '锚索张拉预紧及整体张拉记录表',
        '锚索（端头锚）张拉工序验收及质量评定表',
        '锚索（对穿锚）张拉工序验收及质量评定表',
        '预应力锚索外锚头验收及质量评定表',
        '预应力锚索单元（单束）工程质量评定表',
    ]

    # base_url = 'http://10.215.160.41:8000/main/api/procedure_sequence/'
    base_url = 'http://localhost:18006/main/api/procedure_sequence/'
    headers = {'content-type': 'application/json'}
    depend_at_least_one, depend_have_to, depend_optional, depend_must_undone = [], [], [], []
    unit_type = 'yylmgms_yyl'
    data_list = {
        'hntgc': data_list_hntgc,
        'yylmgms_zk': data_list_yylmgms_zk,
        'yylmgms_yyl': data_list_yylmgms_yyl
    }.get(unit_type)

    for name in data_list:
        sequence = data_list.index(name) + 1
        post_data = {
            'name': name,
            'sequence': sequence,
            'unit_type': unit_type,
            'depend_at_least_one': depend_at_least_one,
            'depend_have_to': depend_have_to,
            'depend_optional': depend_optional,
            'depend_must_undone': depend_must_undone
        }
        res = requests.post(url=base_url, data=json.dumps(post_data), headers=headers)
        print(sequence, res.status_code, res.content.decode('utf-8'))


def delete_all_procedure_sequence():
    # base_url = 'http://10.215.160.41:8000/main/api/procedure_sequence/'
    base_url = 'http://localhost:18006/main/api/procedure_sequence/'
    unit_type = 'yylmgms_yyl'
    url = f'{base_url}?unit_type={unit_type}'

    procedure_sequence_info_list = json.loads(requests.get(url=url).content)

    for info in procedure_sequence_info_list:
        del_url = f'{base_url}{info.get("id")}/'
        res = requests.delete(url=del_url)
        print(f'{info.get("id")}: {res.status_code}')


def process_procedure_sequence_dependency():

    def get_procedure_sequence_info_by_sequence(sequence_: int, unit_type_: str) -> dict:
        query_url = f'{base_url}?unit_type={unit_type_}&sequence={sequence_}'
        return json.loads(requests.get(url=query_url).content.decode('utf-8'))[0]

    def get_patch_data_by_sequence_hntgc(sequence__: int) -> dict:
        patch_data_ = {}

        if sequence__ in [1]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [2]]
            }
        elif sequence__ in [2]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [],
                'depend_optional': [info_.get('id') for info_ in procedure_sequence_info_list
                                    if info_['sequence'] in [1]],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [3, 4, 5, 6, 8, 9, 10, 11, 12]]
            }
        elif sequence__ in [3, 4, 5, 8, 9, 10, 11, 12]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [2]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [13]]
            }
        elif sequence__ in [6]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [2]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [7]]
            }
        elif sequence__ in [7]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [6]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [13]]
            }
        elif sequence__ in [13]:
            patch_data_ = {
                'depend_at_least_one': [info_.get('id') for info_ in procedure_sequence_info_list
                                        if info_['sequence'] in [3, 4, 5, 7, 8, 9, 10, 11, 12]],
                'depend_have_to': [],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [17, 18, 19]]
            }
        elif sequence__ in [14, 15, 16]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [2]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [17, 18, 19]]
            }
        elif sequence__ in [17, 18, 19]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [13]],
                'depend_optional': [info_.get('id') for info_ in procedure_sequence_info_list
                                    if info_['sequence'] in [14, 15, 16]],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [20]]
            }
        elif sequence__ in [20]:
            patch_data_ = {
                'depend_at_least_one': [info_.get('id') for info_ in procedure_sequence_info_list
                                        if info_['sequence'] in [17, 18, 19]],
                'depend_have_to': [],
                'depend_optional': [],
                'depend_must_undone': []
            }

        return patch_data_

    def get_patch_data_by_sequence_yylmgms_zk_10(sequence__: int) -> dict:
        patch_data_10 = {}

        if sequence__ in [1]:
            patch_data_10 = {
                'depend_at_least_one': [],
                'depend_have_to': [],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [2]]
            }
        elif sequence__ in [2]:
            patch_data_10 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                    if info_['sequence'] in [1]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [3]]
            }
        elif sequence__ in [3]:
            patch_data_10 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [2]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [4]]
            }
        elif sequence__ in [4]:
            patch_data_10 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [3]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [5]]
            }
        elif sequence__ in [5]:
            patch_data_10 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [4]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [6, 7]]
            }
        elif sequence__ in [6, 7]:
            patch_data_10 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                        if info_['sequence'] in [5]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [8]]
            }
        elif sequence__ in [8]:
            patch_data_10 = {
                'depend_at_least_one': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [6, 7]],
                'depend_have_to': [],
                'depend_optional': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [6, 7]],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [9]]
            }
        elif sequence__ in [9]:
            patch_data_10 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [8]],
                'depend_optional': [],
                'depend_must_undone': []
            }

        return patch_data_10

    def get_patch_data_by_sequence_yylmgms_zk_20(sequence__: int) -> dict:
        patch_data_20 = {}

        if sequence__ in [1]:
            patch_data_20 = {
                'depend_at_least_one': [],
                'depend_have_to': [],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [2]]
            }
        elif sequence__ in [2]:
            patch_data_20 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [1]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [3]]
            }
        elif sequence__ in [3]:
            patch_data_20 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [2]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [6, 7]]
            }
        elif sequence__ in [6, 7]:
            patch_data_20 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [3]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [8]]
            }
        elif sequence__ in [8]:
            patch_data_20 = {
                'depend_at_least_one': [info_.get('id') for info_ in procedure_sequence_info_list
                                        if info_['sequence'] in [6, 7]],
                'depend_have_to': [],
                'depend_optional': [info_.get('id') for info_ in procedure_sequence_info_list
                                    if info_['sequence'] in [6, 7]],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [9]]
            }
        elif sequence__ in [9]:
            patch_data_20 = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [8]],
                'depend_optional': [],
                'depend_must_undone': []
            }

        return patch_data_20

    def get_patch_data_by_sequence_yylmgms_yyl(sequence__: int) -> dict:
        patch_data_ = {}

        if sequence__ in [1, 2, 3]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [4]]
            }
        elif sequence__ in [4]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                    if info_['sequence'] in [1, 2]],
                'depend_optional': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [3]],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [5, 7]]
            }
        elif sequence__ in [5]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [4]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [6]]
            }
        elif sequence__ in [6]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [5]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [8]]
            }
        elif sequence__ in [7]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [4]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [8]]
            }
        elif sequence__ in [8]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                        if info_['sequence'] in [6, 7]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [9, 10]]
            }
        elif sequence__ in [9]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [8]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                       if info_['sequence'] in [10]]
            }
        elif sequence__ in [10]:
            patch_data_ = {
                'depend_at_least_one': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [8, 9]],
                'depend_have_to': [],
                'depend_optional': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [9]],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [11, 12]]
            }
        elif sequence__ in [11, 12]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [10]],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [13]]
            }
        elif sequence__ in [13]:
            patch_data_ = {
                'depend_at_least_one': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [11, 12]],
                'depend_have_to': [],
                'depend_optional': [],
                'depend_must_undone': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [14]]
            }
        elif sequence__ in [14]:
            patch_data_ = {
                'depend_at_least_one': [],
                'depend_have_to': [info_.get('id') for info_ in procedure_sequence_info_list
                                   if info_['sequence'] in [13]],
                'depend_optional': [],
                'depend_must_undone': []
            }

        return patch_data_

    # base_url = 'http://10.215.160.41:8000/main/api/procedure_sequence/'
    base_url = 'http://localhost:18006/main/api/procedure_sequence/'
    unit_type = 'yylmgms_yyl'
    max_sequence = {
        'hntgc': 20,
        'yylmgms_zk': 9,
        'yylmgms_yyl': 14
    }.get(unit_type)
    get_patch_data_func = {
        'hntgc': get_patch_data_by_sequence_hntgc,
        'yylmgms_zk': get_patch_data_by_sequence_yylmgms_zk_20,
        'yylmgms_yyl': get_patch_data_by_sequence_yylmgms_yyl
    }.get(unit_type)

    procedure_sequence_info_list = [get_procedure_sequence_info_by_sequence(i, unit_type)
                                    for i in range(1, max_sequence + 1)]
    # print(procedure_sequence_info_list)

    for info in procedure_sequence_info_list:
        sequence = info.get('sequence')
        patch_data = get_patch_data_func(sequence)

        patch_url = f'{base_url}{info["id"]}/'
        res = requests.patch(url=patch_url, data=patch_data)
        print(info['id'], res.status_code, res.content.decode('utf-8'))


def test_date_parse():
    sign_time_list = []
    date_time_str_list = [
        '2020-05-26 15:38:20',
        '2020-05-28 15:38:21',
        '2020-05-28 15:38:22',
        None,
        '2020-07-28 15:38:23',
        '2020-05-23 15:18:24',
        '2020-05-28 15:38:25',
        None,
        '2020-05-28 15:38:26',
        '2020-05-21 15:38:27',
        '2021-05-28 19:38:28',
        '1020-05-28 15:38:29'
    ]

    for supervisor_sign_time in date_time_str_list:
        if not supervisor_sign_time:
            continue

        supervisor_sign_time = supervisor_sign_time[0:10]
        sign_time_list.append(datetime.datetime.strptime(supervisor_sign_time, '%Y-%m-%d'))

    print(sign_time_list)
    print(min(sign_time_list).strftime('%Y-%m-%d'))
    print(max(sign_time_list).strftime('%Y-%m-%d'))


def test_modify_file_name():
    directory = 'E:/Adam/audio/audiobook/adam'

    filename_list = os.listdir(directory)

    for filename in filename_list:
        if 'xxx' in filename:
            old_path = os.path.join(directory, filename)
            new_path = os.path.join(directory, filename.replace('MP3', 'mp3'))
            os.renames(old_path, new_path)


def process_baidu_dir():
    """
    根据提供的百度原始数据在本地新建文件夹目录结构。
    :return:
    """
    raw_data_list = []
    for raw_data in raw_data_list:
        absolute_path = '.' + raw_data.get('path', '')
        os.makedirs(absolute_path, exist_ok=True)
        

def test_out_of_memory():
    """
    测试内存溢出。
    :return:
    """
    ll = []
    # 修改 range() 函数内的值来修改占用内存大小。改成 100000000 后跑了一下，没有报内存溢出，电脑内存占用飙到 100%，电脑卡死。
    # 最后不得不强制关机重启。
    for i in range(10):
        print(i)
        ll.append("new string" + f'{i}')


def test_multi_thread_do_request():

    def do_request(thread_num, url_):
        print(f'do_request')
        res = requests.get(url=url_)
        print(res)
        print(thread_num, res.status_code)

    thread_amount = 100
    url = f'https://www.csdn.net/'

    for i in range(thread_amount):
        print(i)
        thread = _thread.start_new_thread(do_request, (i, url))


def test_tuple():
    tup = tuple()
    print(tup)
    print(type(tup))

    tup2 = ()
    print(tup2)
    print(type(tup2))


def test():
    print(f'test')


if __name__ == '__main__':
    print(f'----------main----------')
    test()
