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

        for event in events:

            data = event[self.textfield]
            suffix = self.suffix if self.suffix else self.textfield

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
        return [string[i:i+n] for i in range(len(string) - n + 1)]

    @staticmethod
    def jaccard_similarity(self, a, b, n=2):
        a_ngrams = set(self.get_ngrams(a, n))
        b_ngrams = set(self.get_ngrams(b, n))

        return len(a_ngrams & b_ngrams) / len(a_ngrams | b_ngrams)

    @staticmethod
    def avg_jaccard_similarity(self, data, n=2):
       
        similarities = [
            self.jaccard_similarity(self, a, b, n) for a, b in itertools.combinations(data, 2)
        ]

        mean = sum(similarities) / len(similarities)

        return mean if similarities else 0


dispatch(jaccard, sys.argv, sys.stdin, sys.stdout, __name__)