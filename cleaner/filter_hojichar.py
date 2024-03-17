# coding: UTF-8

from typing import Generator, Iterator, List, Dict, Tuple, Union, Optional, overload, Type, Any
from collections import Counter

import hojichar
from hojichar import Compose, document_filters
import json

from util.text_tool_base import TextProcessorBase

base_path = "cleaner/hoji_dict/"

JA_LIST: List[hojichar.Filter] = [
    document_filters.JSONLoader(key="text"),
    document_filters.AcceptJapanese(),
    document_filters.DiscardRareKuten(),
    document_filters.DocumentLengthFilter(min_doc_len=100, max_doc_len=50000),
    document_filters.DiscardAdultContentJa(
        base_path + "adult_keywords_ja.txt"),
    document_filters.DiscardAdultContentEn(
        base_path + "adult_keywords_en.txt"
    ),
    document_filters.DiscardDiscriminationContentJa(
        base_path + "discrimination_keywords_ja.txt"
    ),
    document_filters.DiscardViolenceContentJa(
        base_path + "violence_keywords_ja.txt"
    ),
    document_filters.DiscardBBSComments(),
    document_filters.DiscardAds(
        base_path + "advertisement_keywords_ja.txt"
    ),
    document_filters.MaskPersonalInformation(),
    # document_filters.ExampleHojiChar(),
    document_filters.JSONDumper()
]

EN_LIST: List[hojichar.Filter] = [
    document_filters.JSONLoader(key="text"),
    document_filters.DocumentLengthFilter(min_doc_len=100, max_doc_len=50000),
    document_filters.DiscardAdultContentEn(
        base_path + "adult_keywords_en.txt"
    ),
    document_filters.NgWordsFilterEn(
        base_path + "ng_keywords_en.txt"
    ),
    document_filters.DiscardBBSComments(),
    document_filters.MaskPersonalInformation(),
    # document_filters.ExampleHojiChar(),
    document_filters.JSONDumper()
]



class FilterHojichar(TextProcessorBase):
    """
    以下を参考にしました
    https://github.com/KanHatakeyama/JapaneseWarcParser/blob/main/mc4s/src/cleaner/hojichar_filter.py

    """

    def __init__(
            self,
            filter_list: List[hojichar.Filter] = None
    ):
        self._filter_list: List[hojichar.Filter] = JA_LIST if filter_list is None else filter_list
        self._cleaner: Compose = Compose(self._filter_list)

    def process_handling(
            self,
            text: str,
    ) -> str:
        d = {"text": text}
        # print(d)
        parsed = self._cleaner(json.dumps(d))
        # print(parsed)
        if parsed == "":
            return ""
        text = json.loads(parsed)["text"]
        return text


if __name__ == "__main__":
    '''
    > python -m cleaner.filter_hojichar
    '''

    from util.versatile_tool import stop_watch

    texts = [
        "生八つ橋のタグまとめ | エキサイトブログ 生八つ橋のタグまとめ 「生八つ橋」のタグがついている新着記事と人気記事をまとめました。エキサイトブログには生八つ橋に関連するブログ（日記、記録、写真、レビュー、噂、まとめ）がたくさん投稿されています。 「生八つ橋」タグの記事（4） 生八つ橋いろいろ 京都旅行のお土産(我が家用)に色々な生八つ橋を買ってきました。我が家はみんな八つ橋ファンなのです～。地元の方達や京都を案内してくれたYさんは「八つ橋なんてもう何年も食べたことないわ～～～」と仰っていましたが、いやいや、美味しいですよ～～！！私は大好きです！まぁ確かに私は東京出身ですが、雷おこしや人形焼きは食べませんからね～。それと同じことでしょうか＾＾；とはいえ、舟和の芋ようかんや東京ばな奈... 2020/03/06 23:54",
        "【エロ動画】くりくり瞳のショートヘアの女の子にシコってもらってムハァーーーーーー！！(*ﾟ∀ﾟ)=3 アダルトMAX-無修正と無料動画- エロ くりくり瞳のショートヘアの女の子にシコってもらってムハァーーーーーー *ﾟ∀ﾟ =3 TOP > エロ くりくり瞳のショートヘアの女の子にシコってもらってムハァーーーーーー *ﾟ∀ﾟ =3 投稿日:2015-08-02 01:00:16 カテゴリー エロ*ﾟ∀ﾟ=3 [1]«73298 73299 73300 73301 73302 73303 73304»[138086]",
    ]

    # texts = [
    #     'Between the golden-yellow lotus leaves and stalks, we see swaying white lotus flowers with thick black.',
    #     'book car ship world text, and school hole dog cat bed car sea.',
    #     'book car ship dog cat bed sea.',
    # ]

    # texts = texts * 3

    parts_filter = FilterHojichar(filter_list=JA_LIST)


    @stop_watch
    def func():
        # for text in texts:
        #     print(list(parts_filter(text)))

        for text in parts_filter(texts):
            print(text)
            # pass


    func()
