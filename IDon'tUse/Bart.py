from transformers import pipeline , BartForConditionalGeneration

summarizer = pipeline("summarization", model= "./models/bart-large-cnn")

def summarize_text(text):
    new_text = summarizer(text, max_length=20, min_length=10, do_sample=False)
    return new_text

#איחוד פסקאות לפסקה מנוסחת אחת
def merging_paragraphs(text):
    new_text = summarizer(text, max_length=400, min_length=250, do_sample=True)
    return new_text


#text_question = "want know take good pictures"
#short_texts = ['Experiment with presets. It’s almost impossible to snap the perfect photo in camera. That’s where editing software like Adobe {{lightroom}} comes in. “I have learned a lot from using presets and using them as a jumping off point,” says Byrne Explore the standard presets available in {{lightroom}}, and then use them to create your own custom photo filters to get the exact look you want The difference between a good photo and a great photo comes down to the details And with the right tools on hand, you can edit those details to perfection', 'Photography\nTips on how to take good photos. Explore your creative vision while improving your photography skills with helpful advice from photography professionals', 'up key lights, you can get just the look you’re going for Natural light can be a little easier to work with since it doesn’t require lots of extra equipment But if you shoot outdoors with natural light, don’t take photos at noon when the sun is directly above', 'Every image you capture won’t be beautiful. Even professional photographers take bad photos. It’s through trial and error that you get better and find the style and approach that interests you', 'Try different styles. Pursue and explore the realms of photography that interest you. “Think about which things you enjoyed shooting. Because that’s going to speak to your viewer. Just shoot whatever makes you happy,” says Carlson. When you’re passionate about the subject matter of your photos, that makes the image more interesting If you like to hike, try your hand at landscape photography Or connect with the people in your life and experiment with portraiture Just follow your passions and explore the subjects that matter to you']
#
#new_texts = []
#
#for text in short_texts:
#    new_texts.append(summarize_text(text)[0]['summary_text'])
#print(new_texts)

#one_text = merging_paragraphs(" ".join(new_texts))[0]['summary_text']
#print()
#print()
#print()
#print()
#print()
#print()
#print()
#print()
#print("--------------------------finish answer 1-----------------")
#print(one_text)
#
#one_text = merging_paragraphs("\n".join(short_texts))[0]['summary_text']
#print()
#print()
#print()
#print()
#print()
#print()
#print()
#print()
#print("--------------------------finish answer 2-----------------")
#print(one_text)



#לא צריך
#
#hits = FindSimilar.semantic_search_from_corpus(new_texts ,text_question)
#print()
#print("--------------------------")
#for hit in hits:
#    idx = hit["corpus_id"]
#    score = hit["score"]
#    print(f"(Score: {score:.4f})", new_texts[idx]+"\n")

