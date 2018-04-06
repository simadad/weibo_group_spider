import os
import re
import json
import requests
from config import *
from collections import namedtuple


session = requests.session()


def get_version():
    url = 'https://weibo.com/u/{uid}/home?wvr=5'.format(uid=uid)
    r = session.get(url, headers=headers)
    version = re.findall(r'version=(\w+)"', r.text)[0]
    return version


def get_source(version: str):
    url = 'https://js2.t.sinajs.cn/t6/webim_prime/js/common/all.js?version={ver}'.format(ver=version)
    r = session.get(url, headers=headers)
    source = re.findall(r'source:"(\d+)"', r.text)[0]
    return source


def get_group_list(source: str):
    # TODO 翻页
    url = 'https://api.weibo.com/webim/2/direct_messages/contacts.json?' \
         'source={s}&count=50&is_include_group=0&myuid={uid}'.format(s=source, uid=uid)
    r = session.get(url, headers=headers)
    data = json.loads(r.text)
    GData = namedtuple('GData', ('gid', 'name'))
    return [GData(x['user']['id'], x['user']['name']) for x in data['contacts']]


def get_group(group_list: list):
    # TODO 多群组
    print(u'请选择将要爬取的群组')
    print(u'\n{index:<5}|\t{group}'.format(index='NO.', group=u'群组'))
    for index, group in enumerate(group_list, 1):
        line = '{index:<5}|\t{name}'.format(index=index, name=group.name)
        print(line)
    g_index = int(input(u'\n请输入群组序号:\t')) - 1
    group = group_list[g_index]
    print(u'准备爬取群组 --- {name}\n......'.format(name=group.name))
    return group.gid, group.name


def get_root_dir():
    """
    获取根目录
    :return: 根目录
    """
    return root_dir or os.getcwd()


def get_or_create_dir(root, sub):
    """
    得到或创建目录
    :param root: 根目录
    :param sub: 子目录
    :return: 目录路径
    """
    is_new_dir = False
    path = '{root}/{sub}'.format(root=root, sub=sub)
    if not os.path.exists(path):
        os.mkdir(path)
        is_new_dir = True
    return path, is_new_dir


def init_root_dir(gname):
    """
    创建目录树----etc 目录、data 目录
    :return:
    """
    data_types = ('image', 'audio', 'file', 'text')
    DirData = namedtuple('DirData', data_types)
    dir_root = get_root_dir()
    dir_etc, is_new_dir = get_or_create_dir(dir_root, 'etc')
    dir_data, is_new_dir = get_or_create_dir(dir_root, 'data')
    dir_group_data, is_new_dir = get_or_create_dir(dir_data, gname)
    dir_group_etc, is_new_dir = get_or_create_dir(dir_etc, gname)
    dirs = DirData(*(get_or_create_dir(dir_group_data, x)[0] for x in data_types))
    return dir_group_etc, dirs


def init():
    version = get_version()
    source = get_source(version)
    group_list = get_group_list(source)
    gid, gname = get_group(group_list)
    dir_etc, dirs = init_root_dir(gname)
    return source, gid, dir_etc, dirs


if __name__ == '__main__':

    pass
