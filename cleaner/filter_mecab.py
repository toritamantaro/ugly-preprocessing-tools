from typing import Generator, Iterator, List, Dict, Tuple, Union, Optional, overload
from collections import Counter

import MeCab

from util.text_tool_base import TextProcessorBase


class PartsFilterMecab(TextProcessorBase):
    """
    以下を参考にしました
    https://github.com/KanHatakeyama/JapaneseWarcParser/blob/main/mc4s/src/cleaner/parts_filter.py

    以下でインストールした時のもの
    !pip install mecab-python3 unidic-lite
    - >
        self._parts_index: int = 4
        self._split_key: str = '-'


    こっちのインストール方法だと、parse時の出力が変わります
    !apt install mecab -y
    !apt install libmecab-dev -y
    !apt install mecab-ipadic-utf8 -y
    !ln -s /etc/mecabrc /usr/local/etc/mecabrc #https://hakasenote.hnishi.com/2020/20200719-mecab-neologd-in-colab/
    !pip install mecab-python3
    - >
        self._parts_index: int = 1
        self._split_key: str = ','
    """

    def __init__(
            self,
            target_parts: Optional[List[str]] = None,
            threshold: float = 0.9,
            min_length: int = 10,
            parts_index: int = 4,
            split_key: str = "-",
    ):
        self._target_parts: List[str] = ['名詞', '記号', '補助記号'] if target_parts is None else target_parts
        self._threshold: float = threshold
        self._min_length: int = min_length
        self._parts_index: int = parts_index
        self._split_key: str = split_key
        self._tagger = MeCab.Tagger()

    def parts_count(
            self,
            text: str,
            return_word_count: bool
    ) -> Union[Tuple[Counter, int], Tuple[Counter, int, Counter]]:
        parsed = self._tagger.parse(text)
        # print(parsed)

        # 品詞をカウントするためのCounterオブジェクト
        pos_counter = Counter()
        word_counter = Counter()

        # 解析結果を行ごとに処理
        all_counts = 0
        for line in parsed.split('\n'):
            # EOSまたは空行の場合はスキップ
            if line == 'EOS' or line == '':
                continue
            # タブで分割し、形態素情報を取得
            pos_info = line.split('\t')
            # print(pos_info)
            # pos = pos_info[1]
            pos = pos_info[self._parts_index]
            # pos = pos.split(",")[0]
            pos = pos.split(self._split_key)[0]

            if return_word_count:
                word = pos_info[0]
                word_counter[(word, pos)] += 1

            # 品詞をカウント
            pos_counter[pos] += 1
            all_counts += 1

        if return_word_count:
            return pos_counter, all_counts, word_counter
        else:
            return pos_counter, all_counts

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
        # print(ratio, pos_counter)

        if ratio > self._threshold and len(text) > self._min_length:
            # return None
            return ""
        return text


if __name__ == "__main__":
    '''
    > python -m cleaner.filter_mecab
    '''

    from util.versatile_tool import stop_watch

    texts = [
        'まとめ|エキサイトブログ生八つ橋のタグまとめ。',
        'ブログ、生八つ橋、日記、記録、写真、レビュー、噂、まとめ。',
        'ブログ、生八つ橋。',
    ]

    # texts = [
    #     'Between the golden-yellow lotus leaves and stalks, we see swaying white lotus flowers with thick black.',
    #     'book car ship world text, and school hole dog cat bed car sea.',
    #     'book car ship dog cat bed sea.',
    # ]

    texts = texts * 3

    parts_filter = PartsFilterMecab(threshold=0.9, min_length=10)

    @stop_watch
    def func():
        for text in parts_filter(texts):
            print(text)
            # pass

    func()
