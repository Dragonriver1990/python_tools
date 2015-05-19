##Python logging module

------------------------
日志在项目中的作用不言而喻，这里对python logging模块做下介绍，主要就是根据工作中得项目做的总结。

------------------------

这里主要讲的是python logging高级日志模式。日志的配置文件单独存放在一个文件`logging.conf`中，日志的操作函数写在`log.py`中。

在`log.py`中，`logging.config.fileConfig(conf_file, defaults={"logpath": log_path})`，加载配置文件。

谢了好久，突然在网上看到了更详细的东西，直接去浏览吧。

http://my.oschina.net/leejun2005/blog/126713



