# coding: UTF-8

from typing import Generator, Iterator, List, Dict, Tuple, Union, Optional, overload, Type, Any
from collections import Counter

from cleantext import clean

from util.text_tool_base import TextProcessorBase


class FilterCleantext(TextProcessorBase):
    """
    以下を参考にしました
    https://github.com/jfilter/clean-text

    !pip install clean-text[gpl]
    """

    def __init__(
            self,
            lang: str = 'en',
    ):
        self._lang = lang

    def process_handling(
            self,
            text: str,
    ) -> str:
        clean_text = clean(text,
                           fix_unicode=True,  # fix various unicode errors
                           to_ascii=True,  # transliterate to closest ASCII representation
                           lower=False,  # lowercase text
                           no_line_breaks=False,  # fully strip line breaks as opposed to only normalizing them
                           no_urls=True,  # replace all URLs with a special token
                           no_emails=True,  # replace all email addresses with a special token
                           no_phone_numbers=True,  # replace all phone numbers with a special token
                           no_numbers=False,  # replace all numbers with a special token
                           no_digits=False,  # replace all digits with a special token
                           no_currency_symbols=False,  # replace all currency symbols with a special token
                           no_punct=False,  # remove punctuations
                           replace_with_punct="",  # instead of removing punctuations you may replace them
                           replace_with_url="",
                           replace_with_email="",
                           replace_with_phone_number="",
                           replace_with_number="",
                           replace_with_digit="",
                           replace_with_currency_symbol="",
                           lang=self._lang  # set to 'de' for German special handling
                           )

        return clean_text


if __name__ == "__main__":
    '''
    > python -m cleaner.filter_hojichar
    '''

    from util.versatile_tool import stop_watch

    texts = [
        'Between the golden-yellow lotus leaves and stalks, we see swaying white lotus flowers with thick black.',
        'book car ship world text, and school hole dog cat bed car sea.',
        'book car ship dog cat bed sea.',
    ]

    # texts = texts * 3

    parts_filter = FilterCleantext()


    @stop_watch
    def func():
        # for text in texts:
        #     print(list(parts_filter(text)))

        for text in parts_filter(texts):
            print(text)
            # pass


    func()
