import requests
import ConfigParser
import os
import time
####################
cf = ConfigParser.ConfigParser()
if not os.path.exists('./spider.cfg'):
    print("Unable to find config file! Check if you forget to rename .cfg.example.")
    exit()
else:
    cf.read('spider.cfg')
    api_pwd = cf.get('api', 'pwd')
    url = cf.get('api', 'url')
    tweet_url = url + 'api/tweets'
    job_url = url + 'api/jobs/spider/3'
twimg_remote_url = 'https://pbs.twimg.com/media/'
img_local_save_path = '/var/www/unispider-sora/public/img/twimg/'
####################


def PostJob(url, pwd, img_id):
    try:
        d = {
            'pwd': pwd,
            'img_id': img_id,
            'type': 3
        }
        r = requests.post(url=url, data=d)
        print("Rst:\n")
        print(r.text)
    except:
        return -1


def GetJob(url, pwd):
    try:
        r = requests.get(url + '?pwd=' + pwd)
        r = r.json()
        return r
    except:
        return -1


def GetImg(img_id, path, twimg_url):
    if not os.path.exists(path):
        os.makedirs(path)
    try:
        r = requests.get(url=twimg_url+img_id, stream=True)
        with open(path + img_id, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
                    f.flush()
            f.close()
            return img_id
    except:
        return -1


def main():
    t = time.time()
    while True:
        if time.time() - t > 60:
            print("Long live spider3! Exiting...")
            return
        print("Geting jobs...\n")
        job = GetJob(job_url, api_pwd)
        if job == '-1':
            exit()
        if job['msg'] == 'fin':
            print("All jobs cleared currently...")
            time.sleep(5)
            continue
        else:
            img_id = job['job']['img_id']
            print("Retriving image " + img_id)
            if GetImg(img_id, img_local_save_path, twimg_remote_url) != -1:
                print("Download completed, reporting job...")
                PostJob(job_url, api_pwd, img_id)

main()