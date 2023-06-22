# Natural Language Processing (NLP) Models for use in a pygame-based videogame
# Author: Christina Kampel

# Pygame-based video game using these models: 

# See the companion article "Pygame with AI": https://de-fellows.github.io/RexCoding/python/pygame/huggingface/transformers/pipelines/natural%20language%20processing/nlp/machine%20learning/ml/artificial%20intelligence/ai/conversational%20models/question-answering%20models/fill-mask/text-generation/2023/06/21/Pygame-with-AI.html


from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM, AutoModelForQuestionAnswering, AutoModelForMaskedLM, AutoModelForCausalLM


# ------------------------ CONVERSATIONAL MODEL --------------------------------------- #
# Model: facebook/blenderbot-400M-distill (https://huggingface.co/facebook/blenderbot-400M-distill?text=Hey+my+name+is+Julien%21+How+are+you%3F)

# set up the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained("facebook/blenderbot-400M-distill")
model = AutoModelForSeq2SeqLM.from_pretrained("facebook/blenderbot-400M-distill")

# set the tokenizer to left padding
tokenizer.padding_side = 'left'

# pad using the eos token
tokenizer.pad_token = tokenizer.eos_token

# create chatbot
blenderbot = pipeline(task="conversational", model=model, tokenizer=tokenizer)

# -------------------------- QUESTION-ANSWERING MODEL ------------------------------------------------ #
# Model: distilbert-base-cased-distilled-squad (https://huggingface.co/distilbert-base-cased-distilled-squad)

# set up model and tokenizer
qa_tokenizer = AutoTokenizer.from_pretrained("distilbert-base-cased-distilled-squad")
qa_model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-cased-distilled-squad")

# create chatbot
qa_chatbot = pipeline(task="question-answering", model=qa_model, tokenizer=qa_tokenizer)

# create context - the information containing the answers
context = """This video game has the following objects in it: Player Bear, Wall, Tree, Key, Lock Polar Bear, and Robot.
             The Player Bear is a character controlled by you, the user. You can use the arrow keys to make the Player Bear move around,
             and the RETURN or ENTER keys to talk with other chatbots.
             The wall is an impassible obstacle. You cannot go over it. You must go around it.
             The tree and the lock are interactive objects. The key is located at the top of the tree. You can climb the tree to get the key.
             The key appears in your inventory. Once you have the key, you can use it to open or unlock the lock.
             
             This game contains two NPCs: the Polar Bear and the Robot.
             Each NPC is a chatbot that uses a different NLP model to perform a language task.
             The Polar Bear is an NPC that uses the facebook/blenderbot-400M-distill model to perform the task of conversational response modelling.
             The Robot is an NPC that uses the distilbert-base-cased-distilled-squad model to perform the task of question-answering.
                     
             Definitions: "NPC" stands for "non-player character". "NLP" stands for "natural language processing".
             """

# -------------------------- FILL-MASK MODEL ------------------------------------------------ #
# Model: distilroberta-base (https://huggingface.co/distilroberta-base)

# set up model and tokenizer
fm_tokenizer = AutoTokenizer.from_pretrained("distilroberta-base")
fm_model = AutoModelForMaskedLM.from_pretrained("distilroberta-base")

# create chatbot
fm_chatbot = pipeline(task="fill-mask", model=fm_model, tokenizer=fm_tokenizer)

# -------------------------- TEXT-GENERATION MODEL ------------------------------------------------ #
# Model: gpt2 (https://huggingface.co/gpt2?text=Once+upon+a+time%2C)

# set up model and tokenizer
tg_tokenizer = AutoTokenizer.from_pretrained("gpt2")
tg_model = AutoModelForCausalLM.from_pretrained("gpt2")

# create chatbot
tg_chatbot = pipeline(task="text-generation", model=tg_model, tokenizer=tg_tokenizer, do_sample=True)

# -------------------------- FUNCTIONS ------------------------------------------------ #

# conversation-trimming function
def trim_convo(conversation):
    """Trim the earliest user and bot lines from a Conversation.

    Parameters:
    - conversation (transformers.pipelines.conversational.Conversation object): conversation to trim

    Returns:
    - Trimmed conversation (transformers.pipelines.conversational.Conversation object)
    """
    try:
        conversation.past_user_inputs.pop(0)
        conversation.generated_responses.pop(0)
        return conversation
    except:
        warning = f"Conversation is too short to be trimmed."
        print(warning)