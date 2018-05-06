# encoding:utf-8
    #frontendPages.py
    #前端页面蓝图
from flask import Blueprint, request
from app import page_content
from flask import render_template

from models import *

frontend = Blueprint('frontend',__name__)


#前端列表蓝图
@frontend.route('/frontendlist/<label_id>', methods=['GET', 'POST'])
def frontendlist(label_id):
    page_content['select'] = label_id
    nav_labels = Label.query.filter().all()

    kw = {
        'articles': Article.query.filter(Article.label_id == label_id).order_by(
            -Article.id).all(),
        'label_name': Label.query.filter(Label.id == label_id).first().name
    }
    if request.method == 'GET':
         return render_template('frontend/list.html', nav_labels=nav_labels,**kw)
    else:
        pass


#前端主页蓝图
@frontend.route('/')
def index():
    index_article = Article.query.filter().order_by(Article.modify_time).offset(
        0).limit(14).all()
    nav_labels = Label.query.filter().all()
    return render_template('frontend/index.html', articles=index_article,
                           nav_labels=nav_labels)

#查看笔记详情蓝图
@frontend.route('/article/<article_id>', methods=['GET', 'POST'])
def article(article_id):
    article_model = Article.query.filter(Article.id == article_id).first()
    if request.method == 'GET':
        if not article_model:
            page_content['error'] = u'文章不存在!'
            return render_template('admin/error.html')
        return render_template('admin/article.html', article=article_model)
    else:
        pass

