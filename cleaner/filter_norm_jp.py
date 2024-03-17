# coding: UTF-8

from typing import Generator, Iterator, List, Dict, Tuple, Union, Optional, overload
from collections import Counter
import re
import unicodedata

from util.text_tool_base import TextProcessorBase

UNICODE_PUNCT = {
    # 日本語の場合は句読点は、。のままがよいでしょう
    "。": "。",
    "、": "、",
    "，": "、",

    "„": '"',
    "”": '"',
    "“": '"',
    "«": '"',
    "»": '"',
    "１": '"',
    "」": '"',
    "「": '"',
    "《": '"',
    "》": '"',
    "´": "'",
    "∶": ":",
    "：": ":",
    "？": "?",
    "！": "!",
    "（": "(",
    "）": ")",
    "；": ";",
    "–": "-",
    "—": " - ",
    "．": ". ",
    "～": "~",
    "’": "'",
    "…": "...",
    "━": "-",
    "〈": "<",
    "〉": ">",
    "【": "[",
    "】": "]",
    "％": "%",
    "►": "-",
}

UNICODE_PUNCT_RE = re.compile(f"[{''.join(UNICODE_PUNCT.keys())}]")


def replace_unicode_punct(text: str) -> str:
    return "".join((UNICODE_PUNCT.get(c, c) for c in text))


def remove_unicode_punct(text: str) -> str:
    """More aggressive version of replace_unicode_punct but also faster."""
    return UNICODE_PUNCT_RE.sub("", text)


# Reuse `strip_accents` for CJK text. Use NFKC
def strip_accents(line: str) -> str:
    """Strips accents from a piece of text."""
    # nfd = unicodedata.normalize("NFD", line)
    nkfc = unicodedata.normalize("NFKC", line)
    output = [c for c in nkfc if unicodedata.category(c) != "Mn"]
    if len(output) == line:
        return line
    return "".join(output)


# Build a regex matching all control characters.
# newline(LF, 10) has meaningful infor in CJK text, so do not remove it.
NON_PRINTING_CHARS_RE = re.compile(
    f"[{''.join(map(chr, list(range(0, 10)) + list(range(11, 32)) + list(range(127, 160))))}]"
)
DIGIT_RE = re.compile(r"\d")
PUNCT_OR_NON_PRINTING_CHARS_RE = re.compile(
    (UNICODE_PUNCT_RE.pattern +
     NON_PRINTING_CHARS_RE.pattern).replace("][", "")
)


def remove_non_printing_char(text: str) -> str:
    return NON_PRINTING_CHARS_RE.sub("", text)


def normalize_spacing_for_tok(text: str, language: str = "en") -> str:
    res = (
        text.replace("\r", "")
        # remove extra spaces
        .replace("(", " (")
        .replace(")", ") ")
        .replace(" +", " ")
    )
    res = re.sub(r"\) ([\.\!\:\?\;\,])", r"\)\1", res)
    res = res.replace("( ", "(").replace(" )", ")")
    res = re.sub(r"(\d) \%", r"\1\%", res)
    res = res.replace(" :", ":").replace(" ;", ";")
    res = res.replace("`", "'").replace("''", ' " ')

    res = (
        res.replace("„", '"')
        .replace("“", '"')
        .replace("”", '"')
        .replace("–", "-")
        .replace("—", " - ")
        .replace(" +", " ")
        .replace("´", "'")
        .replace("([a-z])‘([a-z])", r"\1'\2/")
        .replace("([a-z])’([a-z])", r"\1'\2/")
        .replace("‘", '"')
        .replace("‚", '"')
        .replace("’", '"')
        .replace("''", '"')
        .replace("´´", '"')
        .replace("…", "...")
        # French quotes
        .replace(" « ", ' "')
        .replace("« ", '"')
        .replace("«", '"')
        .replace(" » ", '" ')
        .replace(" »", '"')
        .replace("»", '"')
        # handle pseudo-spaces
        .replace(" %", "%")
        .replace("nº ", "nº ")
        .replace(" :", ":")
        .replace(" ºC", " ºC")
        .replace(" cm", " cm")
        .replace(" ?", "?")
        .replace(" !", "!")
        .replace(" ;", ";")
        .replace(", ", ", ")
        .replace(" +", " ")
        .replace("．", ". ")
    )
    # English "quotation," followed by comma, style
    if language == "en":
        res = re.sub(r"\"([,\.]+)", r"\1\"", res)
    # Czech is confused
    elif language == "cs" or language == "cz":
        pass
    # German/Spanish/French "quotation", followed by comma, style
    else:
        res = res.replace(',"', '",')
        res = re.sub(
            r"(\.+)\"(\s*[^<])", r"\"\1\2", res
        )  # don't fix period at end of sentence

    if (
            language == "de"
            or language == "es"
            or language == "cz"
            or language == "cs"
            or language == "fr"
    ):
        res = re.sub(r"(\d) (\d)", r"\1,\2", res)
    else:
        res = re.sub(r"(\d) (\d)", r"\1.\2", res)
    return res


# # NOTE accent=True will do NFKC normalization
# # NOTE: set punct=0(no zenkaku->hankaku conversion) hby default for Japanese dataset
# def normalize(line: str, accent=True, case=False, numbers=False, punct=0) -> str:
#     line = line.strip()
#     if not line:
#         return line
#     if case:
#         line = line.lower()
#
#     # FIXME: Always apply NKFC normalization for CJK text.
#     if accent:
#         line = strip_accents(line)
#     if numbers:
#         line = DIGIT_RE.sub("0", line)
#     if punct == 1:
#         line = replace_unicode_punct(line)
#     elif punct == 2:
#         line = remove_unicode_punct(line)
#     line = remove_non_printing_char(line)
#     return line
#
#
# def slow_normalize_for_dedup(line: str) -> str:
#     return normalize(line, accent=False, case=True, numbers=True, punct=2)
#
#
# def normalize_for_dedup(line: str) -> str:
#     line = line.strip()
#     if not line:
#         return line
#     # case
#     line = line.lower()
#     # numbers
#     line = DIGIT_RE.sub("0", line)
#     line = PUNCT_OR_NON_PRINTING_CHARS_RE.sub("", line)
#     return line


class NormalizeFilterJp(TextProcessorBase):
    """
    以下を参考にしました
    https://github.com/lighttransport/japanese-llama-experiment/blob/main/02_normalize/text_normalizer.py

    """

    def __init__(
            self,
            accent: bool = True,
            case: bool = False,
            numbers: bool = False,
            punct: int = 0,
    ):
        self._accent: bool = accent
        self._case: bool = case
        self._numbers: bool = numbers
        self._punct: int = punct

    # def __init__(
    #         self,
    #         target_parts: Optional[List[str]] = None,
    #         threshold: float = 0.9,
    #         min_length: int = 10,
    #         parts_index: int = 4,
    #         split_key: str = "-",
    # ):
    #     self._target_parts: List[str] = ['名詞', '記号', '補助記号'] if target_parts is None else target_parts
    #     self._threshold: float = threshold
    #     self._min_length: int = min_length
    #     self._parts_index: int = parts_index
    #     self._split_key: str = split_key
    #     self._tagger = MeCab.Tagger()

    def process_handling(
            self,
            text: str,
    ) -> str:
        """
        # NOTE accent=True will do NFKC normalization
        # NOTE: set punct=0(no zenkaku->hankaku conversion) hby default for Japanese dataset
        """
        line = text.strip()
        if not line:
            return line
        if self._case:
            line = line.lower()

        # FIXME: Always apply NKFC normalization for CJK text.
        if self._accent:
            line = strip_accents(line)
        if self._numbers:
            line = DIGIT_RE.sub("0", line)
        if self._punct == 1:
            line = replace_unicode_punct(line)
        elif self._punct == 2:
            line = remove_unicode_punct(line)
        line = remove_non_printing_char(line)
        return line


if __name__ == "__main__":
    '''
    > python -m cleaner.filter_norm_jp
    '''

    from util.versatile_tool import stop_watch

    texts = [
        'まとめ|エキサイトブログ生八つ橋のタグまとめ.',
        'ブログ、生八つ橋、日記,記録、写真、レビュー、噂、まとめ。',
        'ブログ、生八つ橋。',
    ]

    # texts = [
    #     'Between the golden-yellow lotus leaves and stalks, we see swaying white lotus flowers with thick black.',
    #     'book car ship world text, and school hole dog cat bed car sea.',
    #     'book car ship dog cat bed sea.',
    # ]

    texts = texts * 3

    filter = NormalizeFilterJp()


    @stop_watch
    def func():
        for text in filter(texts):
            print(text)
            # pass


    func()
