from asyncore import file_wrapper
import pandas as pd 
import pathlib
import re
import deepl
import os
import spacy

VERB_ABBREVS = ["VB", "VBD", "VBG", "VBN", "VBP", "VBZ"]

def convert_conll_to_dicts(test_dir) :
    dir = pathlib.Path(test_dir).rglob("*conll")


    dir_sents = []
    for file in dir : #each file is a sentence, as of 4/20/22

        with open(file) as reader :
            lines = reader.readlines()
            file_sents = [] #final array of all sentences in this file (TEXT ONLY)
            file_token_dicts = []

            # Structure of file_token_dicts: 
            # 
            # link each compiled sentence with list of all PropBank senses and their corresponding tokens.
            # Each entry of file_sents is a dictionary: 
            # {"sent": sent, 
            # "tokens": [token1, token2],
            # "lemmas": [lemma1, lemma2],
            # "parse": [parse1, parse2] 
            # "propbank": [PB.01, PB.02]

            current_sent = "" #DeepL automatically fills in the punctuation gaps!
            sent_tokens = []; sent_lemmas = []; sent_parses = []; sent_pbs = []
            
            for i, line in enumerate(lines) :
                if line == '\n' : #marks the end of the current vertical spans of sentences
                    s = re.sub(" / ", "", current_sent) #Use regex to remove the trailing "/ character
                    #print(f"i: {i}, s: {s}") #Verify the new sentence preserves all punctuation 
                    #sans the trailing "/"
                    
                    token_dict = {"sent":s, "tokens":sent_tokens, "lemmas":sent_lemmas, 
                                  "parses":sent_parses, "propbanks":sent_pbs}
                    file_token_dicts.append(token_dict)

                    # Reset sentence containers
                    current_sent = "" 
                    sent_tokens = []; sent_lemmas = []; sent_parses = []; sent_pbs = []
                else :
                    conll_items = line.split('\t')
                    '''
                                LEGEND:

                                0 = token number
                                1 = original token
                                2 = lowercased
                                3 = parse tag 1
                                4 = ?
                                5 = token
                                6 = lemma
                                7 = parse tag 2
                                8 = is a token of item ____
                                9 = dependency relation label
                                10 = English PropBank sense
                                11 = ARG role
                                12 = ARG role
                    ''' 
                    #Extract relevant data from array of CONLL data for this token
                    orig_token = conll_items[1]
                    lemma = conll_items[6]
                    parse = conll_items[3]
                    propbank = conll_items[10]

                    if propbank != "_" and propbank != "" and propbank != "_" :
                        sent_tokens.append(orig_token)
                        sent_lemmas.append(lemma)
                        sent_parses.append(parse)
                        sent_pbs.append(propbank)
                    
                    current_sent += orig_token + " "
        dir_sents.append(file_token_dicts)
    return dir_sents

def get_pl_parses(pl_sents_master) :
    nlp = spacy.load('pl_core_news_lg')
   

    '''
    pl_tags = ["ADJ", "ADJA", "ADJC", "ADJP", "ADV", "AGLT", "BEDZIE", "BREV", "BURK", "COMP", "CONJ",
         "DEPR", "FIN", "GER", "IMPS", "IMPT", "INF", "INTERJ", "INTERP", "NUM", "NUMCOL", "PACT", "PANT", 
         "PCON", "PPAS", "PPRON12", "PPRON3", "PRAET," "PRED", "PREP", "QUB", "SIEBIE", "SUBST", 
         "WINIEN", "XXX", "_SP"]
    for tag in pl_tags :
        spacy.explain(tag)
    exit()
    '''
            


    pl_parses = [] #list of dictionaries, each dictionary contains parse information about 1 sentence
    for sent in pl_sents_master :
        pl_verbs = []; pl_lemmas = []; pl_pos = []

        #print(sent)
        doc = nlp(sent)

   
        for token in doc :
            if token.pos_ == "VERB" : #VERB TOKEN
                pl_verbs.append(token.text) #original token
                pl_lemmas.append(token.lemma_) #lemmatized verb
                pl_pos.append(token.pos_) #Penn TreeBank


        pl_parses.append({"pl_verbs":pl_verbs, "pl_lemmas":pl_lemmas, "pl_pos":pl_pos})

    return pl_parses

if __name__ == "__main__" :
    spoken_dir = "masc-conll/data/spoken/"
    written_dir = "masc-conll/data/written/"

    num_characters = 0
    i = 0

    en_sents_only = [] #FEED THIS INTO DEEPL
    nones = 0
    sent_dicts = convert_conll_to_dicts(spoken_dir) + convert_conll_to_dicts(written_dir)

    # Removes blank text rows from sent_dicts
    # Creates the array of English sentences to be passed into DeepL Translator
    
    sd_length = 0
    new_sent_dicts = []
    for file in sent_dicts :  #file is a list of sentDict objects (list of dictionaries)
        #print("length of original file", len(file))
        #new_file = [d for d in file if d['sent'] != ''] #Removes all empty dictionaries
        #print("length of new file", len(new_file))
        new_file = []
        for i, sentDict in enumerate(file) : #All sentences in 1 file
            s = sentDict["sent"]
            if s == "" :
                del file[i] #Removes dictionaries that have no text from the list "files"
            else :
                sd_length += 1 
                new_file.append(sentDict)
            #num_characters += len(s)
            #en_sents_only.append(s) #list of text-only
        new_sent_dicts.append(new_file)
    
    print("sd length", sd_length)
    '''
    DeepL Translator

    #define AUTH_KEY here
    AUTH_KEY = None
    translator = deepl.Translator(AUTH_KEY)

    if os.path.exists("polish_sents.txt") :
        os.remove("polish_sents.txt")

    pl_sents = []

    results = translator.translate_text(
        en_sents_only, 
        source_lang = 'en',
        target_lang = 'pl',
        formality = 'more'
    )
    for result in results :
        pl_sents.append(result.text)
    
    '''

    ''' 
    12/3/22 Load in Polish sentences from a file
    '''
    reader = open("polish_sents.txt")
    pl_sents_master = reader.readlines()
    reader.close()

    #Get Polish parses
    pl_parses_master = get_pl_parses(pl_sents_master)

    #Column names / containers
    en_sents = []; pl_sents = [] 
    en_verbs = []; en_lemmas = []; en_pos = []
    pl_verbs = []; pl_lemmas = []; pl_pos = []
    en_pb = []

    i = 0
    for file in new_sent_dicts : #file is the list of sentDicts (corresponds to 1 sentence) in 1 file
        for sentDict in file :
            print("i: ", i)

            en_sent = sentDict["sent"]
            if en_sent == "" :
                continue

            #Unpack data for 1 sentence
            tokens = sentDict["tokens"]
            lemmas = sentDict["lemmas"]
            parses = sentDict["parses"]
            propbanks = sentDict["propbanks"]

            #Extract verbal tokens only
            new_tokens = []; new_lemmas = []; new_parses = []; new_propbanks = []
            for k, parse in enumerate(parses) :
                if parse in VERB_ABBREVS :
                    new_tokens.append(tokens[k])
                    new_lemmas.append(lemmas[k])
                    new_parses.append(parse)
                    new_propbanks.append(propbanks[k])
                    

            en_verb_string = ",".join(new_tokens)
            en_lemma_string = ",".join(new_lemmas)
            en_pos_string = ",".join(new_parses)
            en_pb_string = ",".join(new_propbanks)

            print(en_sent)
            pl_sent = pl_sents_master[i]
            pl_parse = pl_parses_master[i]
            print(pl_sent)
            print(pl_parse)
            #Unpack pl_parse into verbs, lemmas, pos arrays
            pl_verbs_arr = pl_parse["pl_verbs"] #array
            pl_lemmas_arr = pl_parse["pl_lemmas"]
            pl_pos_arr = pl_parse["pl_pos"]

            #Unpack each array into comma-separated string
            pl_verb_string = ",".join(pl_verbs_arr)
            pl_lemma_string = ",".join(pl_lemmas_arr)
            pl_pos_string = ",".join(pl_pos_arr)

            #Append
            en_sents.append(en_sent); pl_sents.append(pl_sent)
            en_verbs.append(en_verb_string); en_lemmas.append(en_lemma_string); en_pos.append(en_pos_string)
            pl_verbs.append(pl_verb_string); pl_lemmas.append(pl_lemma_string); pl_pos.append(pl_pos_string)
            en_pb.append(en_pb_string)

            i += 1 #Increment i so it retains value as you process each file

    print("new sentDicts length (supposedly post-removal of empty rows): ", i)
     #to be turned into a DataFrame
    master_data = {"English Text (MASC-CONLL)" : en_sents, "Polish text (DeepL)" : pl_sents,
                    "English Verbs":en_verbs, "English Lemmas":en_lemmas, "English POS":en_pos,
                    "Polish Verbs":pl_verbs, "Polish Lemmas":pl_lemmas, "Polish POS":pl_pos,
                    "English PropBank (Gold)":en_pb
                    }
    df = pd.DataFrame(data = master_data)
    df.to_excel("polish_train.xlsx")