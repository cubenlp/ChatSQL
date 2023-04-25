# ChatSQL
基于ChatGLM-6B,实现nl2sql，直连数据库并返回查询结果
目前仅支持MYSQL语法,后续支持多数据库语法查询

## ✨整体思路
![](figure/ChatSQL技术流程图.png)
整体思路如上，目前采用yaml文件代替Table_info表结构

## 🎬开始
```
git clone git@github.com:yysirs/ChatSQL.git
cd ChatSQL
conda create -n chatsql python=3.9
conda activate chatsql
pip install -r requirements.txt
# 生成本地数据库+插入数据
python local_database.py
# 生成SQL
python main_gui.py
```

## 😁效果演示
![](figure/ChatSQL演示图2.png)

## 👍 特性
- 🛒 支持多表联查
- 🖼️ 2023/04/24 支持web前端
- 🎉 2023/04/24 支持yaml自定义数据库schema
- 😁 2023/04/25 支持yaml自定义数据
- 🎗️ 2023/04/25 支持直连本地数据库查询,验证SQL是否正确

## 各种类型的查询
```
# 单表多条件查询
请帮我查询在2019年的货物销售的净收益率大于10的货物名称

# 两表联查
请帮我查询在2019年的净收益率大于10并且销售量大于100的销售负责人名字

# 两表多条件联查
请帮我查询在2019年的货物的净收益率大于10并且销售量大于100并且销售负责人业绩大于1000的销售负责人名字

# max

# min

# COUNT

# AVG

# GROUP BY HAVING

# ORDER BY

# SUM	

# like

# TOP limit

```
##  TODO
* [x] 增加web前端
* [x] yaml可配置数据库schema
* [x] 采用sqlite本地数据库操作,验证SQL语句是否正确
* [ ] 优化各类查询语句，如：ORDER BY、GROUP BY / HAVING 等复杂查询
* [ ] 优化相似度查询模块
* [ ] Docker部署
* [ ] 其他SQL语法查询，如：ORACLE(关系型数据库)、Cypher(图数据库)

## ❤️致谢
- [ChatGLM-6B](https://github.com/THUDM/ChatGLM-6B):ChatGLM-6B模型提供大语言模型能力
