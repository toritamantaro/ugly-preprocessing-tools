from typing import Dict, Generator, Iterator, List, Union, Optional, overload, Type

from wtpsplit import WtP

from util.text_tool_base import TextSplitterBase


class WtpSplit(TextSplitterBase):
    """
    文分割（sentence segmentation）を行う既存モジュールwtpsplitの動作確認のために作成したラッパー
    make_pipeline()で処理を連結するために作成
    wtpsplit単独で処理する場合は、このクラスを使用する必要はありません。

    wtpsplit
    https://github.com/bminixhofer/wtpsplit
    """

    def __init__(
            self,
            lang_doce: str = 'en',
            model_name: str = "wtp-bert-mini",
            do_paragraph_segmentation: bool = False,
    ):
        self._lang_code: str = lang_doce
        self._model_name: str = model_name
        self._model: Optional[Type[WtP]] = None
        self._do_parag_seg = do_paragraph_segmentation
        self.init_model()

    def init_model(self):
        try:
            self._model = WtP(self._model_name)
            self._model.half().to("cuda")
        except TypeError as e:
            print('catch TypeError:', e)

    def split_handling(
            self,
            text: str,
    ) -> Generator[str, None, None]:
        res = self._model.split(
            text,
            lang_code=self._lang_code,
            do_paragraph_segmentation=self._do_parag_seg
        )
        for line in res:
            yield line


if __name__ == "__main__":
    '''
    > python -m cleaner.splitter_wtpsplit
    '''

    from util.versatile_tool import stop_watch

    # texts = [
    #     'My name is Jonas E. Smith. Please turn to p. 55.',
    # ]

    texts = [
        'Clinical Stanford Emergency Medicine Dept 300 Pasteur Dr Rm M121 https://colab.research.google.com/drive/13nedT0tB3YJV-d5FPdTCjgW49 Alway Bldg MC 5119 Stanford, CA 94305 (650) 725-4492 (office) (650) 736-7605 (fax) Clinical Stanford Emergency Department 900 Welch Rd Ste 350 Stanford, CA 94305 (650) 725-4492 (office) (650) 736-7605 (fax) Additional Info. Stanford Medicine Antibiograms Your Librarian. Every healthcare provider responding to a disaster should have foundational knowledge of disaster medicine. Log in with your SUNet ID. View All Information for Patients & Visitors », Marc and Laura Andreessen Adult Emergency Department. [https://colab.research.google.com/drive/13nedT0tB3YJV-d5FPdTCjgW49y]'
    ]

    # texts = texts * 1_000
    # texts = texts * 3

    splitter = WtpSplit(model_name="wtp-bert-mini")


    @stop_watch
    def func():
        for text in texts:
            print(list(splitter(text)))
            # list(splitter(text))


    func()
