from transformers import pipeline

#classifier = pipeline("summarization", model="t5-base")
classifier = pipeline("summarization")

def abs_summarization(article_sections):
    summ_sections = []
    #for text in article_sections:
        #summ_sections.append(classifier(text, max_length = 100, min_length = 10, do_sample=False)[0]['summary_text'])
    return summ_sections