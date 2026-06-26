# -*- coding: utf-8 -*-
"""
@author: sato
@file: check.py
@date:  2019/9/13 06:14
"""
from spider.utils import mongodb
data = list(mongodb['music'].find())
update_lrc = {}
# for i in data:
#     if len(i['comment_content'].split('\n')) > 1:
#         # print(i['comment_content'].split('\n'), i['id'])
#         update_lrc[i['id']] = '，'.join(i['comment_content'].split('\n')).replace('，，', '，')
# for _id, item in update_lrc.items():
#     print(_id, item)
#     mongodb['music'].find_one_and_update({'id': _id}, {'$set': {'comment_content': item}})

# mongodb['music'].find_one_and_update({'comment_content': '数学书上有一个温柔且霸气的词，有且只有[爱心]'}, {'$set': {'id': 68}})
# mongodb['music'].find_one_and_update({'comment_content': '“你的父亲现在还好吗？”，“他还是会到那个港口去，每个清晨，每一天”'}, {'$set': {'id': 92}})
# mongodb['music'].find_one_and_update({'comment_content': '难平的不是山海，是你的心'}, {'$set': {'id': 104}})
# mongodb['music'].find_one_and_update({'comment_content': '“夏目漱石曾把i love you翻译成“今夜月色真美”，那如何翻译i love you too呢？，风也温柔。”'}, {'$set': {'id': 155}})
# mongodb['music'].find_one_and_update({'comment_content': '润玉:“你算错了开始，我算错了结局。”，旭凤:“你并非算错，是我从未算过，我爱她。”'}, {'$set': {'id': 136}})
# mongodb['music'].find_one_and_update({'comment_content': '你别急 ，你先去读你的书 ，我也去看我的电影 ，总有一天 我们会窝在一起 ，读同一本书 看同一部电影 \u200b'}, {'$set': {'id': 154}})
# mongodb['music'].find_one_and_update({'comment_content': '给大家科普一下，上一个版本是自己录的没拿到版权，而这个版本是原曲日本作家，亲自给买辣椒录的曲啦，这次是有版权的了[爱心]'}, {'$set': {'id': 119}})
# mongodb['music'].find_one_and_update({'comment_content': '被电视剧《穿越时空的爱恋》选作片头曲，被电视剧《乌龙闯情关》选作片尾曲，被电视剧《新蜀山剑侠》选作主题曲，被电视剧《倩女幽魂》（大s版）选作插曲，被电视剧2007年版《新聊斋志异2》选作主题曲'}, {'$set': {'id': 83}})
for i in data:
    if '\r' in i['comment_content'] or '\n' in i['comment_content'] or '\r\n' in i['comment_content'] or '\n\r' in i['comment_content']:
        # print(i['comment_content'].replace('\n', '，').replace('\r', ' ').replace('，，', '，'), i['id'])
        update_lrc[i['id']] = i['comment_content'].replace('\n', '，').replace('\r', ' ').replace('，，', '，')
# 为什么刚开始我脑海中就浮现出了各种仙人叫“大圣”的声音[大哭]
for k, v in update_lrc.items():
    mongodb['music'].update_one({"id": k}, {"$set": {"comment_content": v}})
    print(mongodb['music'].find_one({"id": k}))

