# AMR Similarity (S2match) Computation

This script computes S2match similarity between AMR graphs stored in an input XML or CSV file.

**Input format**

The input file must be produced at the previous step (see amr generation script). The file contains a column named: graph - AMR

**Usage**

Run the script from the command line:

```bash

python 7_s2match.py --input <AMR_graphs> --output <output_file>
```

**Output Examples**

<item>
<topic>allow_shops_to_open_on_holidays_and_sundays</topic>
<arg_A>a3</arg_A>
<arg_B>a5</arg_B>
<text_A>Hence it is good when shops are not open on Sundays and public holidays.</text_A>
<text_B>Opening on Sundays and holidays would therefore help both customers and shops.</text_B>
<type_A>claim</type_A>
<type_B>claim</type_B>
<s2_score>0.5204</s2_score>
</item>