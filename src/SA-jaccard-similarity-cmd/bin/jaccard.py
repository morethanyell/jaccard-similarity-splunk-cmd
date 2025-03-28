#!/usr/bin/env python

import sys
import itertools
from splunklib.searchcommands import \
    dispatch, StreamingCommand, Configuration, Option, validators


@Configuration()
class jaccard(StreamingCommand):

    textfield = Option(
        doc='''
        **Syntax:** **textfield=***<input_field_name>*
        **Description:** The field containing the data.''',
        require=True, validate=validators.Fieldname())

    suffix = Option(
        doc='''
        **Syntax:** **suffix=***<string>*
        **Description:** Gives the output field a suffix for uniqueness. Defaults to the name of the input textfield.''',
        require=False)

    def stream(self, events):

        suffix = self.suffix if self.suffix else self.textfield

        for event in events:

            input_data = event[self.textfield]
            data = [item for item in input_data if item and item.strip()]

            if self.safe_len(data) == 1:
                event[f'jaccard_distance_{suffix}'] = "Invalid MV field (must contain more than 1 item)."
                yield event
                continue

            score = self.avg_jaccard_similarity(self, data)
            event[f'jaccard_distance_{suffix}'] = score
            yield event

    @staticmethod
    def safe_len(data):
        return len(data) if isinstance(data, list) else 1

    @staticmethod
    def get_ngrams(string, n=2):
        return set(string[i:i+n] for i in range(len(string) - n + 1))

    @staticmethod
    def jaccard_similarity(self, a, b, n=2):
        intersection = len(a & b)
        union = len(a | b)
        return intersection / union if union else 0

    @staticmethod
    def avg_jaccard_similarity(self, data, n=2):
        ngram_map = {s: self.get_ngrams(s, n) for s in data}
        similarities = [
            self.jaccard_similarity(self, ngram_map[a], ngram_map[b])
            for a, b in itertools.combinations(data, 2)
        ]
        return sum(similarities) / len(similarities) if similarities else 0


dispatch(jaccard, sys.argv, sys.stdin, sys.stdout, __name__)