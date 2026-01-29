import argparse
import pandas as pd
from nltk.metrics.agreement import AnnotationTask
from nltk.metrics.distance import interval_distance
from nltk.metrics.spearman import spearman_correlation

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
    for idx, row in table.iterrows():
        nltk_data.append((annotator_idx,idx,row["similarity"]))

print(nltk_data)
task = AnnotationTask(nltk_data, interval_distance)
print(f"Krippendorf alpha (squared distance) {task.alpha()}")

combined_table = annotator_tables[0]
for i in range(1, len(annotator_tables)):
    combined_table["similarity"] += annotator_tables[i]["similarity"]
combined_table["similarity"] /= len(annotator_tables)

if args.output != None:
    combined_table.to_csv(args.output)

if (args.computed != None) != (args.output_cmp != None):
    print("Either none or both --computed and --output_cmp need to be provided")
elif args.computed != None:
    collected = annotator_tables[0].drop(columns = ["similarity"])
    for annotator_idx, annotator in enumerate(annotator_tables):
        collected[f"human_{annotator_idx}"] = annotator["similarity"]
    collected["human_avg"] = combined_table["similarity"]

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

        old_fragment_1 = machine_scores["text_A"].copy()
        sort_condition = machine_scores["text_A"] < machine_scores["text_B"]
        machine_scores["text_A"] = machine_scores["text_A"].where(sort_condition, machine_scores["text_B"])
        machine_scores["text_B"] = machine_scores["text_B"].where(sort_condition, old_fragment_1)

        collected = collected.merge(pd.DataFrame({"fragment_text_1": machine_scores["text_A"],
                                                  "fragment_text_2": machine_scores["text_B"],
                                                  score_col: machine_scores[score_col]}), 
                                    on = ["fragment_text_1", "fragment_text_2"], how = "left")

    if args.amr_input:
        amr_data = pd.read_xml(args.amr_input)
        collected = collected.merge(pd.DataFrame({"fragment_text_1": amr_data["fragment_text"],
                                                  "amr_penman_1": amr_data["amr_penman"]}),
                                                  on = ["fragment_text_1"], how = "left")
        collected = collected.merge(pd.DataFrame({"fragment_text_2": amr_data["fragment_text"],
                                                  "amr_penman_2": amr_data["amr_penman"]}),
                                                  on = ["fragment_text_2"], how = "left")

    collected.to_excel(args.output_cmp)

#    spearman_list_human = []
#    spearman_list_machine = []
#    for idx, row in collected.iterrows():
#        spearman_list_human.append((idx, float(row["human_avg"])))
#        spearman_list_machine.append((idx, 5*float(row["machine_score"])))
#    
#    print(spearman_list_human)
#    print(spearman_list_machine)
#    print(f"Spearman correlation: {spearman_correlation(spearman_list_human, spearman_list_machine)}")
