import pandas as pd 
import pathlib
import re
import deepl
import os

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

                    if len(propbank) > 0 :
                        sent_tokens.append(orig_token)
                        sent_lemmas.append(lemma)
                        sent_parses.append(parse)
                        sent_pbs.append(propbank)
                    
                    current_sent += orig_token + " "
        dir_sents.append(file_token_dicts)
    return dir_sents


if __name__ == "__main__" :
    spoken_dir = "masc-conll/data/spoken/"
    written_dir = "masc-conll/data/written/"

    num_characters = 0
    i = 0

    sents_only = [] #FEED THIS INTO DEEPL
    nones = 0
    sent_dicts = convert_conll_to_dicts(spoken_dir) + convert_conll_to_dicts(written_dir)
    for file in sent_dicts :
        for sentDict in file :
            s = sentDict["sent"]
            if s == "" :
                nones += 1
                file.remove(sentDict)
                continue
            else :
                num_characters += len(s)
                sents_only.append(s)
            
    #print("nones: ", nones)
    #print(f"{num_characters} characters in spoken and written folders")

    #print(f"{len(sents_only)} sentences")
    '''
    with open("sents_only.txt", "w") as output :
        for sent in sents_only :
            output.write(sent + "\n")
    '''

    AUTH_KEY = "c1e94bb2-7723-02cd-f03c-49699cdebfe2:fx"
    translator = deepl.Translator(AUTH_KEY)

    if os.path.exists("polish_sents.txt") :
        os.remove("polish_sents.txt")

    with open("polish_sents.txt", "w") as deepl_output:
        for sent in sents_only :    
            result = translator.translate_text(
                sent,
                source_lang = 'en',
                target_lang = 'pl',
                formality = 'more'
            )
            print(result.text)
            deepl_output.write(result.text + "\n")
            
    #print("\nMASC-CONLL PropBank data successfully extracted.")