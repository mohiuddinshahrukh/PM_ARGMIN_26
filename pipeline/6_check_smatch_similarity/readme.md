# AMR Similarity (Smatch) Computation

This script computes Smatch similarity between AMR graphs stored in an input XML or CSV file.

**Input format**

The input file must be produced at the previous step (see amr generation script). The file contains a column named: graph - AMR

Depending on the mode, additional columns are expected:

**Usage Examples**

python ./6_check_similarity.py --input pipeline_redone/5_amr_graph_construction/results/test.xml --topic school_uniforms --type claim --output test_smatch.xml

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