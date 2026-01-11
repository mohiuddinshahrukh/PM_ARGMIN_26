import argparse
import pandas as pd
from nltk.metrics.agreement import AnnotationTask
from nltk.metrics.distance import interval_distance

parser = argparse.ArgumentParser()
parser.add_argument("--input", required = True,
                    help = "Excel spreadsheet files with (partially) annotated data",
                    nargs = "+")
parser.add_argument("--output",
                    help = "Output averaged scroes")
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

if args.output != None:
    combined_table = annotator_tables[0]
    for i in range(1, len(annotator_tables)):
        combined_table["similarity"] += annotator_tables[i]["similarity"]
    combined_table["similarity"] /= len(annotator_tables)

    combined_table.to_csv(args.output)
