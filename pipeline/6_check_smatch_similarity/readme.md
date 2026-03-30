# AMR Similarity (Smatch) Computation

This script computes Smatch similarity between AMR graphs stored in an input XML or CSV file.

**Input format**

The input file must be produced at the previous step (see amr generation script). The file contains a column named: graph - AMR

**Usage**

Run the script from the command line:

```bash

python 6_check_smatch_similarity.py --input <AMR_graphs> --output <output_file>
```

**Output Examples**

<pair>
  <topic>TXL_airport_remain_operational_after_BER_opening</topic>
  <type>claim</type>
  <score>0.273</score>
  <file_A>micro_b044</file_A>
  <file_B>micro_k015</file_B>
  <text_A>As a central airport Berlin Tegel is particularly attractive for business travellers and should by all means remain operational.</text_A>
  <text_B>BER should be re-conceptualized from scratch,</text_B>
</pair>