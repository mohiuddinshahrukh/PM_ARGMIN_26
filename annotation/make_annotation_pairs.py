import argparse
import pandas as pd
import os

parser = argparse.ArgumentParser()
parser.add_argument("--input", required = True,
                    help = "Table of arguments, can be generated with 5_microtext_claims_extraction.py --format csv --types claim premise objection")
parser.add_argument("--main_claim", action = "store_true",
                    help = "If given takes main claims otherwise takes non main claim arguments")
parser.add_argument("--output", required = True,
                    help = "Directory into which Excel files for annotation will be put")
args = parser.parse_args()

corpus = pd.read_csv(args.input)

corpus.drop(corpus[(corpus.type == "claim") != args.main_claim].index, inplace=True)
corpus.drop(corpus[corpus.topic_id == "MISSING_TOPIC"].index, inplace=True)

print(f"Arguments total with topic {len(corpus)}")
# effectively cartesian product of all arguments of the same topic
corpus = corpus.merge(corpus, on = "topic_id", suffixes = ("_1", "_2"))
print(f"After making pairs {len(corpus)}")

# it's more convenient to have them next to each other
corpus = corpus.reindex(columns = ["file_id_1", "topic_id", "adu_id_1", "type_1", "is_major_claim_1",
       "stance_1", "file_id_2",
       "adu_id_2", "type_2", "is_major_claim_2", "stance_2",
       "full_sentence_1", "full_sentence_2",
       "fragment_text_1", "fragment_text_2"])

corpus["similarity"] = "?"

# hack
#rodion_results = pd.read_excel("annotation/annotated/0-199_Zorin.xlsx", index_col = 0)
#rodion_results.drop("Unnamed: 17", axis = 1, inplace = True)
#corpus = corpus.merge(rodion_results, how = "left")
#corpus["similarity"] = corpus["similarity"].fillna("?")
#print(corpus.head())

## shuffle through
corpus = corpus.sample(frac = 1, random_state = 1)

# sort fragment text lexicographically so that two rows with the same
# content but swapped end up the same and can be removed as duplicates
old_fragment_1 = corpus["fragment_text_1"].copy()
sort_condition = corpus["fragment_text_1"] < corpus["fragment_text_2"]
corpus["fragment_text_1"] = corpus["fragment_text_1"].where(sort_condition, corpus["fragment_text_2"])
corpus["fragment_text_2"] = corpus["fragment_text_2"].where(sort_condition, old_fragment_1)
corpus.drop_duplicates(subset = ["fragment_text_1", "fragment_text_2"], inplace = True)
corpus.drop(corpus[corpus["fragment_text_1"] == corpus["fragment_text_2"]].index, inplace = True)
print(f"After removing symmetry {len(corpus)}")

DIVISON = 200

os.makedirs(args.output, exist_ok = True)
i = 0
while i < len(corpus):
    corpus[i:i+DIVISON].to_excel(os.path.join(args.output, f"{i}-{min(i+DIVISON,len(corpus))-1}.xlsx"))
    i += DIVISON
