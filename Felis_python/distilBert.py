import torch
import re

from ModelManager import distilbert_tokenizer, distilbert_model
from RuntimeSettings import load_runtime_settings

settings = load_runtime_settings()


tokenizer = distilbert_tokenizer
model = distilbert_model

# Return the indices of the N largest logits, ordered from largest to smallest
def indices_of_largest(logits):
    res = sorted(range(len(logits)), key=lambda sub: logits[sub])[-settings["N"]:][::-1]
    return res

# Find the best-scoring valid (start, end) index pair from the candidate start/end logits
def find_best_logit_pair(start_logits, best_start_indices, end_logits, best_end_indices, sequence_ids, offset_mapping):
    best_score = float("-inf")
    best_pair = (-1, -1)
    for start_idx in best_start_indices:
        for end_idx in best_end_indices:
            if sequence_ids[start_idx] != 1 or sequence_ids[end_idx] != 1 or end_idx < start_idx or end_idx - start_idx > settings["MAX_ANSWER_LENGTH"] or offset_mapping[start_idx][0] == offset_mapping[start_idx][1] or offset_mapping[end_idx][0] == offset_mapping[end_idx][1]:
                continue
            score = start_logits[start_idx] + end_logits[end_idx]

            if score > best_score:
                best_score = score
                best_pair = (start_idx, end_idx)
    return best_pair

#def expand_answer_to_30_words(inputs, start_idx,start_logits, end_idx,end_logits, sequence_ids, len_context):
#    answer_ids  = inputs["input_ids"][0][start_idx:end_idx + 1]
#    answer = tokenizer.decode(answer_ids, skip_special_tokens=True)
#    if(len(answer.split()) >=MAX_ANSWER_LENGTH):
#        return answer
#    mone = len(answer.split())
#    while mone+2 <= MAX_ANSWER_LENGTH and mone+2 <=len_context:
#        expanded = False
#        can_expand_left = (start_idx - 1 >= 0 and sequence_ids[start_idx - 1] == 1)
#        can_expand_right = (end_idx + 1 < len(sequence_ids) and sequence_ids[end_idx + 1] == 1)
#
#        if can_expand_left and can_expand_right:
#            if start_logits[start_idx - 1] >= end_logits[end_idx + 1]:
#                start_idx -= 1
#            else:
#                end_idx += 1
#            expanded = True
#
#        elif can_expand_left:
#            start_idx -= 1
#            expanded = True
#
#        elif can_expand_right:
#            end_idx += 1
#            expanded = True
#
#        if not expanded:
#            break
#        answer_ids  = inputs["input_ids"][0][start_idx:end_idx + 1]
#        answer = tokenizer.decode(answer_ids, skip_special_tokens=True)
#        mone = len(answer.split())
#    return answer



# Return the full sentence from the context that contains the given answer character span
def the_sentence_of_the_answer(start_char, end_char, context):
    sentences =  re.finditer(r'[^.!?]+[.!?]?', context)
    for sen in sentences:
        start_sen = sen.start()
        end_sen = sen.end()
        if start_char>start_sen and end_char<end_sen:
            return sen.group().strip()
    return context[start_char:end_char].strip()  
                
        
                
            




    




# Run the DistilBERT QA model on a context/question pair and return the sentence containing the best answer
def pipeline_DistilBert(context,question):
    inputs = tokenizer(question, context, return_tensors="pt" , return_offsets_mapping=True)
    offset_mapping = inputs.pop("offset_mapping")[0].tolist()
    with torch.no_grad():
        outputs = model(**inputs)

    start_logits = outputs["start_logits"][0].tolist()
    end_logits = outputs["end_logits"][0].tolist()

    top_start_indices = indices_of_largest(start_logits)
    top_end_indices = indices_of_largest(end_logits)
    sequence_ids = inputs.sequence_ids(0)
    start_idx, end_idx  = find_best_logit_pair(start_logits, top_start_indices, end_logits, top_end_indices,sequence_ids,offset_mapping)
    if start_idx == -1 or end_idx == -1:
        return ""
    start_char = offset_mapping[start_idx][0]
    end_char = offset_mapping[end_idx][1]
    if end_char <= start_char:
        return ""
    answer = the_sentence_of_the_answer(start_char, end_char,context)
    #answer = context[start_char:end_char].strip()
    return answer







#import SplitTextToParagraphs
#import FindSimilar
#import Bart
#
#context = """
#Photography
#Tips on how to take good photos.
#Explore your creative vision while improving your photography skills with helpful advice from photography professionals.
#Power up your photo skills.
#Get tips on equipment choice, exposure, shutter speed, light settings, and more from top photo pros. Discover composition techniques like the rule of thirds and find inspiration in different photography styles such as landscapes and portraiture. Plus, explore how to work with presets and gain helpful insight into cool ways to hone in on your own artistic vision.
#How to take better photos.
#Everyone has different ideas about what makes a great photo. Is the image meant to be beautiful? Is it meant to be thought-provoking? Is it meant to surprise or startle your viewer? Whatever the intent of your image, if it communicates your message or idea, it’s a good photo. But to convey ideas successfully, you need to master the technical side of photography. Understand how your camera works, how to compose a shot, and how to work with changing light. Follow these insights and tips from professionals to improve your photographic abilities.
#Understand the ins and outs of exposure.
#Every great photo starts with a good exposure. Learn how your shutter speed, aperture, and ISO settings relate to each other. For example, if you shoot in low light with a small aperture and a fast shutter speed, you’ll end up with an underexposed image. When you understand that relationship, you can use these tools to experiment and capture the exact image you want. Try longer shutter speeds to create motion blur. Or use wider apertures to get a shallow depth of field. When one setting changes, all the others must adjust to compensate for it. Remember, if your image is over- or underexposed, it will distract your viewer from the composition, color, or content of your photograph.
#Learn your equipment.
#“The more you know about a camera, the more you can take advantage of it, and you can change things on the fly,” explains photographer Jeff Carlson. If you take a picture of a sunset with a DSLR camera, you need to know how to quickly adjust your aperture and shutter speed to work with changing light. It’s important to get to know your camera so you don’t miss that perfect shot of the sun slanting through trees and clouds.
#“It’s not all about the equipment, it’s how you use it. Learn how to use what you have. Even if you just have an iPhone, you can still get creative with that,” says photography Sarah Marcella. Smartphone cameras and digital cameras of all kinds have come a long way, and with post-processing photo editing tools like Adobe {{lightroom}}, you can easily — and professionally — edit your photos anytime.
#Take lots of pictures.
#“My number one piece of advice is to practice. I learn something new every time I shoot. Every environment and every photoshoot is unique,” says photographer Jenn Byrne. Practice doesn’t just mean you go to a photo studio and take lots of photos. You also have to capture images in the moment and hone your artistic vision. Bring your camera with you when you’re out in the world and take photos of the things that interest you. Take close-up pictures of plants while on a walk, or take candid portraits of your family.
#“Shoot a lot of photos and recognize that you’re going to make a lot of really bad photos and that’s okay,” says Carlson. Every image you capture won’t be beautiful. Even professional photographers take bad photos. It’s through trial and error that you get better and find the style and approach that interests you. Try, fail, and try again. 
#Find the light that works for you.
#Good light is crucial for good photos. It can set the mood, create a successful exposure, and highlight what’s important in the composition. Experiment with both studio lighting and natural light to see which approach is right for your photos. With studio lighting, you have complete control of the color, brightness, and position of lights. It can take time to learn how to light scenes and people naturally with studio lights, but once you know how to set up key lights, you can get just the look you’re going for.
#Natural light can be a little easier to work with since it doesn’t require lots of extra equipment. But if you shoot outdoors with natural light, don’t take photos at noon when the sun is directly above. This can make your images flat and overly bright. Instead, shoot during the last hour before sunset and the first hour after sunrise, otherwise known as the golden hour. The light at these times is softer and easier to work with.
#Experiment with composition.
#Composition is how a photographer arranges elements inside the frame of an image. Following standard composition rules, like the rule of thirds, is a great way to experiment with where objects fall within the shot. Don’t snap a shot with your subject sitting in the middle of the image; instead, place your subject in the left or right third of an image and leave the other two thirds more open. Once you’ve mastered shooting with the rule of thirds in mind, experiment with shooting at different angles and from different perspectives. Try to balance your shot, fill the frame with your subject, or think about leading lines that draw the viewer’s eye across the image. An interesting composition can take a good photo and make it exceptional.
#Try different styles.
#Pursue and explore the realms of photography that interest you. “Think about which things you enjoyed shooting. Because that’s going to speak to your viewer. Just shoot whatever makes you happy,” says Carlson. When you’re passionate about the subject matter of your photos, that makes the image more interesting. If you like to hike, try your hand at landscape photography. Or connect with the people in your life and experiment with portraiture. Just follow your passions and explore the subjects that matter to you.
#Focus on your artistic vision.
#Composition is how a photographer arranges elements inside the frame of an image. Following standard composition rules, like the rule of thirds, is a great way to experiment with where objects fall within the shot. Don’t snap a shot with your subject sitting in the middle of the image; instead, place your subject in the left or right third of an image and leave the other two thirds more open. Once you’ve mastered shooting with the rule of thirds in mind, experiment with shooting at different angles and from different perspectives. Try to balance your shot, fill the frame with your subject, or think about leading lines that draw the viewer’s eye across the image. An interesting composition can take a good photo and make it exceptional.
#Experiment with presets.
#It’s almost impossible to snap the perfect photo in camera. That’s where editing software like Adobe {{lightroom}} comes in. “I have learned a lot from using presets and using them as a jumping off point,” says Byrne. Explore the standard presets available in {{lightroom}}, and then use them to create your own custom photo filters to get the exact look you want. The difference between a good photo and a great photo comes down to the details. And with the right tools on hand, you can edit those details to perfection.
#"""
#question = "want know take good pictures"
#sentences_context = SplitTextToParagraphs.split_titles_and_large_sections(context)
#
#short_sen = []
#for sen in sentences_context:
#    short_sen.append(pipeline_DistilBert(sen,question))
#t = FindSimilar.semantic_search_from_corpus(short_sen,question)
#print()
#print()
#print()
#print()
#print("---------------------------------------")
#text = []
#for hit in t:
#    idx = hit["corpus_id"]
#    score = hit["score"]
#    print(f"(Score: {score:.4f}) , short sentences: {short_sen[idx]}:::::::::::::\n ", sentences_context[idx]+"\n")
#    text.append(sentences_context[idx])
#print(text)
#
# 
#new_text = Bart.merging_paragraphs("\n".join(text))[0]['summary_text']
#print()
#print("new_text")
#print(new_text)




#context = r"""
#Extractive Question Answering is the task of extracting an answer from a text given a question. An example     of a
#question answering dataset is the SQuAD dataset, which is entirely based on that task. If you would like to fine-tune
#a model on a SQuAD task, you may leverage the examples/pytorch/question-answering/run_squad.py script.
#"""
#question="What is a good example of a question answering dataset?"
#
#print( pipeline_DistilBert(context, question))
#the_sentence_of_the_answer(context,question)



#from transformers import pipeline
#
## Replace this with your own checkpoint
#model_checkpoint = "huggingface-course/bert-finetuned-squad"
#question_answerer = pipeline("question-answering", model=model_checkpoint)
#
#context = """
#🤗 Transformers is backed by the three most popular deep learning libraries — Jax, PyTorch and TensorFlow — with a seamless integration
#between them. It's straightforward to train your models with one before loading them for inference with the other.
#"""
#question = "Which deep learning libraries back 🤗 Transformers?"
#question_answerer(question=question, context=context)