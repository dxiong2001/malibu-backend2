import json
import requests
import urllib
import urllib.parse
from decouple import config
import time

# from transformers import pipeline

# #classifier = pipeline("summarization", model="t5-base")


# def abs_summarization(article_sections):
#     summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small", framework="tf")
#     summ_sections = []
#     for text in article_sections:
#         summ_sections.append(summarizer(text, max_length = 100, min_length = 10, do_sample=False)[0]['summary_text'])
#     return summ_sections



def abs_summarization(article_sections):
    start_time = time.time()
    summ_sections = []
    for text in article_sections:
        
    
        headers = {
        "Authorization": f"Bearer {config('HUGGING_FACE')}",
        }
        
        data = json.dumps(text)
        API_URL = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"
        response = requests.request("POST", API_URL, headers=headers, data=data)
        print(json.loads(response.content.decode("utf-8")))
        abs_summ = json.loads(response.content.decode("utf-8"))[0]['summary_text']
        
        print(abs_summ)
        summ_sections.append(abs_summ)
    print("--- %s seconds ---" % (time.time() - start_time))
    return summ_sections
    