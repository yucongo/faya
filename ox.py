#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
import yaml

def get_oxword(word):
    try:
        with open('faya.yml', 'r') as yml:
            conf = yaml.load(yml)
        ox_conf = conf['ox']
        app_id = ox_conf['app_id']
        app_key = ox_conf['app_key']
    except KeyError:
        return '配置文件有误'


    language = 'en'
    word_id = word

    url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower()

    r = requests.get(url, headers = {'app_id': app_id, 'app_key': app_key})

    if r.status_code == 200 :
        s_list = r.json()['results'][0]['lexicalEntries'][0]['entries'][0]['senses']
        print(s_list)
    else: return '牛津都没，你想查什么鬼（´-`）'

    defi = 'From ox:'

    for each in s_list:
        defi += '\nDEF:\n'+each['definitions'][0]

    return defi

        #if 'examples' in each:
            #print('examples:' + each['examples'][0]['text'])

if __name__=="__main__":
    print(get_oxword('nice'))
