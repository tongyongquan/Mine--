##项目说明:
基于python3.6,flask,mysql 的web个人网站开发.实现云笔记功能
项目可配置爬虫爬取GitHub数据


##项目配置:
# mysql脚本
    '''
    grant all privileges on *.* to 'user'@'%' identified by 'happy100';
    flush privileges;
    CREATE DATABASE Mine charset utf8;
    '''

#安装requirements.txt中的类库内容，执行pip install -r requirements.txt.

#初始化SQLAlchemy版本库 python manage.py db init
#生成迁移文件  python manage.py db migrate
#映射到数据库  python manage.py db upgrade

#运行Mine_bysj.py


#2018-2-16