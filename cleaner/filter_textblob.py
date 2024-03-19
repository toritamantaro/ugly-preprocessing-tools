from typing import Generator, Iterator, List, Dict, Tuple, Union, Optional, overload
from collections import Counter

from textblob import TextBlob

from util.text_tool_base import TextProcessorBase


class PartsFilterTextblob(TextProcessorBase):
    """
    以下を参考にしました
    https://textblob.readthedocs.io/en/dev/quickstart.html#part-of-speech-tagging

    pip install textblob

        from textblob import TextBlob

        wiki = TextBlob("Python is a high-level, general-purpose programming language.")
        print(wiki.tags)

        -> [('Python', 'NNP'), ('is', 'VBZ'), ('a', 'DT'), ('high-level', 'JJ'), ('general-purpose', 'JJ'), ('programming', 'NN'), ('language', 'NN')]

        Noun Phrase Extraction
        wiki.noun_phrases
        -> WordList(['python'])
    """

    def __init__(
            self,
            target_parts: Optional[List[str]] = None,
            threshold: float = 0.9,
            min_length: int = 10,
    ):
        self._target_parts: List[str] = ['NN', 'NNS', 'NNPS', 'NNP', 'SYM'] if target_parts is None else target_parts
        self._threshold: float = threshold
        self._min_length: int = min_length

    @staticmethod
    def parts_count(
            text: str,
            return_word_count: bool
    ) -> Union[Tuple[Counter, int], Tuple[Counter, int, Counter]]:
        parsed = TextBlob(text)

        # 品詞をカウントするためのCounterオブジェクト
        pos_counter = Counter()
        word_counter = Counter()

        all_counts = 0
        for word, pos in parsed.tags:
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
    > python -m cleaner.filter_textblob
    '''

    from util.versatile_tool import stop_watch

    texts = [
        'Between the golden-yellow lotus leaves and stalks, we see swaying white lotus flowers with thick black.',
        'book car ship world text, and school hole dog cat bed car sea.',
        'book car ship dog cat bed sea.',
    ]

    # texts = texts * 3

    parts_filter = PartsFilterTextblob(threshold=0.9, min_length=10)


    @stop_watch
    def func():
        for text in parts_filter(texts):
            print(text)
            # pass


    func()
    #
