# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/02_app_gradio.ipynb.

# %% auto 0
__all__ = ['categories', 'k', 'min_words', 'max_words', 'ignore_text', 'ignore_common', 'learn', 'text', 'label', 'examples',
           'intf', 'predict']

# %% ../nbs/02_app_gradio.ipynb 4
import warnings
warnings.filterwarnings('ignore')
from fastai.text.all import *
from .data import *
import gradio as gr

# %% ../nbs/02_app_gradio.ipynb 6
categories = ('pseudoscience','science')
k = 30
min_words = 20
max_words = 450
ignore_text = ['the', 'of', 'to', 'and', 'a', 'in', 'it', 'that', 'for', 'on'] 
ignore_common = ignore_text
learn = load_learner('models/2022.12.01 Model v1 88pct', cpu=False)

def predict(url):
    page = get_page_all(url, k, max_words, ignore_text, ignore_common)
    length = len(page.cleaned_text)
    if  length < min_words:
        return "ERROR: Returned "+str(length)+" words"
    else:
        text = ' '.join(page.cleaned_text)
        with learn.no_bar(), learn.no_logging():
            pred,idx,probs = learn.predict(text)
        return dict(zip(categories, map(float,probs)))

# %% ../nbs/02_app_gradio.ipynb 8
text = gr.inputs.Textbox(1)
label = gr.outputs.Label()
examples = ['https://www.theskepticsguide.org/about','https://www.foxnews.com/opinion']

intf = gr.Interface(fn=predict, inputs=text, outputs=label, examples=examples)
