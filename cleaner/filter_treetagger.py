from typing import Generator, Iterator, List, Dict, Tuple, Union, Optional, overload
from collections import Counter

import treetaggerwrapper as ttw

from util.text_tool_base import TextProcessorBase


class PartsFilterTreetagger(TextProcessorBase):
    """
    遅い

    以下を参考にしました
    https://github.com/KanHatakeyama/JapaneseWarcParser/blob/main/mc4s/src/cleaner/parts_filter.py

    https://qiita.com/3000manJPY/items/1c553a89b2c70edaa960

    install
    https://www.cis.uni-muenchen.de/%7Eschmid/tools/TreeTagger/

    windowsの場合はパッケージのダウンロードなどが必要
    """

    def __init__(
            self,
            target_parts: Optional[List[str]] = None,
            threshold: float = 0.9,
            min_length: int = 10,
            language: str = 'en',
    ):
        self._target_parts: List[str] = ['NN', 'NNS', 'NPS', 'NP', ':', '$'] if target_parts is None else target_parts
        self._threshold: float = threshold
        self._min_length: int = min_length
        self._language: str = language

        self._tagger = ttw.TreeTagger(TAGLANG=self._language)

    def parts_count(
            self,
            text: str,
            return_word_count: bool
    ) -> Union[Tuple[Counter, int], Tuple[Counter, int, Counter]]:

        parsed = self._tagger.TagText(text)
        # print(parsed)

        # pos = pos.split(self._split_key)[0]

        # 品詞をカウントするためのCounterオブジェクト
        pos_counter = Counter()
        word_counter = Counter()

        all_counts = 0
        for line in parsed:
            # EOSまたは空行の場合はスキップ
            if line == 'EOS' or line == '':
                continue
            # タブで分割し、形態素情報を取得
            pos_info = line.split('\t')
            word = pos_info[2]
            pos = pos_info[1]
            if not pos.isalpha():
                continue

            # print(word, ' ', pos)
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

        ratio = parts_counts / all_counts
        print(ratio, pos_counter)

        if ratio > self._threshold and len(text) > self._min_length:
            # return None
            return ""
        return text


if __name__ == "__main__":
    '''
    > python -m cleaner.filter_treetagger
    '''

    from util.versatile_tool import stop_watch

    texts = [
        'Between the golden-yellow lotus leaves and stalks, we see swaying white lotus flowers with thick black.',
        'book car ship world text, and school hole dog cat bed car sea.',
        'book car ship dog cat bed sea.',
    ]

    # texts = texts * 3

    parts_filter = PartsFilterTreetagger(threshold=0.9, min_length=10)


    @stop_watch
    def func():
        for text in parts_filter(texts):
            print(text)
            # pass


    func()
