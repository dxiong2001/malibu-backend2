from transformers import pipeline

#classifier = pipeline("summarization", model="t5-base")
summarizer = pipeline("summarization", model="t5-small", tokenizer="t5-small", framework="tf")

def abs_summarization(article_sections):
    summ_sections = []
    for text in article_sections:
        summ_sections.append(summarizer(text, max_length = 100, min_length = 10, do_sample=False)[0]['summary_text'])
    return summ_sections