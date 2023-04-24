import os
import re
import copy
import torch
os.environ["CUDA_VISIBLE_DEVICES"] = "0"
import platform
from transformers import AutoTokenizer, AutoModel
from utility.db_tools import Cur_db
from utility.loggers import logger
from sentence_transformers import util
from prompt import table_schema, embedder,corpus_embeddings, corpus,In_context_prompt

tokenizer = AutoTokenizer.from_pretrained("ChatGlm-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("ChatGlm-6b", trust_remote_code=True).half().cuda()
model = model.eval() 
os_name = platform.system()


# chatbot_prompt = """
# 你是一个文本转SQL的生成器，你的主要目标是尽可能的协助用户，将输入的文本转换为正确的SQL语句。
# 上下文开始
# 表名和表字段来自以下表：
# """

query_template = """问: <user_input>
答: 
"""


def main():
    db_con = Cur_db()
    db_con.pymysql_cur()
    print("欢迎使用 ChatGLM-6B 模型，输入内容即可进行对话，clear 清空对话历史，stop 终止程序")
    history = []
    while True:
        chatbot_prompt = """
你是一个文本转SQL的生成器，你的主要目标是尽可能的协助用户将输入的文本转换为正确的SQL语句。
上下文开始
生成的表名和表字段均来自以下表：
"""
        query = input("\n🧑用户：")
        if query == "stop":
            break
        if query == "clear":
            history = []
            command = 'cls' if os_name == 'Windows' else 'clear'
            os.system(command)
            print("欢迎使用 ChatGLM-6B 模型，输入内容即可进行对话，clear 清空对话历史，stop 终止程序")
            continue
        top_k = 3 
        query_embedding = embedder.encode(query, convert_to_tensor=True) # 与6张表的表名和输入的问题进行相似度计算
        cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0] 
        top_results = torch.topk(cos_scores, k=top_k) # 拿到topk=3的表名
        # 组合Prompt
        table_nums = 0 
        for score, idx in zip(top_results[0], top_results[1]):
            # 阈值过滤
            if score > 0.45:
                table_nums += 1
                chatbot_prompt += table_schema[corpus[idx]]
        chatbot_prompt += "上下文结束\n"
        # In-Context Learning
        if table_nums >= 2 and not history: # 如果表名大于等于2个，且没有历史记录，就加上In-Context Learning
            chatbot_prompt += In_context_prompt
        #  加上查询模板
        chatbot_prompt += query_template
        # chatbot_prompt = chatbot_prompt.replace(" ", "")
        # 生成输入的prompt
        copy_query = copy.deepcopy(query)
        if history:
            query = query
        else:
            query = chatbot_prompt.replace("<user_input>", query)
        response, history = model.chat(tokenizer, query, history=history, temperature=0.1) # 生成SQL
        
        response = re.split("```|\n\n", response)
        print(response)
        for text in response:
            if "SELECT" in text:
                response = text
                break
        else:
            response = response[0]
        response = response.replace("\n", " ").replace("``", "").replace("`", "").strip()
        response = re.sub(' +',' ', response)
        print(f"🤖ChatGLM-6B：{response}") 
        if "很抱歉" in response:
            continue
        # 结果查询
        res = db_con.selectMany(response)
        print("result table:", res)
        # query和sql入库
        sql = "INSERT INTO query_sql_result (user_query, gen_sql) VALUES (%s, %s)"
        val = [copy_query, response]
        db_con.insert(sql, val)
        history = []

if __name__ == "__main__":
    main()