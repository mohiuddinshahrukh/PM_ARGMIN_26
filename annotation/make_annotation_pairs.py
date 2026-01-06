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

os.makedirs(args.output, exist_ok = True)

# shuffle through
corpus = corpus.sample(frac = 1, random_state = 1)

DIVISON = 200

i = 0
while i < len(corpus):
    corpus[i:i+DIVISON].to_excel(os.path.join(args.output, f"{i}-{min(i+DIVISON,len(corpus))-1}.xlsx"))
    i += DIVISON
