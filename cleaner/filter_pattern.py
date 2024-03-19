# coding: UTF-8


from typing import Generator, Iterator, List, Dict, Tuple, Union, Optional, overload
from collections import Counter

import nltk

from util.text_tool_base import TextProcessorBase


class PartsFilterPattern(TextProcessorBase):
    """
    以下を参考にしました
    https://github.com/clips/pattern

    mysqlclientに必要なパッケージ
    sudo apt-get install python3-dev default-libmysqlclient-dev build-essential

    pip install mysqlclient
    pip install pattern




    """
    pass



if __name__ == "__main__":
    '''
    > python -m cleaner.filter_pattern
    '''

    print('pattern test')
    # from pattern.en import parse
    from pattern.en import lemma

    s = 'The mobile web is more important than mobile apps.'
    # s = parse(s, relations=True, lemmata=True)
    print(lemma(s))

    # from util.versatile_tool import stop_watch
    #
    # texts = [
    #     'Between the golden-yellow lotus leaves and stalks, we see swaying white lotus flowers with thick black.',
    #     'book car ship world text, and school hole dog cat bed car sea.',
    #     'book car ship dog cat bed sea.',
    # ]
    #
    # # texts = texts * 3
    #
    # parts_filter = PartsFilterNltk(threshold=0.9, min_length=10)
    #
    #
    # @stop_watch
    # def func():
    #     for text in parts_filter(texts):
    #         print(text)
    #         # pass
    #
    #
    # func()
    #
