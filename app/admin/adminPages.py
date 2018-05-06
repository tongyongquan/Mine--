# encoding:utf-8
    #adminPages.py
    #后台管理页面蓝图
from datetime import timedelta
from flask import Blueprint, request, config
import config
from functools import wraps
from flask import redirect, url_for, g, render_template, session
from app import app,page_content
from models import *

admin = Blueprint('admin',__name__)


# 在app入栈后和请求前之间的操作
@app.before_request
def before_request():
    user_id = session.get('user_id')
    g.user = None
    if user_id:
        session_user = User.query.filter(User.id == user_id).first()
        if session_user:
            # app的全局变量g.user
            g.user = session_user
            page_content['nav_label'] = Label.query.filter().all()


# 用户密码MD5加密
def create_md5(str_passwd):
    import hashlib
    m = hashlib.md5()
    m.update(str_passwd.encode('utf8'))
    return m.hexdigest()


#登录限制装饰器
def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if g.user:
            return func(*args, **kwargs)
        else:
            return redirect(url_for('admin.login'))

    return wrapper


#管理员登录蓝图
@admin.route('/login/',methods=['POST','GET'])
def login():
    if request.method == 'GET':
        return render_template('admin/login.html')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        password_hash = create_md5(password)
        login_user = User.query.filter(User.username == username,
                                       User.password == password_hash).first()
        if login_user:
            session.permanent = True
            # 设置回话保存时间
            app.permanent_session_lifetime = timedelta(
                days=config.session_lifetime)

            session['user_id'] = login_user.id

            # 将用户名保存到页面信息
            page_content['username'] = login_user.username
            page_content['user_authority']=login_user.authority
            return redirect(url_for('admin.index'))
        else:
            page_content['error'] = u'用户名或密码错误!'
            return render_template('admin/error.html')


#注册管理员蓝图
@admin.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template(
            'admin/register.html')
    else:
        page_content['error'] = u'验证码错误!'

        username = request.form.get('username')
        password = request.form.get('password')
        if username == '' or password == '':
            page_content['error'] = u'用户名或密码为空!'
            return render_template('admin/error.html', **page_content)
        re_password = request.form.get('re_password')
        if password != re_password:
            page_content['error'] = u'两次密码不一致!'
            return render_template('admin/error.html', **page_content)
        # avatar = request.form.get('avatar')
        register_user = User.query.filter(User.username == username).first()
        if register_user:
            page_content['error'] = u'用户已存在!'
            return render_template('admin/error.html', **page_content)
        register_user = User(username=username, password=create_md5(password),authority='admin' )
        del page_content['error']
        db.session.add(register_user)
        db.session.commit()
        return redirect(url_for('admin.login'))


#访问后台管理主页蓝图
@admin.route('/')
@login_required
def index():
    index_article = Article.query.filter().order_by(Article.modify_time).offset(
        0).limit(14).all()
    nav_labels = Label.query.filter().all()
    return render_template('admin/index.html',articles=index_article)


#注销登录蓝图
@admin.route('/logout')
@login_required
def logout():
    session.clear()
    page_content.clear()
    return redirect(url_for('admin.index'))


#添加笔记蓝图
@admin.route('/article/add', methods=['POST', 'GET'])
@login_required
def article_add():
    if request.method == 'GET':
        return render_template('admin/article/add_article_ueditor.html')
    else:
        title = request.form.get('title')
        info = request.form.get('info')
        label_id = request.form.get('label_id')
        form_content = request.form.get('content')
        article_model = Article(title=title, info=info, content=form_content,
                                label_id=label_id, author_id=g.user.id)
        article_model.author = g.user
        db.session.add(article_model)
        db.session.commit()
        return redirect(url_for('admin.index'))


#管理笔记列表蓝图
@admin.route('/list/<label_id>', methods=['GET', 'POST'])
@login_required
def list(label_id):
    page_content['select'] = label_id
    kw = {
        'articles': Article.query.filter(Article.label_id == label_id).order_by(
            -Article.id).all(),
        'label_name': Label.query.filter(Label.id == label_id).first().name
    }
    if request.method == 'GET':
            return render_template('admin/list.html', **kw)

    else:
        pass

#查看笔记详情蓝图
@admin.route('/article/<article_id>', methods=['GET', 'POST'])
@login_required
def article(article_id):
    article_model = Article.query.filter(Article.id == article_id).first()
    if request.method == 'GET':
        if not article_model:
            page_content['error'] = u'文章不存在!'
            return render_template('admin/error.html')
        return render_template('admin/article.html', article=article_model)
    else:
        pass


#修改笔记蓝图
@admin.route('/article/edit/<article_id>', methods=['POST', 'GET'])
@login_required
def article_edit(article_id):
    article_model = Article.query.filter(Article.id == article_id).first()
    if request.method == 'GET':
        return render_template('admin/article/edit.html', article=article_model)
    else:
        title = request.form.get('title')
        info = request.form.get('info')
        label_id = request.form.get('label_id')
        form_content = request.form.get('content')
        article_model.title = title
        article_model.info = info
        article_model.content = form_content
        article_model.label_id = label_id
        article_model.modify_time = datetime.now()
        db.session.commit()
        return redirect(url_for('admin.index'))

#删除笔记蓝图
@admin.route('/article/delete/<article_id>', methods=['POST', 'GET'])
@login_required
def article_delete(article_id):
    article_model = Article.query.filter(Article.id == article_id).first()
    if request.method == 'GET':
        db.session.delete(article_model)
        db.session.commit()
        return redirect(url_for('admin.index'))
    else:
        pass


#删除标签蓝图
@admin.route('/label/delete/<label_id>')
@login_required
def label_delete(label_id):
    label = Label.query.filter(Label.id == label_id).first()
    if label:
        children_label = Label.query.filter(Label.parent_id == label_id).all()
        other_label = Label.query.filter(Label.name == '其他').first()
        for child in children_label:
            child.parent = other_label
        db.session.delete(label)
        db.session.commit()
    return redirect(url_for('admin.label_add'))


#增加标签蓝图
@admin.route('/label/add', methods=['GET', 'POST'])
@login_required
def label_add():
    if request.method == 'GET':
        all_label = Label.query.all()
        page_content['all_label'] = all_label
        return render_template('admin/label/add.html', **page_content)
    else:
        name = request.form.get('name')
        if name == '':
            page_content['error'] = u'标签名不能为空!'
            return render_template('admin/error.html', **page_content)
        temp = Label.query.filter(Label.name == name).first()
        if temp:
            page_content['error'] = u'已经存在该标签名!'
            return render_template('admin/error.html', **page_content)
        parent_id = request.form.get('parent_id')
        parent = Label.query.filter(Label.id == parent_id).first()
        label = Label(name=name)
        label.parent = parent
        db.session.add(label)
        db.session.commit()
        return redirect(url_for('admin.label_add'))


#修改标签蓝图
@admin.route('/label/edit/<label_id>', methods=['GET', 'POST'])
@login_required
def label_edit(label_id):
    label = Label.query.filter(Label.id == label_id).first()

    if not label:
        page_content['error'] = u'标签不存在!'
        return render_template('admin/error.html', **page_content)
    page_content['label'] = label
    if request.method == 'GET':
        all_label = Label.query.filter(Label.id != label_id).all()
        page_content['all_label'] = all_label
        return render_template('admin/label/edit.html', **page_content)
    else:
        name = request.form.get('name')
        if name == '':
            page_content['error'] = u'标签名不能为空!'
            return render_template('admin/error.html', **page_content)
        temp = Label.query.filter(Label.name == name).first()
        if temp and temp != label:
            page_content['error'] = u'已经存在该标签名!'
            return render_template('admin/error.html', **page_content)
        parent_id = request.form.get('parent_id')
        label.name = name
        parent = Label.query.filter(Label.id == parent_id).first()
        label.parent = parent
        db.session.commit()
        return redirect(url_for('admin.label_add'))


