# 只因进化录

移植自真寻的[只因进化录](https://github.com/RShock/ikun_evolution)

## 安装

### 插件安装
```
pip install nonebot_plugin_ikun_evolution
```
在 nonebot2 项目中设置 load_plugin()
```
nonebot.load_plugin('nonebot_plugin_ikun_evolution')
```

### 数据库配置

你需要安装一个[postgresql数据库](https://hibikier.github.io/zhenxun_bot/docs/installation_doc/install_postgresql.html)才能进行游戏

安装完毕后，在`env.dev`里填上刚刚的数据库链接
```
psql = "postgresql://名字:密码@127.0.0.1:5432/数据库名字"
```

如果按真寻教程就是
```
psql = "postgresql://uname:zhenxun@127.0.0.1:5432/testdb"
```

这步有点困难，好处是再也不用担心误删数据库了。请加油罢

## 已知问题

pip install的话，初始运行报找不到json文件夹错误

去相应目录下创建json文件夹（我明天修一下，pypi把我的空文件夹删了...）(应该修好了）

第一次运行没有成功加载配置文件，需要第二次运行才可以

谜，明天我也修一下
