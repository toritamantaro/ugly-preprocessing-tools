# coding: UTF-8

from typing import Generator, Iterator, List, Dict, Tuple, Union, Optional, overload, Any
import itertools

from util.text_tool_base import TextProcessorBase, TextSplitterBase


class ParagraphCleaningDirector(TextProcessorBase):
    """ Director of cleaning process for each paragraph

    """

    def __init__(
            self,
            paragraph_splitter: [TextSplitterBase] = None,
            sentence_cleaner: [TextProcessorBase] = None
    ):
        self._paragraph_splitter: [TextSplitterBase] = paragraph_splitter
        self._sentence_cleaner: [TextProcessorBase] = sentence_cleaner
        self._sentence_endings: List[str] = ['。', '！', '？', '.', '!', '?', "．", "」", '"']

    @staticmethod
    def split_text_into_paragraphs(text: str) -> List[str]:
        """
        textを改行文字で段落に分割
        """
        return text.splitlines()

    def split_paragraphs_into_sentences(self, paragraphs: List[str]) -> List[List[str]]:
        """
        List[段落]の要素（段落）をself._paragraph_splitter()で文章毎に分割
        """
        return [list(self._paragraph_splitter(paragraph)) for paragraph in paragraphs]  # List[List[str]]
        # return  list(map(lambda x: list(self._paragraph_splitter(x)), paragraphs))  # List[List[str]]
        # return list(map(self._paragraph_splitter, paragraphs))  # List[Generator[str]]

    @staticmethod
    def concat_sentences_into_paragraphs(group_of_sentences: List[List[str]]) -> List[str]:
        """
        List[List[文章]]の要素（List[文章]）を結合して段落に戻す
        """
        # print(group_of_sentences)
        return ["".join(sentences) for sentences in group_of_sentences]

    @staticmethod
    def concat_paragraphs_into_text(paragraphs: List[str]) -> str:
        """
        List[段落]の要素（段落）を結合してtextに戻す
        """
        return "\n".join(paragraphs)

    @staticmethod
    def remove_duplicate_elements(container: Iterator) -> List:
        """
        同一の要素が連続する場合に削除する
        """
        return [next(g) for _, g in itertools.groupby(container)]

    def sentences_cleaner(self, sentences: List[str]) -> List[str]:
        """
        List[文章]の要素（文章）をself._sentence_cleaner()でクリーニングし、重複削除
        """
        new_sentences = [list(self._sentence_cleaner(sentence)) for sentence in sentences]
        # new_sentences = list(map(self._sentence_cleaner, sentences))

        new_sentences = itertools.chain.from_iterable(new_sentences)
        new_sentences = self.remove_duplicate_elements(new_sentences)
        return new_sentences

    def paragraphs_cleaner(self, paragraphs: List[List[str]]) -> List[List[str]]:
        """
        List[List[文章]]の要素（List[文章]）をself.sentences_cleaner()でクリーニング
        """
        new_paragraphs = [self.sentences_cleaner(paragraph) for paragraph in paragraphs]
        return new_paragraphs

    @staticmethod
    def clean_line_endings(paragraphs: List[List[str]], endings: List[str]) -> List[List[str]]:
        """ endingsで指定した記号で終わっている要素のみを取り出す """
        ''' 空要素除去 '''
        paragraphs = [[s for s in p if s != ''] for p in paragraphs if p != '']
        ''' 文末記号以外の文字を削除する '''
        paragraphs = [[s for s in p if (s[-1] in endings) or (len(p) < 2)] for p in paragraphs]
        return paragraphs

    def process_handling(
            self,
            text: str,
    ) -> str:
        """
        単純なパイプラインの連結だけでは実現できない sentence segmentation, cleaning, concatenation
        といった複数の処理をまとめたもの
        """

        '''---- normalize ----'''
        # 別途用意したものをpipelineで前処理として連結すれば良いと思う。ここでは行わない

        '''---- sentence segmentation ----'''
        paragraphs = self.split_text_into_paragraphs(text)
        paragraphs_divided_into_sentences = self.split_paragraphs_into_sentences(paragraphs)

        '''---- paragraphs cleaning ----'''
        new_paragraphs = self.paragraphs_cleaner(paragraphs_divided_into_sentences)
        new_paragraphs = self.clean_line_endings(new_paragraphs, self._sentence_endings)
        # print('removed', new_paragraphs)

        '''---- concat paragraphs ----'''
        new_paragraphs = self.concat_sentences_into_paragraphs(new_paragraphs)
        new_paragraphs = self.remove_duplicate_elements(new_paragraphs)
        text = self.concat_paragraphs_into_text(new_paragraphs)

        '''---- text filter ----'''
        # 別途用意したものをパイプラインで後処理として連結すれば良いと思う。ここでは行わない

        return text


if __name__ == "__main__":
    '''
    > python -m cleaner.director_paragraph_filter
    '''
    from util.text_tool_base import make_pipeline
    from util.versatile_tool import stop_watch
    from cleaner.filter_mecab import PartsFilterMecab

    import functools
    from ja_sentence_segmenter.concatenate.simple_concatenator import concatenate_matching
    from ja_sentence_segmenter.normalize.neologd_normalizer import normalize
    from ja_sentence_segmenter.split.simple_splitter import split_newline, split_punctuation

    parts_filter = PartsFilterMecab(threshold=0.9, min_length=10, parts_index=4, split_key="-")
    # parts_filter = PartsFilterMecab(threshold=0.9, min_length=10, parts_index=1, split_key=",")

    split_punc2 = functools.partial(split_punctuation, punctuations=r"。!?")
    concat_tail_te = functools.partial(concatenate_matching, remove_former_matched=False)
    splitter = make_pipeline(normalize, split_newline, concat_tail_te, split_punc2)

    cleaner = ParagraphCleaningDirector(
        paragraph_splitter=splitter,
        sentence_cleaner=parts_filter
    )

    texts = [
        "まとめ | エキサイトブログ 生八つ橋のタグまとめ。ブログ、生八つ橋、日記、記録、写真、レビュー、噂、まとめ。\n「生八つ橋」タグの記事（4）。 色々な生八つ橋を買ってきました。我が家はみんな八つ橋ファンなのです～。我が家はみんな八つ橋ファンなのです～。色々な生八つ橋を買ってきました。\n Yさんは。「八つ橋なんてもう何年も食べたことないわ～～～」と仰っていましたが、いや",
    ]

    # texts = texts * 1_000
    texts = texts * 2


    @stop_watch
    def func():
        for text in cleaner(texts):
            print(text)
            # pass


    func()
