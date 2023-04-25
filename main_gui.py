import os
import re
os.environ["CUDA_VISIBLE_DEVICES"] = "4"
import torch
from transformers import AutoModel, AutoTokenizer
import gradio as gr
import mdtex2html
import platform
from transformers import AutoTokenizer, AutoModel
from utility.utils import config_dict
from utility.loggers import logger
from sentence_transformers import util
from local_database import db_operate
from prompt import table_schema, embedder,corpus_embeddings, corpus,In_context_prompt, query_template

tokenizer = AutoTokenizer.from_pretrained("/home/liushu/program/ChatGLM-6B/ChatGlm-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("/home/liushu/program/ChatGLM-6B/ChatGlm-6b", trust_remote_code=True).half().cuda()
model = model.eval()


"""Override Chatbot.postprocess"""

def postprocess(self, y):
    if y is None:
        return []
    for i, (message, response) in enumerate(y):
        y[i] = (
            None if message is None else mdtex2html.convert((message)),
            None if response is None else mdtex2html.convert(response),
        )
    return y

gr.Chatbot.postprocess = postprocess

def parse_text(text):
    """copy from https://github.com/GaiZhenbiao/ChuanhuChatGPT/"""
    lines = text.split("\n")
    lines = [line for line in lines if line != ""]
    count = 0
    for i, line in enumerate(lines):
        if "```" in line:
            count += 1
            items = line.split('`')
            if count % 2 == 1:
                lines[i] = f'<pre><code class="language-{items[-1]}">'
            else:
                lines[i] = f'<br></code></pre>'
        else:
            if i > 0:
                if count % 2 == 1:
                    line = line.replace("`", "\`")
                    line = line.replace("<", "&lt;")
                    line = line.replace(">", "&gt;")
                    line = line.replace(" ", "&nbsp;")
                    line = line.replace("*", "&ast;")
                    line = line.replace("_", "&lowbar;")
                    line = line.replace("-", "&#45;")
                    line = line.replace(".", "&#46;")
                    line = line.replace("!", "&#33;")
                    line = line.replace("(", "&#40;")
                    line = line.replace(")", "&#41;")
                    line = line.replace("$", "&#36;")
                lines[i] = "<br>"+line
    text = "".join(lines)
    return text


def predict(input, chatbot, history):
    max_length = 2048
    top_p = 0.7
    temperature = 0.1
    top_k = 3
    dboperate = db_operate(config_dict['db_path'])
    chatbot_prompt = """
你是一个文本转SQL的生成器，你的主要目标是尽可能的协助用户将输入的文本转换为正确的SQL语句。
上下文开始
生成的表名和表字段均来自以下表：
"""
    query_embedding = embedder.encode(input, convert_to_tensor=True) # 与6张表的表名和输入的问题进行相似度计算
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
    query = chatbot_prompt.replace("<user_input>", input)
    chatbot.append((parse_text(input), ""))
    # 流式输出
    # for response, history in model.stream_chat(tokenizer, query, history, max_length=max_length, top_p=top_p,
    #                                            temperature=temperature):
    #     chatbot[-1] = (parse_text(input), parse_text(response))
    response, history = model.chat(tokenizer, query, history=history, max_length=max_length, top_p=top_p,temperature=temperature)
    chatbot[-1] = (parse_text(input), parse_text(response))
    # chatbot[-1] = (chatbot[-1][0], chatbot[-1][1])
    # 获取结果中的SQL语句
    response = re.split("```|\n\n", response)
    for text in response:
        if "SELECT" in text:
            response = text
            break
    else:
        response = response[0]
    response = response.replace("\n", " ").replace("``", "").replace("`", "").strip()
    response = re.sub(' +',' ', response)
    # 查询结果
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
    return chatbot, history


def reset_user_input():
    return gr.update(value='')


def reset_state():
    return [], []

with gr.Blocks() as demo:
    gr.HTML("""<h1 align="center">🤖ChatSQL</h1>""")

    chatbot = gr.Chatbot()
    with gr.Row():
        with gr.Column(scale=4):
            with gr.Column(scale=12):
                user_input = gr.Textbox(show_label=False, placeholder="Input...", lines=10).style(
                    container=False)
            with gr.Column(min_width=32, scale=1):
                submitBtn = gr.Button("Submit", variant="primary")
        with gr.Column(scale=1):
            emptyBtn = gr.Button("Clear History")
            # max_length = gr.Slider(0, 4096, value=2048, step=1.0, label="Maximum length", interactive=True)
            # top_p = gr.Slider(0, 1, value=0.7, step=0.01, label="Top P", interactive=True)
            # temperature = gr.Slider(0, 1, value=0.95, step=0.01, label="Temperature", interactive=True)

    history = gr.State([])

    submitBtn.click(predict, [user_input, chatbot, history], [chatbot, history],
                    show_progress=True)
    submitBtn.click(reset_user_input, [], [user_input])

    emptyBtn.click(reset_state, outputs=[chatbot, history], show_progress=True)

demo.queue().launch(share=False, inbrowser=True)