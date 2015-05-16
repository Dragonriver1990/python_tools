Redis Python Client
======================

---------------------
类 StrictRedis：是对Redis协议的实现，它提供了所有redis command 的python接口，大部分可以使用的command，

类StrictRedis都有实现

其中涉及到的实例代码在我的git上均可以找到 (https://github.com/Dragonriver1990/python_tools.git)
 
---------------------


* `__init__(self,host='locahost',port=6379,db=0,password=None...)`

	初始化函数中的参数中，`host`和`port`为必填项，`db`和`passeord`是可选项，根据你的`Redis Server`配置情况而定

* `__repr__`格式化返回创建对象


* `pipeline`管道是redis在提供单个请求中缓冲多条服务器命令的基类的子类。它通过减少服务器-客户端之间反复的TCP数据库包，从而大大提高了执行批量命令的功能

```
	def flush(self):
        keys = self._redis.keys("%s*" % self.prefix)
        pipe = self._redis.pipeline()
        for key in keys:
            pipe.delete(key)
        pipe.execute()
```



=====================

=====================
###redis command 分类

Redis 按照key和values，可以讲命令分为六类：Key   String Hash  List   Set    SortedSet

现在分别对每类命令做概述。
