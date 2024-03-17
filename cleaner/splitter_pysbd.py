
from typing import Dict, Generator, Iterator, List, Union, Optional, overload, Type

import pysbd

from util.text_tool_base import TextSplitterBase


class PysbdSplit(TextSplitterBase):
    """
    文分割（sentence segmentation）を行う既存モジュールpysbdの動作確認のために作成したラッパー
    make_pipeline()で処理を連結するために作成
    pysbd単独で処理する場合は、このクラスを使用する必要はありません。

    pysbd
    https://github.com/nipunsadvilkar/pySBD
    """

    def __init__(
            self,
            language: str = 'en',
            clean:bool = False,
    ):
        self._language: str = language
        self._clean: bool = clean
        self._segmenter = pysbd.Segmenter(language=self._language, clean=self._clean)

    def split_handling(
            self,
            text: str,
    ) -> Generator[str, None, None]:
        res = self._segmenter.segment(text)

        for line in res:
            yield line


if __name__ == "__main__":
    '''
    > python -m cleaner.splitter_pysbd
    '''

    from util.versatile_tool import stop_watch

    # texts = [
    #     'My name is Jonas E. Smith. Please turn to p. 55.',
    # ]

    texts = [
        'Clinical Stanford Emergency Medicine Dept 300 Pasteur Dr Rm M121 https://colab.research.google.com/drive/13nedT0tB3YJV-d5FPdTCjgW49 Alway Bldg MC 5119 Stanford, CA 94305 (650) 725-4492 (office) (650) 736-7605 (fax) Clinical Stanford Emergency Department 900 Welch Rd Ste 350 Stanford, CA 94305 (650) 725-4492 (office) (650) 736-7605 (fax) Additional Info. Stanford Medicine Antibiograms Your Librarian. Every healthcare provider responding to a disaster should have foundational knowledge of disaster medicine. Log in with your SUNet ID. View All Information for Patients & Visitors », Marc and Laura Andreessen Adult Emergency Department. [https://colab.research.google.com/drive/13nedT0tB3YJV-d5FPdTCjgW49y]'
    ]

    texts = texts * 1_000  # 1.998671sec
    # texts = texts * 3

    splitter = PysbdSplit(language='en')

    @stop_watch
    def func():
        for text in texts:
            # print(list(splitter(text)))
            list(splitter(text))

    func()


