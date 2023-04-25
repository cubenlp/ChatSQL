# ChatSQL
实现nl2sql，直连数据库并返回查询结果

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
![](figure/ChatSQL演示图2.jpg)

## 👍 特性
- 🛒 支持多表联查
- 🖼️ 2023/04/24 支持web前端
- 🎉 2023/04/24 支持yaml自定义数据库schema
- 😁 2023/04/25 支持yaml自定义数据
- 🎗️ 2023/04/25 支持直连本地数据库查询,验证SQL是否正确


##  TODO
* [x] 增加web前端
* [x] yaml可配置数据库schema
* [x] 采用sqlite本地数据库操作,验证SQL语句是否正确
* [ ] 优化各类查询语句，如：ORDER BY、GROUP BY / HAVING 等复杂查询