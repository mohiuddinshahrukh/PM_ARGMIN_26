import sys


class SmatchScorer:
    """Wrapper for calculating Smatch scores safely."""

    def __init__(self):
        try:
            import smatch
            self.smatch = smatch
        except ImportError:
            print("Error: 'smatch' library not found. Run: pip install smatch")
            sys.exit(1)

    def clean_amr(self, raw_text):
        """Removes comments and newlines from AMR strings."""
        if not isinstance(raw_text, str): return ""
        lines = raw_text.split('\n')
        # Filter out comment lines (#) and empty lines
        valid = [line.strip() for line in lines if line.strip() and not line.strip().startswith('#')]
        return " ".join(valid)

    def calculate(self, str1, str2):
        s1 = self.clean_amr(str1)
        s2 = self.clean_amr(str2)

        if not s1 or not s2: return 0.0

        try:
            # Calculate F-Score (Logic from File 6)
            best_match, test_total, gold_total = self.smatch.get_amr_match(s1, s2)
            if test_total == 0 or gold_total == 0: return 0.0

            precision = best_match / float(test_total)
            recall = best_match / float(gold_total)

            if precision + recall > 0:
                return (2 * precision * recall) / (precision + recall)
        except Exception:
            pass

        return 0.0
