from transformers import pipeline


mood_classifier = pipeline('sentiment-analysis')
m = mood_classifier('I am deeply upset by how large these pre-trained models are.')
print(m)
