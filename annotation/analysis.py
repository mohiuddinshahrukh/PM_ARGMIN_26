import argparse
import pandas as pd
from nltk.metrics.agreement import AnnotationTask
from nltk.metrics.distance import interval_distance, binary_distance
from nltk.metrics.spearman import spearman_correlation
from sklearn.metrics import f1_score, root_mean_squared_error
import pathlib
from random import random, seed
import matplotlib.pyplot as plt
from os import makedirs
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--input", required = True,
                    help = "Excel spreadsheet files with (partially) annotated data",
                    nargs = "+")
parser.add_argument("--output",
                    help = "Output averaged scores to given file")
parser.add_argument("--computed",
                    help = "CSV File with machine generated similarity pairs",
                    nargs = "+")
parser.add_argument("--output_cmp",
                    help = "Output combined scores for comparison to given file")
parser.add_argument("--amr_input",
                    help = "Pipeline stage 5 output")
args = parser.parse_args()

annotator_tables = list[pd.DataFrame]()
for file in args.input:
    annotator_tables.append(pd.read_excel(file, index_col = 0))

for table in annotator_tables:
    table.drop(table[table["similarity"] == "?"].index, inplace = True)

nltk_data = []
for annotator_idx, table in enumerate(annotator_tables):
    i = 0
    for idx, row in table.iterrows():
        nltk_data.append((annotator_idx,idx,(row["similarity"]-1)/4))
        i += 1

task = AnnotationTask(nltk_data, interval_distance)
print(f"Krippendorf alpha (squared distance) {task.alpha()}")

pearson_tables = {}
for annotator_idx, table in enumerate(annotator_tables):
    pearson_tables[f"annotator_{annotator_idx}"] = table["similarity"]

print(f"Pearson r {pd.DataFrame(pearson_tables).corr()}")

combined_table = annotator_tables[0]
for i in range(1, len(annotator_tables)):
    combined_table["similarity"] += annotator_tables[i]["similarity"]
combined_table["similarity"] /= len(annotator_tables)

if args.output != None:
    combined_table.to_csv(args.output)

def evaluate(df, score_col):
    test_fold_size = 4
    topics = list(set(collected["topic_id"]))
    num_folds = len(topics) // test_fold_size
    result_macro_f1 = 0
    result_f1 = [0, 0]
    for fold in range(num_folds):
        fold_offset = fold*test_fold_size
        train_topics = topics[:fold_offset] + topics[fold_offset+test_fold_size:]
        test_topics = topics[fold_offset:fold_offset+test_fold_size]

        train = df[df["topic_id"].map(lambda x: x in train_topics)]
        test = df[df["topic_id"].map(lambda x: x in test_topics)]

        best_macro_f1 = 0.0
        best_decision_boundary = None

        decision_boundary = 0.0
        decision_boundary_step = 0.05
        for i in range(int(1.0 / decision_boundary_step)):
            f1_scores = f1_score(train["human_avg_opitz"], (train[score_col] > decision_boundary).astype(int), average = None)
            macro_f1 = sum(f1_scores)/2
            if macro_f1 > best_macro_f1:
                best_macro_f1 = macro_f1
                best_decision_boundary = decision_boundary

            decision_boundary += decision_boundary_step

        #print(best_macro_f1)
        #print(f"Best decision boundary {best_decision_boundary}")
        f1_scores = f1_score(test["human_avg_opitz"], (test[score_col] > best_decision_boundary).astype(int), average = None)
        result_macro_f1 += sum(f1_scores) / 2
        result_f1[0] += f1_scores[0]
        result_f1[1] += f1_scores[1]

    print(score_col)
    print(f"Macro F1 {result_macro_f1/num_folds} {result_f1[0]/num_folds} {result_f1[1]/num_folds}")
    rms = root_mean_squared_error(df["human_avg"]-1, df[score_col]*4)
    print(f"RMS: {rms}")


if args.computed != None:
    collected = annotator_tables[0].drop(columns = ["similarity"])
    for annotator_idx, annotator in enumerate(annotator_tables):
        collected[f"human_{annotator_idx}"] = annotator["similarity"]
    collected["human_avg"] = combined_table["similarity"]

    def to_opitz_score(score: float) -> int:
        score -= 1
        score *= (2-1) / (5-1)
        return round(score)
    collected["human_avg_opitz"] = collected["human_avg"].map(to_opitz_score)

    seed(12345)
    collected["random"] = pd.Series(index = collected.index, data = [random() for i in range(len(collected))])

    collected["human_avg_norm"] = (collected["human_avg"] - 1) / 4
    score_cols = ["human_avg_norm"]

    evaluate(collected, "random")
    for computed_file in args.computed:
        machine_scores = pd.read_csv(computed_file)

        score_col = ""
        if "score" in machine_scores.columns:
            score_col = "smatch_score"
            machine_scores.rename(columns = {"score": "smatch_score"}, inplace = True)
        elif "s2_score" in machine_scores.columns:
            score_col = "s2_score"
        elif "sbert_score" in machine_scores.columns:
            score_col = "sbert_score"

        machine_scores.rename(columns = {"text_1": "text_A", "text_2": "text_B"}, inplace = True)

        old_fragment_1 = machine_scores["text_A"].copy()
        sort_condition = machine_scores["text_A"] < machine_scores["text_B"]
        machine_scores["text_A"] = machine_scores["text_A"].where(sort_condition, machine_scores["text_B"])
        machine_scores["text_B"] = machine_scores["text_B"].where(sort_condition, old_fragment_1)

        collected = collected.merge(pd.DataFrame({"fragment_text_1": machine_scores["text_A"],
                                                  "fragment_text_2": machine_scores["text_B"],
                                                  score_col: machine_scores[score_col]}), 
                                    on = ["fragment_text_1", "fragment_text_2"], how = "left")

        evaluate(collected, score_col)

        score_cols.append(score_col)

    if args.amr_input:
        amr_data = pd.read_xml(args.amr_input)
        collected = collected.merge(pd.DataFrame({"fragment_text_1": amr_data["fragment_text"],
                                                  "amr_penman_1": amr_data["amr_penman"]}),
                                                  on = ["fragment_text_1"], how = "left")
        collected = collected.merge(pd.DataFrame({"fragment_text_2": amr_data["fragment_text"],
                                                  "amr_penman_2": amr_data["amr_penman"]}),
                                                  on = ["fragment_text_2"], how = "left")

    if args.output_cmp != None:
        collected.to_excel(args.output_cmp)

    divisions = 3
    remaining = collected
    start = 0
    step = 1 / divisions
    for i in range(divisions):
        print(f"division {i}")
        within_range = remaining[remaining["human_avg_norm"] <= (start+step)]
        for col in score_cols:
            accuracy = np.count_nonzero(np.floor(within_range[col].where(within_range[col]!=1, 0.9) *3) == i) / len(within_range)
            print(f"{col} {accuracy}")

        remaining = remaining[remaining["human_avg_norm"] > (start+step)]
        start += step

    makedirs("plots", exist_ok = True)
    for col in score_cols:
        plt.cla()
        plt.clf()
        plt.xlabel({"human_avg_norm": "Human average", "s2_score": "S²MATCH", "sbert_score": "S-BERT", "smatch_score": "SMATCH"}[col])
        plt.hist(collected[col])
        plt.savefig(f"plots/{col}_dist.png")

#    spearman_list_human = []
#    spearman_list_machine = []
#    for idx, row in collected.iterrows():
#        spearman_list_human.append((idx, float(row["human_avg"])))
#        spearman_list_machine.append((idx, 5*float(row["machine_score"])))
#    
#    print(spearman_list_human)
#    print(spearman_list_machine)
#    print(f"Spearman correlation: {spearman_correlation(spearman_list_human, spearman_list_machine)}")
