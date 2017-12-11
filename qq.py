#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
from datetime import datetime
from qqbot import QQBotSlot as qqbotslot
from qqbot import QQBotSched as qqbotsched, RunBot
import weather
import bilibili
import yaml
from pymongo import MongoClient
from aqi import get_aqi
import wyy
import Faya_fun
import _thread
import private

@qqbotslot
def onQQMessage(bot, contact, member, content):

    if bot.isMe(contact, member):
        return

    if member:
        if member.qq in my_members:
            nickname = my_members[member.qq]
        else:
            nickname = '?'
    elif contact.qq == master_qq:
        nickname = 'master'
    else:
        nickname = '?'

    '''
    if nickname in nick_dict:
        to_show_memo = check_memo(nickname)
        for each_p in to_show_memo:
            for each_memo in to_show_memo[each_p]:
                show_memo = '%s' % each_memo['memo']
                print(show_memo)
                bot.SendTo(contact, show_memo)
    '''

    faya_reply = Faya_fun.scenario(nickname, content, contact)




    last_post_time = 0
    last_reply = ''

    global last_post_time, last_reply

    if faya_reply:
        if last_reply != faya_reply:
            if time.time() - last_post_time > 20:
                bot.SendTo(contact, faya_reply)

                last_post_time = time.time()
                last_reply = faya_reply

    if member and not faya_reply:
        with open('log.txt', 'a+') as log:
            log.write(content.replace('\n', '')+'\n')

    eval(private.code())


    if content.find("http://music.163.com/") >= 0:
        bot.SendTo(contact, '尝试收藏')
        _thread.start_new_thread(wait_wyy, (bot, contact, content, nickname,))

        #wyylink = give_wyy()
        #return '尝试收藏' #save_wyy(content, nickname)+'\n\n'+wyylink

    if content.startswith('alarm'):
        al = content.split(' ')
        if len(al) >= 2:
            print(al)
            try:
                wait = float(al[1])
                if len(al) == 2:
                    _thread.start_new_thread(alarm,(bot, contact, nickname, wait,))
                else:
                    _thread.start_new_thread(alarm,(bot, contact, nickname, wait, al[2]))
            except TypeError:
                bot.SendTo(contact, '时间不对')

def wait_wyy(bot, contact, content, nickname):
    driver = wyy.save_wyy(content, nickname)
    bot.SendTo(contact, driver)
    return 0


def alarm(bot, contact, nick, min ,msg=''):
    bot.SendTo(contact, '好的')
    time.sleep(60*min)
    if msg:
        bot.SendTo(contact,nick + ' 提醒时间到了\n'+msg)
    else:
        bot.SendTo(contact, nick + ' 提醒时间到了')
    return 0



'''
@qqbotslot
def onStartupComplete(bot):
    with open('re.txt', 'w') as r:
        r.write(''+'\n')


@qqbotslot
def onExit(bot, code, reason, error):
    while 1:
        with open('re.txt', 'r') as r:
            if r.read() == 'ok':
                bot.Restart()                    
                break
            else:
                time.sleep(60)
'''

@qqbotsched(hour='0,1,6,11', minute='00') #18,20,22,23
def clock(bot):
    nowhour = datetime.now().hour
    gl = bot.List('group', 'qq=478475973')
    if gl is not None and (nowhour == 0 or nowhour >= 6):
        for group in gl:
            trd = '%s点了www' % nowhour
            kqzl = 0
            if nowhour == 6:
                trd += '\n 早呀。好困。'
                bot.SendTo(group, trd)

                tenki = weather.get_weather()
                bot.SendTo(group, tenki)

                kqzl = get_aqi()
                bot.SendTo(group, kqzl)

            if nowhour == 11:
                trd += '\n中午了呢'


            if nowhour == 0:
                trd += '\n什么都不想说了。。'

            if not kqzl:
                bot.SendTo(group, trd)

conn = MongoClient('localhost', 16376)
ani_post = conn.faya.bili.find_one()
ani_post.pop('_id')

days, hours, minutes =[],[],[]

for each in ani_post:
    if ani_post[each]['day'] not in days:
        days.append(ani_post[each]['day'])
    if ani_post[each]['hour'] not in hours:
        hours.append(ani_post[each]['hour'])
    if ani_post[each]['minute'] not in minutes:
        minutes.append(ani_post[each]['minute'])

@qqbotsched(day_of_week=','.join(days), hour=','.join(hours), minute=','.join(minutes))
def anime(bot):
    now = datetime.now()
    weekday = datetime.weekday(datetime.now())
    gl = bot.List('group', 'qq=478475973')
    if gl is not None:
        for group in gl:
            key = str(weekday)+str(now.hour)+str(now.minute)
            if key in ani_post:
                info = ani_post[key]['title']
                info = info + '\n' + bilibili.get_bilibili(ani_post[key]['av_id'])
                bot.SendTo(group, info)


if __name__ == "__main__":
    with open('faya.yml', 'r') as yml:
        conf = yaml.load(yml)
        try:
            master_qq = conf['master_qq']
            nict_dict = conf['nict_dict']
            group_qq = conf['group_qq']
            my_members = conf['my_members']

            global master_qq, nict_dict, group_qq, my_members
        except KeyError:
            print('配置文件有误')

    RunBot()