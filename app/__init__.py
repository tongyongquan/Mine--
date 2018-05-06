from flask import Flask, session
import config
from flask_sqlalchemy import SQLAlchemy
#为解决循环调用,在这定义db
db = SQLAlchemy()

app = Flask(__name__)
app.config.from_object(config)
db.init_app(app)

# 页面信息
page_content = {
    'nav_label': [],  # 标签列表,存储所有标签对象
    'select': 100  # 设置标签的选中状态
}

# 添加jinja的全局变量字典,自动更改
app.jinja_env.globals['session'] = session
app.jinja_env.globals['page_content'] = page_content  # 全局字典里的页面信息字典
app.jinja_env.auto_reload = True


from app.admin.adminPages import admin
from app.frontend.frontendPages import frontend
from app.uploader.upload import upload
from app.spider.github_spider import spider

#注册后台管理页面蓝图
app.register_blueprint(admin,url_prefix='/admin')

#注册前端页面蓝图
app.register_blueprint(frontend)

#注册上传接口蓝图
app.register_blueprint(upload)

#注册爬虫功能
app.register_blueprint(spider)