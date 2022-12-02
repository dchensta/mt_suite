import pandas as pd 
import pathlib

def convert_conll_to_dicts(test_dir) :
    dir = pathlib.Path(test_dir).rglob("*conll")

    #i = 0
    dir_sents = []
    for file in dir : #each file is a sentence, as of 4/20/22
        '''
        i += 1
        if i > 1 :
            break
        '''

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
            
            for line in lines :
                if line == '\n' : #marks the end of the current vertical spans of sentences
                    file_sents.append(current_sent)

                    token_dict = {"sent":current_sent, "tokens":sent_tokens, "lemmas":sent_lemmas, 
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
    dir_sents = convert_conll_to_dicts(spoken_dir) + convert_conll_to_dicts(written_dir)
    for file in dir_sents :
        for sentDict in file :
            num_characters += len(sentDict["sent"])
    
    print(f"{num_characters} characters in spoken and written folders")
    print("Program completed")