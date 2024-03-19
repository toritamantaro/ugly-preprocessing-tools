import datasets
from datasets import load_dataset

from util.text_tool_base import make_pipeline
from util.versatile_tool import stop_watch
from cleaner.filter_mecab import PartsFilterMecab
from cleaner.filter_nltk import PartsFilterNltk
from cleaner.director_paragraph_filter import ParagraphCleaningDirector
from cleaner.filter_norm_jp import NormalizeFilterJp
from cleaner.filter_hojichar import FilterHojichar, JA_LIST, EN_LIST
from cleaner.splitter_blingfire import BlingfireSplit


def main():
    ''' 処理前のデータローダの中身確認 '''
    # dataset_name = "cerebras/SlimPajama-627B"
    dataset_name = "DKYoon/SlimPajama-6B"
    dataset_stream = load_dataset(dataset_name, split='train', streaming=True)

    for record in list(dataset_stream.take(3)):
        print(record)

    print('------------------------------------------------')

    ''' --- 処理されたデータローダの生成 --- '''

    ## 一連の処理をまとめたパイプラインを作る
    ''' normalize '''
    text_normalizer = NormalizeFilterJp()

    ''' paragraph cleaning '''
    paragraph_splitter = BlingfireSplit()
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

    ## データローダをマップする関数を用意
    ## https://huggingface.co/docs/datasets/stream#map

    def process_filter(example):
        example['text'] = list(processor(example['text']))
        return example

    ## フィルタリングされたデータローダを生成
    filted_dataset = dataset_stream.map(process_filter)
    for record in list(filted_dataset.take(3)):
        print(record)

    print('------------------------------------------------')


if __name__ == "__main__":
    main()
