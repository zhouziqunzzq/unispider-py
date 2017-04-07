import twitter
import requests
import re
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
    job_url = url + 'api/jobs/spider/2'
    re1 = re.compile(r'</?blockquote[^>]*>', re.S)
    re2 = re.compile(r'</?p[^>]*>', re.S)
    re3 = re.compile(r'&mdash;.*\(@.*\).*<a[^>]+>.*</a>', re.S)
####################


def CleanTweet(tweet):
    tweet = re1.sub('', tweet)
    tweet = re2.sub('', tweet)
    tweet = re3.sub('', tweet)
    return tweet


def PostJob(url, pwd, since_id):
    try:
        d = {
            'pwd': pwd,
            'max_id': 0,
            'since_id': since_id,
            'type': 2
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


def PostTweetHtmlContent(url, pwd, job_list):
    try:
        api = twitter.Api(consumer_key=cf.get('twitter', 'consumer_key'),
                          consumer_secret=cf.get('twitter', 'consumer_secret'),
                          access_token_key=cf.get('twitter', 'access_token_key'),
                          access_token_secret=cf.get('twitter', 'access_token_secret'))
        for t in job_list:
            tweet = api.GetStatusOembed(status_id=t, omit_script=True)
            tweet = CleanTweet(tweet['html'])
            d = {
                'pwd': pwd,
                'html_content': tweet,
                '_method': 'PUT'
            }
            r = requests.post(url=url + '/' + t, data=d)
            print("Rst:\n")
            print(r.text)
    except:
        return


def main():
    print("Geting jobs...\n")
    job = GetJob(job_url, api_pwd)
    if len(job) == 0:
        exit()
    print("job_list=")
    print(job)
    try:
        print("Updating tweets html_content...\n")
        PostTweetHtmlContent(tweet_url, api_pwd, job)
    except:
        exit()
    #print("Updating job status... since_id=" + str(job))
    #PostJob(job_url, api_pwd, job['max_id'])

main()
