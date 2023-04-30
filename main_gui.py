import os
import re
os.environ["CUDA_VISIBLE_DEVICES"] = "3"
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
from utils import obtain_sql, retrieval_related_table, execute_sql
from prompt import query_template, chatbot_prompt


tokenizer = AutoTokenizer.from_pretrained("./ChatGlm-6b", trust_remote_code=True)
model = AutoModel.from_pretrained("./ChatGlm-6b", trust_remote_code=True).half().cuda()
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
    temperature = 0.2
    dboperate = db_operate(config_dict['db_path'])
    input_prompt = chatbot_prompt
    input_prompt = retrieval_related_table(input_prompt, input, history, top_k=3)
    input_prompt += query_template
    query = input_prompt.replace("<user_input>", input)
    chatbot.append((parse_text(input), ""))
    # 流式输出
    # for response, history in model.stream_chat(tokenizer, query, history, max_length=max_length, top_p=top_p,
    #                                            temperature=temperature):
    #     chatbot[-1] = (parse_text(input), parse_text(response))
    response, history = model.chat(tokenizer, query, history=history, max_length=max_length, top_p=top_p,temperature=temperature)
    chatbot[-1] = (parse_text(input), parse_text(response))
    # chatbot[-1] = (chatbot[-1][0], chatbot[-1][1])
    # 获取结果中的SQL语句
    response = obtain_sql(response)
    chatbot = execute_sql(response, chatbot, dboperate)
    return chatbot, history


def reset_user_input():
    return gr.update(value='')


def reset_state():
    return [], []

with gr.Blocks() as demo:
    gr.HTML("""<h1 align="center">🤖ChatSQL-GLM</h1>""")

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