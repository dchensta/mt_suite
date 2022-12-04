import re
import pandas as pd

d = {"English (MASC-CONLL)" : [], "Polish (DeepL)" : []}
with open("sents_only.txt") as reader :
    lines = reader.readlines()
    d["English (MASC-CONLL)"] = lines

with open("polish_sents.txt") as reader :
    lines = reader.readlines()
    d["Polish (DeepL)"] = lines
    
df = pd.DataFrame(data = d)
df.to_excel("train.xlsx")