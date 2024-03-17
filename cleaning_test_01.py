# coding: UTF-8

import functools
from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation

from util.text_tool_base import make_pipeline
from util.versatile_tool import stop_watch
from cleaner.filter_mecab import PartsFilterMecab
from cleaner.filter_nltk import PartsFilterNltk
from cleaner.director_paragraph_filter import ParagraphCleaningDirector
from cleaner.filter_norm_jp import NormalizeFilterJp
from cleaner.filter_hojichar import FilterHojichar, JA_LIST, EN_LIST


def japanese():
    texts = [
        "生八つ橋のタグまとめ | エキサイトブログ 生八つ橋のタグまとめ 「生八つ橋」のタグがついている新着記事と人気記事をまとめました。\nブログ（日記、記録、写真、レビュー、噂、まとめ）投稿。\n 「生八つ橋」タグの記事（4） 生八つ橋いろいろ 京都旅行のお土産(我が家用)に色々な生八つ橋を買ってきました。我が家はみんな八つ橋ファンなのです～。我が家はみんな八つ橋ファンなのです～。\n地元の方達や京都を案内してくれたYさんは。「八つ橋なんてもう何年も食べたことないわ～～～」と仰っていましたが、いやいや.. 2020/03/06 23:54",
        "【エロ動画】くりくり瞳のショートヘアの女の子(*ﾟ∀ﾟ)=3 アダルトMAX-無修正と無料動画- エロ くりくり瞳のショートヘアの女の子ムハァーーーーーー *ﾟ∀ﾟ =3 TOP > エロ くりくり瞳のショートヘアの女の子 *ﾟ∀ﾟ =3 投稿日:2015-08-02 01:00:16 カテゴリー エロ*ﾟ∀ﾟ=3 [1]«73298 73299 73300 73301 73302 73303 73304»[138086]",
    ]

    # texts = texts * 1_000
    # texts = texts * 2

    ''' normalize '''
    text_normalizer = NormalizeFilterJp()

    ''' paragraph cleaning '''
    split_punc = functools.partial(split_punctuation, punctuations=r"。!?")
    concat_tail_te = functools.partial(concatenate_matching, remove_former_matched=False)
    paragraph_splitter = make_pipeline(normalize, split_newline, concat_tail_te, split_punc)

    sentence_cleaner = PartsFilterMecab(threshold=0.9, min_length=10, parts_index=4, split_key="-")
    # sentence_cleaner = PartsFilterMecab(threshold=0.9, min_length=10, parts_index=1, split_key=",")

    paragraph_cleaner = ParagraphCleaningDirector(
        paragraph_splitter=paragraph_splitter,
        sentence_cleaner=sentence_cleaner
    )

    ''' text filter '''
    text_filter = FilterHojichar(filter_list=JA_LIST)

    ''' make pipline '''
    processor = make_pipeline(
        text_normalizer,
        paragraph_cleaner,
        text_filter,
    )

    @stop_watch
    def func():
        for text in processor(texts):
            print(text)
            # pass

    func()


def english():
    texts = [
        "/** * ScriptDev2 is an extension for mangos providing enhanced features for * area triggers, creatures, game objects, instances, items, and spells beyond * the default database scripting in mangos. * * Copyright (C) 2006-2013 ScriptDev2 <http://www.scriptdev2.com/> * * This program is free software; you can redistribute it and/or modify * it under the terms of the GNU General Public License as published by * the Free Software Foundation; either version 2 of the License, or * (at your option) any later version. * * This program is distributed in the hope that it will be useful, * but WITHOUT ANY WARRANTY; without even the implied warranty of * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the * GNU General Public License for more details. * * You should have received a copy of the GNU General Public License * along with this program; if not, write to the Free Software * Foundation, Inc",
        "He Walked with a Zombie Geoffrey O'Brien March 9, 2006 issue The Val Lewton Horror Collection 9 films by Val Lewton DVD box set, $59.98 Icons of Grief: Val Lewton's Home Front Pictures by Alexander Nemerov University of California Press, 213 pp., $60.00; $24.95 (paper) The creative career of Val Lewton—the part with a continuing afterlife—lasted just four years, from the spring of 1942, when pre-production work began on his film Cat People, until April 1946, when Bedlam, the last of the eleven films he produced for RKO, was released. ",
        "I am going to cum, but you can close your eyes and let me cum in your mouth ### Assistant: Oh my god, I can feel it growing in my pussy.Tell me where your hands are. ### Assistant: Mmmm.. tell me where you want them.I want to kiss you first and feel your tounge on mine. ### Assistant: My pussy is just tooo wet..For you",
    ]

    # texts = texts * 1_000
    # texts = texts * 2

    ''' normalize '''
    text_normalizer = NormalizeFilterJp()

    ''' paragraph cleaning '''
    split_punc = functools.partial(split_punctuation, punctuations=r".!?")
    concat_tail_te = functools.partial(concatenate_matching, remove_former_matched=False)
    paragraph_splitter = make_pipeline(normalize, split_newline, concat_tail_te, split_punc)

    sentence_cleaner = PartsFilterNltk(threshold=0.9, min_length=10)

    paragraph_cleaner = ParagraphCleaningDirector(
        paragraph_splitter=paragraph_splitter,
        sentence_cleaner=sentence_cleaner
    )

    ''' text filter '''
    text_filter = FilterHojichar(filter_list=EN_LIST)

    ''' make pipline '''
    processor = make_pipeline(
        text_normalizer,
        paragraph_cleaner,
        text_filter,
    )

    @stop_watch
    def func():
        for text in processor(texts):
            print(text)
            # pass

    func()


if __name__ == "__main__":
    # japanese()
    english()
