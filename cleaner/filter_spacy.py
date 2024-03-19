from typing import Generator, Iterator, List, Dict, Tuple, Union, Optional, overload
from collections import Counter

import spacy

from util.text_tool_base import TextProcessorBase


class PartsFilterSpacy(TextProcessorBase):
    """
    以下を参考にしました
    https://spacy.io/usage/models

    pip install spacy

    python -m spacy download en_core_web_sm


    import spacy

    nlp = spacy.load("en_core_web_sm")

    doc = nlp("Clinical ... PdTCjgW49y]")
    print([(w.text, w.pos_) for w in doc])

    ('Medicine', 'PROPN')
    ('-', 'SYM')
    ('https://colab.research.google.com/drive/13nedT0tB3YJV-d5FPdTCjgW49', 'PROPN')
    ('fax', 'NOUN')
    ('(', 'PUNCT')
    ('https://colab.research.google.com/drive/13nedT0tB3YJV-d5FPdTCjgW49y', 'X')
     ('.', 'PUNCT'),
     ('[', 'X')

    """
    def __init__(
            self,
            target_parts: Optional[List[str]] = None,
            threshold: float = 0.9,
            min_length: int = 10,
            model_name: str = 'en_core_web_sm',
    ):
        self._target_parts: List[str] = ['NOUN', 'PROPN', 'SYM', 'PUNCT', 'X'] if target_parts is None else target_parts
        self._threshold: float = threshold
        self._min_length: int = min_length
        self._nlp_name:str = model_name
        self._nlp = spacy.load(self._nlp_name)

    def parts_count(
            self,
            text: str,
            return_word_count: bool
    ) -> Union[Tuple[Counter, int], Tuple[Counter, int, Counter]]:
        parsed = self._nlp(text)

        # 品詞をカウントするためのCounterオブジェクト
        pos_counter = Counter()
        word_counter = Counter()

        all_counts = 0
        for p in parsed:
            word = p.text
            pos = p.pos_
            if not pos.isalpha():
                continue
            if return_word_count:
                word_counter[(word, pos)] += 1
            pos_counter[pos] += 1
            all_counts += 1

        counts = (pos_counter, all_counts)
        if return_word_count:
            counts = counts + (word_counter,)

        return counts

    def process_handling(
            self,
            text: str,
    ) -> str:
        if text is None:
            # return None
            return ""

        pos_counter, all_counts = self.parts_count(text, return_word_count=False)

        parts_counts = 0
        for parts in self._target_parts:
            parts_counts += pos_counter.get(parts, 0)

        # print(text, pos_counter, all_counts)
        ratio = 1.0 if all_counts == 0 else parts_counts / all_counts
        # ratio = parts_counts / all_counts
        # print(ratio, pos_counter)

        if ratio > self._threshold and len(text) > self._min_length:
            # return None
            return ""
        return text


if __name__ == "__main__":
    '''
    > python -m cleaner.filter_spacy
    '''

    from util.versatile_tool import stop_watch

    texts = [
        'Between the golden-yellow lotus leaves and stalks, we see swaying white lotus flowers with thick black.',
        'book car ship world text, and school hole dog cat bed car sea.',
        'book car ship dog cat bed sea.',
    ]

    texts = texts * 1000  # 16.16sec
    # texts = texts * 3

    parts_filter = PartsFilterSpacy(threshold=0.9, min_length=10)

    @stop_watch
    def func():
        for text in parts_filter(texts):
            # print(text)
            pass

    func()

