import twitter
import requests
import ConfigParser
import os
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
    job_url = url + 'api/jobs/spider/1'
    tw_owner = cf.get('target', 'goshujinsama')
####################


def PostJob(url, pwd, max_id, since_id):
    try:
        d = {
            'pwd': pwd,
            'max_id': max_id,
            'since_id': since_id,
            'type': 1
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


def PostTweetInit(url, pwd, tweets):
    max_id = '0'
    since_id = '0'
    try:
        if len(tweets) != 0:
            since_id = tweets[0].id_str
        for t in tweets:
            max_id = t.id_str
            d = {
                'pwd': pwd,
                'data': t
            }
            r = requests.post(url=url, data=d)
            print("Rst:\n")
            print(r.text)
        return [max_id, since_id]
    except:
        return [-1, -1]


def PostTweet(url, pwd, oldtweets, newtweets):
    max_id = '0'
    since_id = '0'
    try:
        for t in oldtweets:
            max_id = t.id_str
            d = {
                'pwd': pwd,
                'data': t
            }
            r = requests.post(url=url, data=d)
            print("Rst:\n")
            print(r.text)
        if len(newtweets) != 0:
            since_id = newtweets[0].id_str
        for t in newtweets:
            d = {
                'pwd': pwd,
                'data': t
            }
            r = requests.post(url=url, data=d)
            print("Rst:\n")
            print(r.text)
        return [max_id, since_id]
    except:
        return [-1, -1]


def main():
    print("Geting jobs...\n")
    job = GetJob(job_url, api_pwd)
    if job == '-1' or job['max_id'] == '-1':
        exit()
    print("max_id=" + job['max_id'] + "\n")
    print("since_id=" + job['since_id'] + "\n")
    try:
        print("Retriving tweets...\n")
        api = twitter.Api(consumer_key=cf.get('twitter', 'consumer_key'),
                          consumer_secret=cf.get('twitter', 'consumer_secret'),
                          access_token_key=cf.get('twitter', 'access_token_key'),
                          access_token_secret=cf.get('twitter', 'access_token_secret'))
        if job['max_id'] == '0' and job['since_id'] == '0':
            tweets = api.GetUserTimeline(screen_name=tw_owner)
            print("Post init tweets...\n")
            [max_id, since_id] = PostTweetInit(tweet_url, api_pwd, tweets)
        else:
            oldtweets = api.GetUserTimeline(screen_name=tw_owner, max_id=str(int(job['max_id']) - 1))
            newtweets = api.GetUserTimeline(screen_name=tw_owner, since_id=job['since_id'])
            print("Post tweets...\n")
            [max_id, since_id] = PostTweet(tweet_url, api_pwd, oldtweets, newtweets)
    except:
        exit()
    if since_id == '0':
        since_id = job['since_id']
    print("Updating job status... max_id=" + max_id + ", since_id=" + since_id)
    PostJob(job_url, api_pwd, max_id, since_id)

main()
