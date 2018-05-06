# encoding:utf-8
    #github_spider.py
    #爬虫页面蓝图
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
from flask import Blueprint, render_template, request
from app import db
from models import *
spider = Blueprint('spider',__name__)


@spider.route('/collect',methods=['POST','GET'])
def collect():

    if request.method == 'GET':
        pass
    else:
        pass


@spider.route('/github',methods=['POST','GET'])
def github_spider():
    nav_labels = Label.query.filter().all()

    if request.method=='GET':
        urls = get_urls(1, 'python')
        articles = []
        for url in urls:
            ar_temp = {
                'name': url[19:],
                'url': url
            }
            articles.append(ar_temp)
        return render_template('frontend/spiderlist.html', nav_labels=nav_labels,articles=articles)
    else:
        pass


def get_urls(page,question):
    links=[]
    for pagenum in range(1,page+1):
        print ('get page%d'%pagenum+r"'s urls")
        html = requests.get("https://github.com/search?p=%d&q=%s"%(pagenum,question)+'&type=Repositories&utf8=%E2%9C%93')
        bsObj = BeautifulSoup(html.text,"html.parser")
        for link in bsObj.find('ul',{'class':'repo-list'}).findAll('h3'):
            links.append('https://github.com/'+link.get_text().strip())
    return links


def getNewsDetail(newsurl):
    article={}
    res = requests.get(newsurl,verify=False)
    res.encoding='utf-8'
    soup=BeautifulSoup(res.text,'html.parser')

    article['author']=soup.select('.author')[0].text
    if soup.select('.plain')[0].text:
        article['info']=soup.select('.plain')[0].text
    else :
        article['info']=''
    return article

