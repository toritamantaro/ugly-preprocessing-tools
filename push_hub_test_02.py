from cleantext import clean

from util.text_tool_base import make_pipeline
from util.datasets_tool import DatasetFileInfoMediator, HubPushProcessedParquetFile
from cleaner.filter_hojichar import FilterHojichar, JA_LIST, EN_LIST


def normalize_text(original_text):
    clean_text = clean(original_text,
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
                       lang="en"  # set to 'de' for German special handling
                       )
    return clean_text


def main():
    """ クリーニング処理したtextをRepositoryにpushする """

    ''' １．処理したファイルをpushするRepositoryを用意
    この例では、`cerebras/SlimPajama-627B`から*.parquetファイルをダウンロードし、
    dataset.map()でクリーニングしたのちに、別途用意しておいたHuggingfaceHub
    (ttaront/filtered_slimpa)にアップロードします
    予めHuggingfaceHubRepository(ttaront/filtered_slimpa)を作成し、
    README.mdにYAMLでconfigsを設定しておきます
    ここでは、元のdataset`cerebras/SlimPajama-627B`を参考にし、以下のように定義しました

    ---
    task_categories:
    - text-generation
    language:
    - en
    pretty_name: filtered_slimpa
    ---
    
    config_nameは設定されていません
    この状態で、たとえばローカルにある*.parquetをhubの"test"フォルダにuploadすると、testデータとして登録される
    '''

    ''' ２．参照先datasetの*.parquetファイルリストを取得 '''
    path = "cerebras/SlimPajama-627B"
    name = None
    api_token = "hf_************************"

    fm = DatasetFileInfoMediator(path, name, api_token=api_token)

    file_info_dict = fm.get_parquet_info()
    print(file_info_dict)

    # このリストの内容を複数人数で分担すれば良いかと思います
    # ここではテスト用にリストを絞る
    file_info_dict = {
        'test': [
            'https://huggingface.co/datasets/cerebras/SlimPajama-627B/resolve/refs%2Fconvert%2Fparquet/default/partial-test/0000.parquet',
            # 'https://huggingface.co/datasets/cerebras/SlimPajama-627B/resolve/refs%2Fconvert%2Fparquet/default/partial-test/0001.parquet',
        ],
        'train': [
            'https://huggingface.co/datasets/cerebras/SlimPajama-627B/resolve/refs%2Fconvert%2Fparquet/default/partial-train/0000.parquet',
            # 'https://huggingface.co/datasets/cerebras/SlimPajama-627B/resolve/refs%2Fconvert%2Fparquet/default/partial-train/0001.parquet',
        ],
        'validation': [
            'https://huggingface.co/datasets/cerebras/SlimPajama-627B/resolve/refs%2Fconvert%2Fparquet/default/partial-validation/0000.parquet',
            # 'https://huggingface.co/datasets/cerebras/SlimPajama-627B/resolve/refs%2Fconvert%2Fparquet/default/partial-validation/0001.parquet',
        ]
    }

    ''' ３．クリーニング用のmap関数を用意 '''

    ''' text filter '''
    text_filter = FilterHojichar(filter_list=EN_LIST)

    ''' make pipline '''
    processor = make_pipeline(
        text_filter,
    )

    ''' dataset.map() に渡す関数を定義 
    !!! ここ(cleaning_tool())の処理内容を任意に書き換えてください !!!
    '''

    def cleaning_tool(example):
        text = normalize_text(example["text"])
        example["text"] = "".join(list(processor(text)))
        return example

    ''' ４．クリーニング処理を適用しpushする '''
    upload_repo = 'ttaront/filtered_slimpa'  # push先のRepository
    push_file = HubPushProcessedParquetFile(
        map_func=cleaning_tool,
        api_token=api_token,
        upload_repo=upload_repo,
        file_name_head='',  # オリジナルのファイル名の先頭に名前を追加。任意。
    )

    for key, val in file_info_dict.items():
        for org_path in val:
            upload_dir = key  # アップロードファイルを格納するRepositoryのディレクトリを指定
            push_file(parquet_path=org_path, upload_dir=upload_dir)


if __name__ == "__main__":
    main()
