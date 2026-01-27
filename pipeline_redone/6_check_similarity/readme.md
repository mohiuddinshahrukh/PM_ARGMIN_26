# AMR Similarity (Smatch) Computation

This script computes Smatch similarity between AMR graphs stored in an input XML or CSV file. It supports two workflows:
- Microtext / ADU mode: compute similarities per ADU pair (claim, premise, etc.)
- Minimal-pair mode: compute one similarity score per sentence pair (minimal pair) grouped by id_pair.

**Minimal pair example**:
Tuition fees should not be **charged** in Germany.
Tuition fees should not be **introduced** in Germany.

Note: The minimal-pair mode is useful when testing a specific hypothesis (for example, that the use of synonyms should have only a minimal influence on the Smatch score). Such hypotheses can be evaluated by constructing a minimal pair and assessing it using Smatch.

The output is a CSV (default) or XML file containing only matches above a small threshold.

**Input format**

The input file must be produced at the previous step (see amr generation script). The file contains a column named: graph - AMR in PENMAN notation (comments like # ::snt ... are allowed)

Depending on the mode, additional columns are expected:

**Usage Examples**

Microtext / ADU mode:
python ./6_check_similarity.py --input pipeline_redone/5_amr_graph_construction/results/test.xml --topic school_uniforms --type claim --output test_smatch.xml

Minimal-pair mode:
python ./6_check_similarity.py --input ../5_amr_graph_construction/pair_graphs.xml --output test_score_pairs.xml

**Output Examples**

Microtext / ADU mode:
<pair>
    <topic>school_uniforms</topic>
    <type>claim</type>
    <score>0.815</score>
    <file_A>micro_b038</file_A>
    <file_B>micro_b030</file_B>
    <text_A>School uniforms should be introduced in our schools again.</text_A>
    <graph_A># ::snt School uniforms should be introduced in our schools again.
# ::tokens ["School", "uniforms", "should", "be", "introduced", "in", "our", "schools", "again", "."]
# ::ner_tags ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"]
# ::ner_iob ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"]
# ::pos_tags ["NN", "NNS", "MD", "VB", "VBN", "IN", "PRP$", "NNS", "RB", "."]
# ::lemmas ["school", "uniform", "should", "be", "introduce", "in", "our", "school", "again", "."]
(r0 / recommend-01
  :ARG1 (i0 / introduce-02
    :location (s0 / school
      :poss (w0 / we))
    :mod (a0 / again)
    :ARG1 (u0 / uniform
      :mod (s1 / school))))</graph_A>
    <text_B>School uniforms should not be worn in our schools.</text_B>
    <graph_B># ::snt School uniforms should not be worn in our schools.
# ::tokens ["School", "uniforms", "should", "not", "be", "worn", "in", "our", "schools", "."]
# ::ner_tags ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"]
# ::ner_iob ["O", "O", "O", "O", "O", "O", "O", "O", "O", "O"]
# ::pos_tags ["NN", "NNS", "MD", "RB", "VB", "VBN", "IN", "PRP$", "NNS", "."]
# ::lemmas ["school", "uniform", "should", "not", "be", "wear", "in", "our", "school", "."]
(r0 / recommend-01
  :polarity -
  :ARG1 (w0 / wear-01
    :location (s0 / school
      :poss (w1 / we))
    :ARG1 (u0 / uniform
      :mod (s1 / school))))</graph_B>
  </pair>

Minimal-pair mode:
<pair>
    <pair_id>pair_1</pair_id>
    <score>0.857</score>
    <text_A>Tuition fees should not be charged in Germany.</text_A>
    <graph_A># ::snt Tuition fees should not be charged in Germany.
# ::tokens ["Tuition", "fees", "should", "not", "be", "charged", "in", "Germany", "."]
# ::ner_tags ["O", "O", "O", "O", "O", "O", "O", "GPE", "O"]
# ::ner_iob ["O", "O", "O", "O", "O", "O", "O", "B", "O"]
# ::pos_tags ["NN", "NNS", "MD", "RB", "VB", "VBN", "IN", "NNP", "."]
# ::lemmas ["tuition", "fee", "should", "not", "be", "charge", "in", "Germany", "."]
(r0 / recommend-01
  :polarity -
  :ARG1 (c0 / charge-01
    :location (c1 / country
      :name (n0 / name
        :op1 "Germany"))
    :ARG1 (f0 / fee
      :mod (t0 / tuition))))</graph_A>
    <text_B>Tuition fees should not be introduced in Germany.</text_B>
    <graph_B># ::snt Tuition fees should not be introduced in Germany.
# ::tokens ["Tuition", "fees", "should", "not", "be", "introduced", "in", "Germany", "."]
# ::ner_tags ["O", "O", "O", "O", "O", "O", "O", "GPE", "O"]
# ::ner_iob ["O", "O", "O", "O", "O", "O", "O", "B", "O"]
# ::pos_tags ["NN", "NNS", "MD", "RB", "VB", "VBN", "IN", "NNP", "."]
# ::lemmas ["tuition", "fee", "should", "not", "be", "introduce", "in", "Germany", "."]
(r0 / recommend-01
  :ARG1 (i0 / introduce-02
    :location (c0 / country
      :name (n0 / name
        :op1 "Germany"))
    :polarity -
    :ARG1 (f0 / fee
      :mod (t0 / tuition))))</graph_B>
  </pair>

Notes / Caveats
In minimal-pair mode, each minimal pairis expected to contain exactly two sentences.