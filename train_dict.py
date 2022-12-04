import pandas as pd

def train_dict(path) :
    df = pd.read_excel(path) #dataframe
    i = 0
    for row in df.iterrows() :
        if i > 5 :
            break
        i += 1

        en = row["English (MASC-CONLL)"]
        pl = row["Polish DeepL"]

        print(en)
        print(pl)

if __name__ == "__main__" :
    path = 'polish_train.xlsx'
    train_dict(path)