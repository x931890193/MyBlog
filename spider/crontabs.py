# -*- coding: utf-8 -*-
"""
@author: sato
@file: crontabs.py
@time: 2019-09-04 06:14

"""
import json
import hashlib
import time

import pymongo
import requests
import re
import threading
from pymongo import MongoClient

import multiprocessing
import sys

sys.path.insert(0, '/data/MyBlog')
from MyBlog.env import env
from MyBlog.settings import MEDIA_URL
from MyBlog.utils import redis_client
from spider.utils import qiniu_client, mongodb

MONGO_URI = env('MONGO_URI', 'mongodb://127.0.0.1:27017')
MONGODB_NAME = env('MONGODB_NAME', 'blog')
MUSIC_API_BASE_URL = env('MUSIC_API_BASE_URL', 'http://music.bytealien.com').rstrip('/')
MUSIC_LOGIN_EMAIL = env('MUSIC_LOGIN_EMAIL', '')
MUSIC_LOGIN_PASSWORD = env('MUSIC_LOGIN_PASSWORD', '')


def music_api_url(path):
    return '{}{}'.format(MUSIC_API_BASE_URL, path)


def music_login(session, username=None, password=None):
    username = username or MUSIC_LOGIN_EMAIL
    password = password or MUSIC_LOGIN_PASSWORD
    if not username or not password:
        print('skip music login: MUSIC_LOGIN_EMAIL or MUSIC_LOGIN_PASSWORD is not configured')
        return None
    return session.get(
        url=music_api_url('/login'),
        params={'email': username, 'password': password},
        headers={},
    )


class DuanziSpider(object):

    def __init__(self, *arg, **kw):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/76.0.3809.132 Safari/537.36'
        }
        self.base_url = 'http://duanziwang.com/'
        self.mongodb = MongoClient(MONGO_URI)[MONGODB_NAME]

    def req_and_write_base(self):
        to_insert = []
        old_ids = [int(i['id']) for i in list(self.mongodb['duanzi'].find())]
        for i in range(1, 5000):
            res = requests.get(url=self.base_url + 'page/{}/'.format(i), headers=self.headers)
            if res.status_code not in (200, 201):
                print('network error!')
                continue
            res.encoding = 'utf-8'
            data = re.findall('<article id="(\d+)" class="post">([\S\s]*?)</article>', res.text)
            # id, title, content, time, hot, like
            for item in data:
                if not item:
                    continue
                _id = int(item[0])
                if _id in old_ids:
                    continue
                rest = item[1]
                title = re.findall('<a href=".*">([\S\s]*?)</a>', rest)[0]
                like = re.findall('<span>([\S\s]*?)</span>', rest)[0]
                content = re.findall('<p>([\S\s]*?)</p>', rest)
                if content:
                    content = content[0]
                else:
                    content = ''
                hot = re.findall('<time class="post-date">([\S\s]*?)</time>', rest)[0]
                _time = re.findall('<time class="post-date" datetime=".*">([\S\s]*?)</time>', rest)[0]

                to_insert.append({
                    'id': _id,
                    'title': title,
                    'content': content,
                    'time': _time,
                    'hot': hot,
                    'like': int(like),
                })
                print(to_insert)
        if not to_insert:
            print('no more new duanzi!')
            return
        self.mongodb['duanzi'].insert_many(to_insert)

    def req_and_write_with_params(self, category):
        old_ids = [int(i['id']) for i in list(self.mongodb['duanzi'].find())] + [1]
        for i in range(1, 2000):
            print(self.base_url + 'category/{}/{}/'.format(category, i))
            try:
                res = requests.get(url=self.base_url + 'category/{}/{}/'.format(category, i), headers=self.headers)
                if res.status_code not in (200, 201):
                    print('network error!')
                    continue
            except Exception as e:
                print('{} {}'.format(e, self.base_url + 'category/{}/{}/'.format(category, i)))
                continue
            res.encoding = 'utf-8'
            data = re.findall('<article id="(\d+)" class="post">([\S\s]*?)</article>', res.text)
            # id, title, content, time, hot, like
            for item in data:
                if not item:
                    continue
                _id = int(item[0])
                if _id in old_ids:
                    continue
                rest = item[1]
                title = re.findall('<a href=".*">([\S\s]*?)</a>', rest)[0]
                like = re.findall('<span>([\S\s]*?)</span>', rest)[0]
                content = re.findall('<p>([\S\s]*?)</p>', rest)
                if content:
                    content = content[0]
                else:
                    content = ''
                hot = re.findall('<time class="post-date">([\S\s]*?)</time>', rest)[0]
                _time = re.findall('<time class="post-date" datetime=".*">([\S\s]*?)</time>', rest)[0]
                temp = {
                    'id': _id,
                    'title': title,
                    'content': content,
                    'time': _time,
                    'hot': hot,
                    'like': int(like),
                }
                self.mongodb['duanzi'].insert(temp)
                print(temp)


class VideoSpider(DuanziSpider):
    def __init__(self, *args, **kwargs):
        DuanziSpider.__init__(self, *args, **kwargs)
        # self.base_url = 'http://gaoxiao.52op.net/egao/index.htm'
        # self.base_url = 'http://gaoxiao.52op.net/fangyan/'
        self.base_url = 'http://gaoxiao.52op.net/egao/'
        self.json_url = 'http://gaoxiao.52op.net/flvData/d.aspx?id={}'

    def get_media_list(self):
        res = requests.get(self.base_url, headers=self.headers)
        res.encoding = 'utf-8'
        total_pages = re.findall('<a class="linkPage" href="(.*?)">([\S\s]*?)</a>', res.text)
        self.base_url = [self.base_url] + [t[0] for t in total_pages]
        # print(res.text)
        all_url = set()
        for p in self.base_url:
            ret = requests.get(url=p, headers=self.headers)
            ret.encoding = 'utf-8'
            htmls = re.findall('<a href="(.*)">([\S\s]*?)</a>', ret.text)
            for html in htmls:
                if html[0].endswith('target="_blank') and 'htm' in html[0]:
                    _id = html[0].split(' ')[0].split('/')[-1].split('.')[0]
                    all_url.add(self.json_url.format(_id))
        return all_url

    def down_and_upload_media(self, url):
        print(url)
        res = requests.get(url=url, headers=self.headers)
        res.encoding = 'utf-8'
        if res.status_code not in (200, 201):
            return
        data = json.loads(res.text)
        Data = data.get('Data')
        if not Data:
            return
        mp4_url = Data.get('MP4')
        if not mp4_url:
            return
        mp4_url = mp4_url.encode('utf-8').decode()
        res = requests.get(mp4_url, self.headers)
        if res.status_code not in (200, 201):
            return
        m = hashlib.md5()
        m.update(res.content)
        uid = m.hexdigest()
        if self.mongodb['video'].find_one({'uid': uid}):
            print(self.mongodb['video'].find_one({'uid': uid}))
            return
        r, info = qiniu_client.up_stream(res.content, 'video/' + uid + '.mp4')
        title_desc = data.get('Name')
        if ' ' in title_desc:
            title_desc = title_desc.split(' ')
            title = title_desc[0]
            desc = title_desc[1]
        else:
            title = desc = title_desc
        if r.get('key'):
            to_write = {
                'id': self.get_inc_id(),
                'uid': uid,
                'src': MEDIA_URL + r.get('key'),
                'title': title,
                'describe': desc
            }
            print('write data {}'.format(to_write))
            self.mongodb['video'].insert(to_write)

    @staticmethod
    def get_inc_id():
        return redis_client.incrby('video_id', 1)

    def run(self):
        url = list(self.get_media_list())
        pool = multiprocessing.Pool(multiprocessing.cpu_count())
        print(len(url))
        for a in url:
            # pool.apply_async(self.down_and_upload_media, args=(a,))
            self.down_and_upload_media(a)
        # pool.close()
        # pool.join()


def main():
    spider = DuanziSpider()
    # spider.req_and_write_base()
    categories = ['经典段子', '一句话段子', '段子来了', '搞笑图', '经典词句']
    threads = list()
    for c in categories:
        t = threading.Thread(target=spider.req_and_write_with_params, args=(c,))
        t.start()
        threads.append(t)
    for thread in threads:
        thread.join()

    video_spider = VideoSpider()
    video_spider.run()


def transfor():
    base_url = music_api_url('/song/url?id={}')
    mongodb = MongoClient(MONGO_URI)[MONGODB_NAME]
    data_byte = redis_client.hgetall('song')
    # comment_data = json.loads(data_byte.decode())
    # print(type(data_byte))
    new_data = []
    # /song/url?id = 33894312
    with requests.session() as se:
        if music_login(se) is None:
            return
        for i in data_byte.values():
            temp = json.loads(i)
            song_id = temp.get('song_id')
            ret = se.get(url=base_url.format(song_id))
            if ret.status_code not in (200, 201):
                return
            data = ret.json().get('data')[0]
            music_url = data.get('url')
            if not music_url:
                print(data)
                continue
            music_type = data.get('type')
            res = se.get(music_url)
            m = hashlib.md5()
            m.update(res.content)
            uid = m.hexdigest()
            if mongodb['music'].find_one({'uid': uid}):
                return
            r, info = qiniu_client.up_stream(res.content, 'music/' + uid + '.' + music_type)
            temp.update({'mp3_url': MEDIA_URL + r.get('key')})
            temp['id'] = redis_client.incrby('music_id', 1)
            temp['uid'] = uid
            # new_data.append(temp)
            print(temp)
            mongodb['music'].insert_one(temp)


def upload_img():
    mongodb = MongoClient(MONGO_URI)[MONGODB_NAME]
    url_list = [
        'https://timgsa.baidu.com/timg?image&quality=80&size=b9999_10000&sec=1568828008&di=9112e879b925fe0438eebb1a04eba7a2&imgtype=jpg&er=1&src=http%3A%2F%2Fc.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30086_france%2F30086_45133_6.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226225172&di=657e0be64fca0a747159b53683611d94&imgtype=0&src=http%3A%2F%2Fc.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30230_usa%2F30230_56211_6.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226259554&di=ab06461319c73f0baa7ae206c4759cc5&imgtype=0&src=http%3A%2F%2Fa.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30086_france%2F30086_45813_3.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226259554&di=d9391964f433fc5fa96d5f76c02170e5&imgtype=0&src=http%3A%2F%2Fa.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30211_switzerland%2F30211_72099_1.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226038115&di=e61131829cdf0a7be9b26584629c4143&imgtype=0&src=http%3A%2F%2Fa.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30032_belgium%2F30032_41782_21.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226038115&di=79abb4fe3625f6ba98dfe25d5f34879b&imgtype=0&src=http%3A%2F%2Fb.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30086_france%2F30086_62790_9.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226038114&di=3e5efc59235e25b9aa7f9ee7dd41f387&imgtype=0&src=http%3A%2F%2Fd.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30200_spain%2F30200_32770_12.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226038114&di=5202cd4d4eca3a37d618dc2acd9840dd&imgtype=0&src=http%3A%2F%2Fimg11.360buyimg.com%2Fcms%2Fjfs%2Ft184%2F304%2F3102149857%2F137575%2Fe48bdaff%2F53e1c97cN36195426.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226038114&di=3239cd1c251a6aa0bb01fdeea27dcd8f&imgtype=0&src=http%3A%2F%2Fa.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30200_spain%2F30200_32770_13.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226134608&di=57b5aaf431f471a6e57d16837c4ef80b&imgtype=0&src=http%3A%2F%2Fd.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30180_portugal%2F30180_117870_4.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226134607&di=e0a753bfc75433fe1ac3545435973c28&imgtype=0&src=http%3A%2F%2Fd.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30200_spain%2F30200_32770_8.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226134607&di=efe34f3226edcaceaef6f3213a10598d&imgtype=0&src=http%3A%2F%2Fpic.8pig.com%2Fdest%2Fcountry%2F66e547291bdfacdecf75d0a87bd5b2aa.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226134607&di=b21134222a93307842f83d0b4c445881&imgtype=0&src=http%3A%2F%2Fc.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30153_morocco%2F30153_50398_5.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226134606&di=21244c7274afcfd37cdf072ef6e5eabb&imgtype=0&src=http%3A%2F%2Fb.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30200_spain%2F30200_31538_9.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226178549&di=28c54860d6c39c1959eca15294c82e8c&imgtype=0&src=http%3A%2F%2Fpic.8pig.com%2Fdest%2Fcountry%2F723ecd5d2d62b746a4dee70871661f03.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226178549&di=4610430751ac766b614e39910c2b3b7d&imgtype=0&src=http%3A%2F%2Fc.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30200_spain%2F30200_31538_5.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226178548&di=6f06f2b384309903dd392dadbe70ba67&imgtype=0&src=http%3A%2F%2Fa.otcdn.com%2Fimglib%2Falmacen_fotos%2Fgeo_destinos_1920x440%2F30200_spain%2F30200_32869_1.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226225175&di=efd5c165a36ecb4c89bf157fc0a74251&imgtype=0&src=http%3A%2F%2Fpic.8pig.com%2Fdest%2Fcountry%2FFenLan02.jpg',
        'https://timgsa.baidu.com/timg?image&quality=100&size=b9999_10000&sec=1568226225174&di=87ff8f08315ceb79e18bfa159ec8c079&imgtype=0&src=http%3A%2F%2Fpic.8pig.com%2Fdest%2Fcountry%2Fc1f9df5e0a352f6a3332b6264d07d543.jpg',

    ]
    for i in url_list:
        req = requests.get(url=i)
        m = hashlib.md5()
        m.update(req.content)
        uid = m.hexdigest()
        if mongodb['banner'].find_one({'uid': uid}):
            return
        r, info = qiniu_client.up_stream(req.content, 'banner_image/' + uid + '.jpg')
        print(r, info)
        tmp_data = {'id': redis_client.incrby('banner_id', 1), 'uid': uid, 'banner_url': MEDIA_URL + r.get('key')}
        mongodb['banner'].insert_one(tmp_data)


def get_my_like(username=None, password=None):
    # username 手机号
    base_url = music_api_url('/song/url?id={}')
    mongodb = MongoClient(MONGO_URI)[MONGODB_NAME]

    with requests.session() as se:
        login_res = music_login(se, username, password)
        if login_res is None:
            return
        print(login_res)
        try:
            res = se.get(url=music_api_url('/daily_signin'))
            print(res.text)
        except:
            print('eeeeeeee')
        # 拿身份信息 id
        login_id = login_res.json().get('account').get('id')
        # 拿我的歌单
        my_list_res = se.get(url=music_api_url('/user/playlist?uid={}').format(login_id))
        # 我的喜欢列表
        my_like_list_id = my_list_res.json()['playlist'][0]['id']
        # my_like_detail
        my_like_songs_ids = \
        se.get(url=music_api_url('/playlist/detail?id={}').format(my_like_list_id)).json()['playlist'][
            'trackIds']
        my_like_songs_ids = [like['id'] for like in my_like_songs_ids]
        for i in my_like_songs_ids:
            temp = dict()
            song_detail = se.get(url=music_api_url('/song/detail?ids={}').format(i)).json()['songs'][0]
            temp['title'] = song_detail.get('name')
            temp['author'] = ','.join([n['name'] for n in song_detail.get('ar')])
            temp['images'] = song_detail.get('al').get('picUrl')
            temp['album'] = song_detail.get('al').get('name')
            temp['pub_date'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                             time.localtime(song_detail.get('publishTime') // 1000))
            # 拿热评
            comment_data = se.get(url=music_api_url('/comment/hot?id={}&type=0').format(i)).json()
            temp['comments_count'] = comment_data['total']
            temp['comment_id'] = ''
            if not comment_data['hotComments']:
                comment_data['hotComments']
                continue
            try:
                temp['comment_user_id'] = comment_data['hotComments'][0]['user']['userId']
            except:
                temp['comment_user_id'] = ''
            temp['comment_nickname'] = comment_data['hotComments'][0]['user']['nickname']
            temp['comment_avatar_url'] = comment_data['hotComments'][0]['user']['avatarUrl']
            temp['comment_liked_count'] = ','.join(
                [str(f) for f in str(comment_data['hotComments'][0]['likedCount']).split('\n')])
            temp['comment_content'] = comment_data['hotComments'][0]['content']
            temp['comment_pub_date'] = time.strftime('%Y-%m-%d %H:%M:%S',
                                                     time.localtime(comment_data['hotComments'][0]['time'] // 1000))
            temp['format_lrc'], temp['pretty_lrc'] = get_lrc(song_id=i)
            song_info = se.get(url=base_url.format(i))
            if song_info.status_code not in (200, 201):
                return
            data = song_info.json().get('data')[0]
            music_url = data.get('url')
            if not music_url:
                print(data)
                continue
            music_type = data.get('type')
            res = se.get(music_url)
            m = hashlib.md5()
            m.update(res.content)
            uid = m.hexdigest()
            if mongodb['music'].find_one({'uid': uid}):
                print('ignore this {}'.format(temp))
                continue
            r, info = qiniu_client.up_stream(res.content, 'music/' + uid + '.' + music_type)
            temp['song_id'] = i
            temp.update({'mp3_url': MEDIA_URL + r.get('key')})
            temp['id'] = redis_client.incrby('music_id', 1)
            temp['uid'] = uid
            # new_data.append(temp)
            print('insert this {}'.format(temp))
            mongodb['music'].insert_one(temp)


# ['_id',
# 'song_id',
# 'title',
# 'images',
# 'author',
# 'album',
# 'description',
# 'mp3_url',
# 'pub_date',
# 'comment_id',
# 'comment_user_id',
# 'comment_nickname',
# 'comment_avatar_url',
# 'comment_liked_count',
# 'comment_content',
# 'comment_pub_date',
# 'songs_count',
# 'comments_count',
# 'category_name',
# 'format_lrc',
# 'pretty_lrc',
# 'id',
# 'uid']

def get_lrc(song_id):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:58.0) Gecko/20100101 Firefox/58.0'}
    url = 'http://music.163.com/api/song/media?id={}'.format(song_id)
    res = requests.get(url=url, headers=headers)
    if res.status_code not in (200, 201):
        data = {'lrc': '[00:20.010] 获取歌词失败！'}
    else:
        json_data = json.loads(res.text)
        data = {'lrc': json_data.get('lyric', "[00:20.010] 暂无歌词～")}
        if '纯音乐' in data['lrc'] or not data['lrc']:
            data['lrc'] = "[00:20.010] 暂无歌词～"
        data['lrc'] = data['lrc'].replace('\r\n', '\n')
        data['lrc'] = data['lrc'].replace('\n\n', '\n')
        data['lrc'] = data['lrc'].replace('\r', '\n')

        lrc = data['lrc'].split('\n')
        data['lrc'] = '\n'.join(l for l in lrc if all(l.split(']')))
    format_lrc = [d for d in data.get('lrc').split('\n') if d and not d.isspace()]
    # print(format_lrc)
    if format_lrc == ['纯音乐，请您欣赏。']:
        format_lrc = ['[00:20.010] 暂无歌词～']
    pretty_lrc = []
    try:
        pretty_lrc = [lrc[lrc.index(']') + 1:] for lrc in format_lrc if lrc and not lrc.isspace()]
    except:

        print(format_lrc)
    # logger.info(data)
    return format_lrc, pretty_lrc
def enter():
    spider = VideoSpider()
    spider.run()
    get_my_like()


if __name__ == '__main__':
#    upload_img()
    # main()
    #spider = VideoSpider()
    #spider.run()
    get_my_like()
    # print(list(mongodb['music'].find())[:1])
    # print(list(mongodb['music'].index_information()))
    # print(mongodb['music'].ensure_index('id', 0))
    # print(mongodb['duanzi'].ensure_index('id', 0))
    # print(mongodb['video'].ensure_index('id', 0))
    # print(mongodb['banner'].ensure_index('id', 0))
    # print(ret)
    # '[00:20.010] 暂无歌词～'
