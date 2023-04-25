import gradio as gr

def my_function(x):
    return x**2, x**3

iface = gr.Interface(fn=my_function, 
                     inputs=gr.inputs.Number(), 
                     outputs=[gr.outputs.Textbox(), gr.outputs.Textbox()])

iface.launch()