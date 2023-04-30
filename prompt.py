"""
Text2SQL机器人·Prompt
"""
import numpy as np
from sentence_transformers import SentenceTransformer, util
from utility.utils import config_dict as DB_CONFIG
from local_database import db_operate

embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# 每张表的表含义和对应的表结构
# table_schema = {"货物销售表,主要存储货物名称、净收益率、损失率、环比增长率、销售量、货物品类、货物仓库、销售负责人名字、销售部门、销售负责人联系方式":
#                  """表1: cargo
# 字段1:cargo_id(货物编号),字段2:cargo_name(货物名称),字段3:year(年份),字段4:net_yield(净收益率%),字段5:loss_rate(损失率%),字段6:month_on_month_growth_rate(环比增长率%),字段7:sales_volume(销售量),字段8:cargo_price(货物单价),字段9:cargo_category(货物品类),字段10:source_cargo(货物来源),字段11:storage_warehouse(货物仓库),字段12:sales_person_name(销售责任人名字),字段13:sales_person_id(销售负责人id),字段14:sales_department(销售部门),字段15:sales_person_numbers(销售负责人联系方式)
# """,
#                 "人员信息表,主要存储销售人员人名、入职时间、当前业绩、职位等级":
#                  """表2: sales
# 字段1:sales_person_id(销售人员id),字段2:sales_person_name(人员名称),字段3:sales_person_level(人员等级),字段4:sales_person_work_date(入职时间),字段5:sales_person_leader_id(人员主管id),字段6:sales_person_leader_name(人员主管名字),字段7:sales_person_number(人员电话),字段8:sales_person_achievement_year(人员业绩年份),字段9:sales_person_achievement(人员业绩),字段10:sales_person_department(人员部门名称),字段11:sales_person_department_id(人员部门id)
# """,
#                 "货物信息表,主要存储货物名称、货物来源地、购买价格、货物大类、货物品类、供应商名称和供应商负责人":
#                 """表3: cargo_info
# 字段1:cargo_info_id(货物信息id),字段2:cargo_id(货物id),字段3:cargo_name(货物名称),字段4:origin_cargo(货物产地),字段5:cargo_purchase_price(货物购买价),字段6:cargo_type(货物大类),字段7:cargo_category(货物品类),字段8:cargo_supply_company(供货公司),字段9:cargo_num(货物数量),字段10:cargo_supply_aftermarket_person(货物售后负责人),字段11:cargo_supply_aftermarket_person_number(货物售后负责人联系电话),字段12:cargo_supply_market_person(货物公司销售负责人),字段13:cargo_supply_market_person_number(货物公司负责人联系电话)
# """,
#                 "部门表,主要存储部门名称、部门职责、部门主管":
#                 """表4: depart_list
# 字段1:department_id(部门id),字段2:department_name(部门名称),字段3:department_duty(部门职责),字段4:department_lead_name(部门负责人名字),字段5:department_lead_name_id(部门负责人id),字段6:department_person_nums(部门人数)
# """,
#                 "购买信息表,主要存储购买公司名称、购买公司街道、购买负责人、购买货物名称和数量以及类型":
#                 """表5: purchase_info
# 字段1:purchase_company_id(货物购买方id),字段2:purchase_company_name(货物购买方名称),字段3:purchase_company_address(货物购买方地址),字段4:purchase_company_person_name(货物购买方负责人人名),字段5:purchase_company_person_numbers(货物购买方负责人联系方式),字段6:purchase_company_person_level(货物购买方负责人职位),字段7:purchase_cargo_name_id(购买货物id),字段8:purchase_cargo_name(购买货物名称),字段9:purchase_cargo_nums(购买货物数量),字段10:purchase_cargo_type(购买货物大类),字段11:purchase_cargo_category(购买货物品类)
# """,
#                 "供应商信息表,主要存储供应商名称、供应商地址、供应商货物名称、入供应商目录日期":
#                  """表6: supply_company
# 字段1:supply_company_id(供货公司id),字段2:supply_company_name(供货公司名称),字段3:supply_company_address(供货公司地址),字段4:supply_company_product_id(供货公司货物id),字段5:supply_company_product_name(供货公司货物名称),字段6:supply_company_date(供货公司入名录时间)
# """}


# corpus = list(table_schema.keys())

# corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)


chatbot_prompt = """
你是一个文本转SQL的生成器，你的主要目标是尽可能的协助用户将输入的文本转换为正确的SQL语句。
上下文开始
生成的表名和表字段均来自以下表：
"""

# chatbot_prompt = """
# 你是一个文本转SQL的生成器，你的主要目标是尽可能的协助用户，将输入的文本转换为正确的SQL语句。
# 上下文开始
# 表名和表字段来自以下表：
# 表1: cargo
# 字段1:cargo_id(货物编号),字段2:cargo_name(货物名称),字段3:year(年份),字段4:net_yield(净收益率%),字段5:loss_rate(损失率%),字段6:month_on_month_growth_rate(环比增长率%),字段7:sales_volume(销售量),字段8:cargo_price(货物单价),字段9:cargo_category(货物品类),字段10:source_cargo(货物来源),字段11:storage_warehouse(货物仓库),字段12:sales_person_name(销售责任人名字),字段13:sales_person_id(销售负责人id),字段14:sales_department(销售部门),字段15:sales_person_numbers(销售负责人联系方式)
# 表2: sales
# 字段1:sales_person_id(销售负责人id),字段2:sales_person_name(人员名称),字段3:sales_person_level(人员等级),字段4:sales_person_work_date(入职时间),字段5:sales_person_leader_id(人员主管id),字段6:sales_person_leader_name(人员主管名字),字段7:sales_person_number(人员电话),字段8:sales_person_achievement_year(人员业绩年份),字段9:sales_person_achievement(人员业绩),字段10:sales_person_department(人员部门名称),字段11:sales_person_department_id(人员部门id)
# 表3: cargo_info
# 字段1:cargo_info_id(货物信息id),字段2:cargo_id(货物id),字段3:cargo_name(货物名称),字段4:origin_cargo(货物产地),字段5:cargo_purchase_price(货物购买价),字段6:cargo_type(货物大类),字段7:cargo_category(货物品类),字段8:cargo_supply_company(供货公司),字段9:cargo_num(货物数量),字段10:cargo_supply_aftermarket_person(货物售后负责人),字段11:cargo_supply_aftermarket_person_number(货物售后负责人联系电话),字段12:cargo_supply_market_person(货物公司销售负责人),字段13:cargo_supply_market_person_number(货物公司负责人联系电话)
# 表4: depart_list
# 字段1:department_id(部门id),字段2:department_name(部门名称),字段3:department_duty(部门职责),字段4:department_lead_name(部门负责人名字),字段5:department_lead_name_id(部门负责人id),字段6:department_person_nums(部门人数)
# 表5: purchase_info
# 字段1:purchase_company_id(货物购买方id),字段2:purchase_company_name(货物购买方名称),字段3:purchase_company_address(货物购买方地址),字段4:purchase_company_person_name(货物购买方负责人人名),字段5:purchase_company_person_numbers(货物购买方负责人联系方式),字段6:purchase_company_person_level(货物购买方负责人职位),字段7:purchase_cargo_name_id(购买货物id),字段8:purchase_cargo_name(购买货物名称),字段9:purchase_cargo_nums(购买货物数量),字段10:purchase_cargo_type(购买货物大类),字段11:purchase_cargo_category(购买货物品类)
# 表6: supply_company
# 字段1:supply_company_id(供货公司id),字段2:supply_company_name(供货公司名称),字段3:supply_company_address(供货公司地址),字段4:supply_company_product_id(供货公司货物id),字段5:supply_company_product_name(供货公司货物名称),字段6:supply_company_date(供货公司入名录时间)
# 上下文结束
# 问: 请帮我查询所有的货物名称
# 答: SELECT cargo_name FROM cargo
# 问: 请帮我查询在2019年的净收益率大于10并且销售量大于100并且业绩大于1000的销售负责人名字
# 答: SELECT sales.sales_person_name FROM sales INNER JOIN cargo on sales.sales_person_id = cargo.sales_person_id WHERE cargo.year = 2019 AND cargo.net_yield > 10 AND cargo.sales_volume > 100 AND sales.sales_person_achievement > 1000
# 问: 文本转SQL: <user input>
# 答: 
# """

# 一些学习的例子
In_context_prompt = """问: 请帮我查询所有的货物名称
答: SELECT cargo_name FROM cargo;
问: 请帮我查询在2019年的净收益率大于10并且销售量大于100并且业绩大于1000的销售负责人名字
答: SELECT sales.sales_person_name FROM sales INNER JOIN cargo on sales.sales_person_id = cargo.sales_person_id WHERE cargo.year = 2019 AND cargo.net_yield > 10 AND cargo.sales_volume > 100 AND sales.sales_person_achievement > 1000;
问: 请帮我查询购买"板材"货物的公司名称
答: SELECT purchase_company_name FROM purchase_info WHERE purchase_cargo_name = "板材";
"""

query_template = """问: <user_input>
答: 
"""

# yaml解析
TABLE = DB_CONFIG["TABLE"]
table_schema = {}

for table_name in TABLE.keys():
    # table描述拼接
    table_info = """"""
    table_info += "表名:" + table_name + "\n"
    table_info += "字段:"
    for idx, filed in enumerate(TABLE[table_name]["field"].items()):
        if idx == len(TABLE[table_name]["field"].items()) - 1:
            table_info += filed[0] + "(" + filed[1][0] + ")"
        else:
            table_info += filed[0] + "(" + filed[1][0] + "),"

    table_schema[TABLE[table_name]["info"]] = table_info

# 获取表的描述信息
corpus = list(table_schema.keys())

# 向量化
corpus_embeddings = embedder.encode(corpus, convert_to_tensor=True)