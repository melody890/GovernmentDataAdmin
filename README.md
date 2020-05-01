# Government Data Admin

## 项目结构

```
GovernmentDataAdmin/
	chart/ 	# 可视化app
	DataAdmin/ # 设置
	event/ 	# 事件登记处理app  
        home/   #主页app
	kgraph/ # 知识图谱app
	static/ # 静态文件
		chart/	# 对应app的html文件
		event/
                home/   # 主页及通用视图   
		kgraph/
		user/
		base.html	# 基本模板
		footer.html     # 页脚
		header.html	# 页眉
		sidebar.html    # 侧边栏
	templates/  # 前端html文件
	user/ # 用户app
        webinfo/    # 爬虫app
	db
	manage.py
	README.md
	requirement.txt
```



## 待完成功能

- 破解微博登录
- 实现多页爬虫搜索
- 知识图谱模型构建
- 知识图谱再次点击取消节点
- 网页上线
- 数据库迁移



## 完成功能

- ### 可视化

  - 近一周各社区各类型事件数量折线图
  - 近一年日历事件热点图
  - 各类型事件数量饼状图
  - 不同性质事件执行情况旭日图
  - 热点词云
  - 热点地图
  - 实时事件滚动显示

- ### 知识图谱

  - 首页词云，支持点击跳转
  - 支持关键词检索
  - 支持相关节点点击扩展

- ### 事件处理

  - 事件上传功能
  - 事件处置功能
  - 列表筛选

- ### 用户

  - 用户注册、登录、退出
  - 用户信息更改
  - 头像上传

- ### 微博爬虫

  - 信息页面解析+内容提取

