import time
from concurrent.futures import ThreadPoolExecutor, wait
from init import *


def get_data_pre(source, gid, mid):
    url = 'https://api.weibo.com/webim/groupchat/query_messages.json?' \
         'source={s}&convert_emoji=1&count=20&id={gid}&max_mid={mid}&query_sender=1'.format(s=source, gid=gid, mid=mid)
    r = session.get(url, headers=headers)
    data = json.loads(r.text)
    return data


def get_media_data(source, fids: list):
    fid = fids[0]
    src = "https://upload.api.weibo.com/2/mss/msget?source={source}&fid={fid}".format(source=source, fid=fid)
    r = session.get(src, headers=headers)
    data = r.content
    return fid, data


def router_msg_flow_control(data: dict):
    msg_list = data.get('messages')
    if msg_list:
        mid = msg_list[0]['id']
        print(mid, len(msg_list), 2222222222)
        return mid, msg_list
    else:
        print(1231231231)
        return False, False


def router_msg_flow(source, gid, mid=0):
    while True:
        data = get_data_pre(source, gid, mid)
        # print(data, 5555555)
        mid, msg_list = router_msg_flow_control(data)
        if not mid:
            print('end')
            break
        # TODO `yield msg_list` 20 msg pre thread
        for msg in msg_list:
            # print(type(msg), 999999999999)
            yield msg


def router_msg_save(source, msg: dict):
    # print(77777777777)
    content, username, time_fm, media_type, fids = analyze_msg(msg)
    # print(content[:20], username, time_fm, media_type, fids, 333333333333)
    save_text_msg(content, time_fm, username)
    if fids:
        fid, data = get_media_data(source, fids)
        if media_type == 1:
            save_image_msg(data, time_fm, username)
        elif media_type == 4:
            save_audio_msg(data, time_fm, username)
        else:
            save_file_msg(data, time_fm, username, content)


def analyze_msg(msg: dict):
    content = msg['content']
    _time = msg['time']
    media_type = msg.get('media_type')
    fids = msg.get('fids')
    # print(content[:10], _time, media_type, 'aaaaaaaaaaa')
    time_fm = time.strftime('%y-%m-%d-%H-%M-%S', time.localtime(_time))
    username = msg['from_user']['screen_name']
    # print(time_fm, username, 'bbbbbbbbbbbbbbbbbb')
    return content, username, time_fm, media_type, fids


def save_text_msg(content, time_fm, username: str):
    # TODO 调整数据记录顺序
    time_fm_month = time_fm[:5]
    # dir_text = '{dir_data}/text'.format(dir_data=dir_data)
    path_gather = u'{dir}/{time}.txt'.format(dir=dirs.text, time=time_fm_month)
    dir_month, is_new = get_or_create_dir(dirs.text, time_fm_month)
    path_detail = '{dir}/{username}.txt'.format(dir=dir_month, username=username)
    with open(path_detail, 'a') as f:
        line = '{time}: {data}\n'.format(time=time_fm, data=content)
        f.write(line)
    with open(path_gather, 'a') as f:
        username_fm = username.ljust(20 - len(re.findall(u"[\u4e00-\u9fa5\u3040-\u309f\u30a0-\u30ff]", username)))
        line = '{time} {username}: {data}\n'.format(time=time_fm, data=content, username=username_fm)
        f.write(line)


def save_image_msg(data, time_fm, username):
    time_fm_month = time_fm[:5]
    dir_month, is_new = get_or_create_dir(dirs.image, time_fm_month)
    dir_user, is_new = get_or_create_dir(dir_month, username)
    path = '{dir}/{time_fm}.jpg'.format(dir=dir_user, time_fm=time_fm)
    if os.path.exists(path):
        path = '{path}-{time}'.format(path=path, time=str(time.time())[-6:])
    with open(path, 'wb') as f:
        f.write(data)


def save_audio_msg(data, time_fm, username):
    time_fm_month = time_fm[:5]
    dir_month, is_new = get_or_create_dir(dirs.audio, time_fm_month)
    dir_user, is_new = get_or_create_dir(dir_month, username)
    path = '{dir}/{time_fm}.amr'.format(dir=dir_user, time_fm=time_fm)
    if os.path.exists(path):
        path = '{path}-{time}'.format(path=path, time=str(time.time())[-6:])
    with open(path, 'wb') as f:
        f.write(data)


def save_file_msg(data, time_fm, username, content: str):
    time_fm_month = time_fm[:5]
    dir_month, is_new = get_or_create_dir(dirs.file, time_fm_month)
    dir_user, is_new = get_or_create_dir(dir_month, username)
    # file_name = lambda x: x[x.find(']') + 1:] if re.search(r'\.\w+', x) else '{}.jpg'.format(x[x.find(']') + 1:])
    path = '{dir}/{time_fm}-{file}'.format(dir=dir_user, time_fm=time_fm, file=comp_file_name(content))
    if os.path.exists(path):
        path = '{path}-{time}'.format(path=path, time=str(time.time())[-6:])
    with open(path, 'wb') as f:
        f.write(data)


def comp_file_name(content: str):
    name = content[content.find(']') + 1:]
    if not re.search(r'\.\w+', content):
        name = '{}.jpg'.format(name)
    return name


def router():
    pool_items = ThreadPoolExecutor(thr_pool_nums)
    thr_items = []
    global dirs
    source, gid, dir_etc, dirs = init()
    # print(source, gid, dir_etc, dirs, 1111111111)
    msg_flow = router_msg_flow(source, gid)
    for msg in msg_flow:
        # print(type(msg), 888888888888888888)
        thr = pool_items.submit(router_msg_save, source, msg)
        # TODO 清除已结束线程
        thr_items.append(thr)
    wait(thr_items)


if __name__ == '__main__':
    dirs = None
    router()
