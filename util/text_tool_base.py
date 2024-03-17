import functools
from typing import Callable, Generator
from typing import Dict, Generator, Iterator, List, Union, Optional, overload, Type, Any
from abc import ABCMeta, abstractmethod


def make_pipeline(
        *funcs: Callable[..., Generator[str, None, None]]
) -> Callable[..., Generator[str, None, None]]:
    """ Make pipeline of generators.

    https://github.com/wwwcojp/ja_sentence_segmenter/blob/main/ja_sentence_segmenter/common/pipeline.py
    """

    def composite(
            func1: Callable[..., Generator[str, None, None]],
            func2: Callable[..., Generator[str, None, None]]
    ) -> Callable[..., Generator[str, None, None]]:
        return lambda x: func2(func1(x))

    return functools.reduce(composite, funcs)


class TextProcessorBase(metaclass=ABCMeta):
    """
    Textに何らか処理を行うジェネレータの抽象基底クラス。
    サブクラスにおいて、@abstractmethodであるprocess_handling()をオーバーライドして利用してください。
    """

    def __call__(
            self,
            input_data: Union[str, List[str], Iterator[str]],
    ) -> Generator[str, None, None]:
        return self.process(input_data)

    @abstractmethod
    def process_handling(
            self,
            text: str,
    ) -> str:
        raise NotImplementedError

    def __process_iter(
            self,
            texts: Iterator[str],
    ) -> Generator[str, None, None]:
        for text in texts:
            # print(text)
            yield self.process_handling(text)

    @overload
    def process(self, input_data: str) -> Generator[str, None, None]:
        pass

    @overload
    def process(self, input_data: List[str]) -> Generator[str, None, None]:
        pass

    @overload
    def process(self, input_data: Iterator[str]) -> Generator[str, None, None]:
        pass

    def process(
            self,
            input_data: Union[str, List[str], Iterator[str]],
    ) -> Generator[str, None, None]:
        if isinstance(input_data, str):
            yield from self.__process_iter(iter([input_data]))
        elif isinstance(input_data, list):
            yield from self.__process_iter(iter(input_data))
        elif isinstance(input_data, Iterator):
            yield from self.__process_iter(input_data)


class TextSplitterBase(metaclass=ABCMeta):
    """
    Textを分割したりするジェネレータの抽象基底クラス。
    サブクラスにおいて、@abstractmethodであるsplit_handling()をオーバーライドして利用してください。
    """

    def __call__(
            self,
            input_data: Union[str, List[str], Iterator[str]],
    ) -> Generator[str, None, None]:
        return self.split(input_data)

    @abstractmethod
    def split_handling(
            self,
            text: str,
    ) -> Generator[str, None, None]:
        raise NotImplementedError

    def __split_iter(
            self,
            texts: Iterator[str],
    ) -> Generator[str, None, None]:
        for text in texts:
            # print(text)
            return self.split_handling(text)

    @overload
    def split(self, input_data: str) -> Generator[str, None, None]:
        pass

    @overload
    def split(self, input_data: List[str]) -> Generator[str, None, None]:
        pass

    @overload
    def split(self, input_data: Iterator[str]) -> Generator[str, None, None]:
        pass

    def split(
            self,
            input_data: Union[str, List[str], Iterator[str]],
    ) -> Generator[str, None, None]:
        if isinstance(input_data, str):
            yield from self.__split_iter(iter([input_data]))
        elif isinstance(input_data, list):
            yield from self.__split_iter(iter(input_data))
        elif isinstance(input_data, Iterator):
            yield from self.__split_iter(input_data)
