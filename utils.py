"""
@Author: Liushu
@Date: 2023/04/30
"""
import re
import torch
from sentence_transformers import util
from prompt import embedder, corpus_embeddings, table_schema, corpus, In_context_prompt


# 检索问句答案可能存在表结构
def retrieval_related_table(input_prompt, input, history=None, top_k=3, is_moss=False):
    query_embedding = embedder.encode(input, convert_to_tensor=True) # 与6张表的表名和输入的问题进行相似度计算
    cos_scores = util.cos_sim(query_embedding, corpus_embeddings)[0] 
    top_results = torch.topk(cos_scores, k=top_k) # 拿到topk=3的表名
    # 组合Prompt
    table_nums = 0 
    for score, idx in zip(top_results[0], top_results[1]):
        # 阈值过滤
        if score > 0.45:
            table_nums += 1
            input_prompt += table_schema[corpus[idx]]
        input_prompt += "上下文结束\n"
    # In-Context Learning
    if is_moss:
        In_context_prompt = In_context_prompt.replace("问: ", "<|Human|>: ").replace("答:", "<eoh>")
    if table_nums >= 2 and not history: # 如果表名大于等于2个，且没有历史记录，就加上In-Context Learning
        input_prompt += In_context_prompt
    return input_prompt


def obtain_sql(response):
    response = re.split("```|\n\n", response)
    for text in response:
        if "SELECT" in text:
            response = text
            break
    else:
        response = response[0]
    response = response.replace("\n", " ").replace("``", "").replace("`", "").strip()
    response = re.sub(' +',' ', response)
    return response


def execute_sql(response, chatbot, dboperate):
    if "SELECT" in response:
        try:
            sql_stauts = "sql语句执行成功,结果如下:"
            sql_result = dboperate.query_data(response)
            sql_result = str(sql_result)
        except Exception as e:
            sql_stauts = "sql语句执行失败"
            sql_result = str(e)
        chatbot[-1] = (chatbot[-1][0], 
                       chatbot[-1][1] + "\n\n"+ "===================="+"\n\n" + sql_stauts + "\n\n" + sql_result)
    return chatbot