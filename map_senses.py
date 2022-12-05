import pandas as pd

def map_senses(train_path) :
    '''
    {xlsx} datapath = path to Excel file containing MT data
    '''
    df = pd.read_excel(train_path)

    '''Keys and Values of df

    English Text (MASC-CONLL)               Welcome back to our show !
    Polish text (DeepL)          Witamy ponownie w naszym programie!\n
    English Verbs                                              Welcome
    English Lemmas                                             welcome
    English POS                                                    VBP
    Polish Verbs                                                Witamy
    Polish Lemmas                                                witać
    Polish POS                                                    VERB
    English PropBank (Gold)                                 welcome.01
    
    '''

    pl_lexicon = {}
    unequal_lengths = []
    for index, row in df.iterrows() :
        #Skip empty rows (no Polish lemma or English PropBank)
        if type(row["Polish Lemmas"]) != str or type(row["English PropBank (Gold)"]) != str:
            continue

        #Transform comma-separated strings into arrays
        pl_lemmas = row["Polish Lemmas"].split(",") 
        en_propbanks = row["English PropBank (Gold)"].split(",")

        if len(pl_lemmas) != 1 or len(en_propbanks) != 1 :
            unequal_lengths.append(index) # index = row number in DataFrame
            continue

        #1 to 1 scenario
        pl_lemma = row["Polish Lemmas"]
        en_propbank = row["English PropBank (Gold)"]
        #New Entry
        if pl_lexicon.get(pl_lemma) == None : 
            pl_lexicon[pl_lemma] = {en_propbank : 1}
        else : #Pre-existing Entry
            #Check if en_propbank entry is new or not
            if pl_lexicon[pl_lemma].get(en_propbank) == None :
                pl_lexicon[pl_lemma][en_propbank] = 1
            else :
                pl_lexicon[pl_lemma][en_propbank] += 1

        '''
        #for i, pl_lemma in enumerate(pl_lemmas) :
            #Alignment of Polish verb lemma with English PropBank
            #en_propbank = en_propbanks[i]

            #New Entry
            if pl_lexicon.get(pl_lemma) == None : 
                pl_lexicon[pl_lemma] = {en_propbank : 1}
            else : #Pre-existing Entry
                #Check if en_propbank entry is new or not
                if pl_lexicon[pl_lemma].get(en_propbank) == None :
                    pl_lexicon[pl_lemma][en_propbank] = 1
                else :
                    pl_lexicon[pl_lemma][en_propbank] += 1
        '''
                
    #print(pl_lexicon.items())
    #print("Row #'s with unequal lengths: ", unequal_lengths)
    print("Number of rows with unequal lengths: ", len(unequal_lengths))
    print("Proportion of rows in DataFrame that have unequal lengths: ", len(unequal_lengths) / len(df))

    return pl_lexicon

def convert_conllup_to_test_set(gold_path) :
    '''
    Indices of global.columns:
    0 = STANZA:ID   1 = STANZA:FORM     2 = STANZA:LEMMA 
    3 = STANZA:UPOS 4 = STANZA:XPOS     5 = STANZA:FEATS 
    6 = STANZA:HEAD 7 = STANZA:DEPREL   8 = GOLD:PRED 
    9 = GOLD:ARGHEADS               (10 total)
    '''

    test_X = []; test_y = []
    with open(gold_path) as reader :
        lines = reader.readlines()
        for line in lines :
            if line[0] == "#" or line[0] == "\n":
                continue

            conll_items = line.split('\t')

            gold_en_propbank = conll_items[8]
            if gold_en_propbank != "_" :
                pl_lemma = conll_items[2]
                test_X.append(pl_lemma)
                test_y.append(gold_en_propbank)

    return test_X, test_y

def evaluate_on_gold(pl_lexicon, test_X, test_y) :
    score = 0

    not_in_lexicon = {}
    in_lexicon = {}
    for x, y in zip(test_X, test_y) :
        options = pl_lexicon.get(x)
        if options == None :
            not_in_lexicon[x] = not_in_lexicon.get(x, 0) + 1
        else :
            in_lexicon[x] = in_lexicon.get(x, 0) + 1
            for pb_sense in options.keys() :
                if pb_sense == y :
                    score += 1
    
    accuracy = round(score*100 / len(test_X), 3)
    print(f"Accuracy of learned Polish:English PB mappings on Polish test set: {accuracy}%")
    print(f" = {score} / {len(test_X)} lemmas receive the correct English PropBank label, based on human annotation of those Polish lemmas")
    print(f"{len(not_in_lexicon)} Polish lemmas not learned in training, but present in test set")
    print(f"versus {len(in_lexicon)} Polish lemmas that were learned in training and can thus be looked up for the test set")
if __name__ == "__main__" :
    #Use training set to create mappings between Polish lemmas and English PropBank
    train_path = "polish_train.xlsx"
    pl_lexicon = map_senses(train_path)

    #Prepare test set (Polish OntoNotes Gold from Universal PropBank 2.0)
    gold_path = "pl_trontonotes-gold.conllup"
    test_X, test_y = convert_conllup_to_test_set(gold_path)
    evaluate_on_gold(pl_lexicon, test_X, test_y)
    