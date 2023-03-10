import threading
import requests
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd
import json
import os
from fake_useragent import UserAgent
from tqdm import tqdm
import argparse

pd.options.display.max_columns = None
pd.options.display.max_rows = None
user_agent = UserAgent()
template = 'https://www.google.com.tw/maps/dir/{}/{}'


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input_file', type=str, default='address_list.json')
    parser.add_argument("--output_file", type=str, default='adjacency_matrix.json')

    args = parser.parse_args()

    return args

def get_header():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9", 
        "Accept-Encoding": "gzip, deflate, br", 
        "Accept-Language": "zh-TW,zh;q=0.9", 
        "Sec-Fetch-Dest": "document", 
        "Sec-Fetch-Mode": "navigate", 
        "Sec-Fetch-Site": "none", 
        "Upgrade-Insecure-Requests": "1", 
        "User-Agent": user_agent.random
    }
    return headers


def get_dist(soup):
    doc = soup.prettify()
    if doc.find('公里') != -1:
        pos = doc.find('公里')
        return float(doc[pos-20:pos].split('\"')[-1])

    elif doc.find('公尺') != -1:
        pos = doc.find('公尺')
        return float(doc[pos-20:pos].split('\"')[-1]) / 1000
    else:
        return None

def job(i, j, url, adjacency_matrix):
    html_doc = requests.get(url, headers=get_header())
    if html_doc.status_code != 200:
        print('I\'m a robot')
        return
    soup = BeautifulSoup(html_doc.text, 'html.parser')
    adjacency_matrix[i['name']][j['name']] = get_dist(soup)

def crawler(addr_list, adjacency_matrix):
    threads = []
    
    arr = []
    for i in addr_list:
        for j in addr_list:
            arr.append([i, j])
            
    for index, (i, j) in enumerate(tqdm(arr, bar_format='{l_bar:20}{bar:30}{r_bar}')):
        if adjacency_matrix[i['name']][j['name']] != None:
            continue
        url = template.format(i['address'], j['address'])
        print('\r{} -> {}'.format(i['name'], j['name']), end='')
#         print('\r{}/{}, {} -> {}, url: {}'.format(
#             index, len(addr_list)*len(addr_list), i['name'], j['name'], url), end='')

        threads.append(threading.Thread(target = job, args = (i, j, url, adjacency_matrix)))
        threads[-1].start()
        sleep(0.05)
    print()
    print('wait a moment')
    for thread in threads:
        thread.join()

def get_valid_edge_size(adjacency_matrix):
    cnt = 0
    for src in adjacency_matrix.keys():
        for dest in adjacency_matrix.keys():
            if adjacency_matrix[src][dest] != None:
                cnt += 1
    return cnt


def init_adjacency_matrix(addr_list):
    adjacency_matrix = {}
    for i in addr_list:
        adjacency_matrix[i['name']] = {}
        for j in addr_list:
            if i['name'] == j['name']:
                adjacency_matrix[i['name']][j['name']] = 0
            else:
                adjacency_matrix[i['name']][j['name']] = None
    return adjacency_matrix

def get_matrix(output_file, addr_list):
    name_set = set(pd.DataFrame(addr_list)['name'])
    
    # cache file
    if os.path.exists(output_file):
        with open(file=output_file, mode='r', encoding='utf-8') as reader:
            adjacency_matrix = json.load(reader)

        # check if the cache file is available
        if set(adjacency_matrix.keys()) == name_set:
            return adjacency_matrix

    adjacency_matrix = init_adjacency_matrix(addr_list)
    # create/overwrite file
    with open(file=output_file, mode='w', encoding='utf-8') as writer:
        json.dump(obj=adjacency_matrix, fp=writer, ensure_ascii=False, indent=4)
    return adjacency_matrix    

if __name__ == '__main__':
    args = parse_args()

    with open(file=args.input_file, mode='r', encoding='utf-8') as reader:
        addr_list = json.load(reader)


    adjacency_matrix = get_matrix(args.output_file, addr_list)

    cnt = get_valid_edge_size(adjacency_matrix) # number of edge that already get distance
    print('cnt = {}'.format(cnt))

    time_out = 0
    while cnt != len(addr_list) * len(addr_list):
        if time_out > 3:
            print('[ERROR] I\'m a robot')
            break
        
        crawler(addr_list, adjacency_matrix)
        newcnt = get_valid_edge_size(adjacency_matrix)
        if cnt == newcnt:
            sleep(2)
            time_out += 1

        cnt = newcnt
        print('cnt = {}'.format(cnt))
        sleep(5)


    print('adjacency matrix save at {}'.format(args.output_file))
    with open(file=args.output_file, mode='w', encoding='utf-8') as writer:
        json.dump(obj=adjacency_matrix, fp=writer, ensure_ascii=False, indent=4)