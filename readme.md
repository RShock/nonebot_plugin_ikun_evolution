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

或者直接下载拖到插件文件夹里。

你的python版本应当大于3.9。

你的gocqhttp最好为rc3以上，否则可能存在组消息发送为空的情况。

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

在初次运行时，无法正确加载资源。

只需要再运行一次bot，看见
```
nonebot_plugin_ikun_evolution | 【只因进化录】资源载入中
nonebot_plugin_ikun_evolution | 【只因进化录】任务载入完成，共9个任务
nonebot_plugin_ikun_evolution | 【只因进化录】制作表载入完成，共1个配方
nonebot_plugin_ikun_evolution | 【只因进化录】地图载入完成，共42张地图
nonebot_plugin_ikun_evolution | 【只因进化录】帮助载入完成，共11条帮助
nonebot_plugin_ikun_evolution | 【只因进化录】技能载入完成，共38个技能
nonebot_plugin_ikun_evolution | 【只因进化录】敌人载入完成，共30个敌人
nonebot_plugin_ikun_evolution | 【只因进化录】物品载入完成，共7个物品
```
即为载入完成
