## Setup

To get started, clone this repository onto your local device.

```shell
git clone https://github.com/nike00811/distance_crawler.git
cd distance_crawler
```

install all the dependencies listed in requirements.txt.

```shell
pip install -r requirement.txt
```

## Usage

Run the following command

```shell
python crawler.py --input_file address_list.json --output_file output.json
```

Alternatively, you can simply use the provided `crawler.ipynb` file to run the code on a notebook interface

#### address_list.json

```json
[
    {
        "name": "中坡",
        "address": "台北市南港區中坡南路47號1樓"
    },
    {
        "name": "中研",
        "address": "台北市南港區研究院路二段128號1樓(學術活動中心)"
    },
    {
        "name": "中貿",
        "address": "台北市南港區經貿二路186號2樓"
    },
    {
        "name": "玉成",
        "address": "台北市南港區西新里南港路三段3號1樓"
    },
    {
        "name": "玉德",
        "address": "台北市南港區玉成街150號1樓"
    }
]
```



#### User-Agent

Use different user agents at each request to prevent being detected and banned by the server.

```python
from fake_useragent import UserAgent

user_agent = UserAgent()

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

url = 'https://www.google.com.tw/maps/dir/台北市南港區中坡南路47號1樓/台北市南港區研究院路二段128號1樓(學術活動中心)'
html_doc = requests.get(url, headers=get_header())
```



#### thread

Use threads to allow the process to send a large number of requests at simultaneously waiting for each server response.

```python
import threading

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
        threads.append(threading.Thread(target = job, args = (i, j, url, adjacency_matrix)))
        threads[-1].start()
        sleep(0.05)
    for thread in threads:
        thread.join()
```



## result

```json
{
    "中坡": {
        "中坡": 0,
        "中研": 5.5,
        "中貿": 4.7,
        "玉成": 2.2,
        "玉德": 0.35
    },
    "中研": {
        "中坡": 6.0,
        "中研": 0,
        "中貿": 3.2,
        "玉成": 4.8,
        "玉德": 5.7
    },
    "中貿": {
        "中坡": 4.8,
        "中研": 2.5,
        "中貿": 0,
        "玉成": 3.1,
        "玉德": 4.5
    },
    "玉成": {
        "中坡": 2.5,
        "中研": 4.4,
        "中貿": 2.7,
        "玉成": 0,
        "玉德": 2.3
    },
    "玉德": {
        "中坡": 0.35,
        "中研": 5.3,
        "中貿": 4.5,
        "玉成": 2.0,
        "玉德": 0
    }
}
```

![image-20230310094703028](C:\Users\nike\AppData\Roaming\Typora\typora-user-images\image-20230310094703028.png)