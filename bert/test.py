from transformers import pipeline


mood_classifier = pipeline('sentiment-analysis')



m = mood_classifier('I am deeply upset by how large these pre-trained models are.')
print(m)
from news_scraping_lib import fetch_all_campus


sentences = fetch_all_campus()
for i in sentences:
    print()
    print(mood_classifier(i[0]))
