import os
from typing import List, Dict, Optional, Callable, Type
import requests
from collections import defaultdict

import datasets
from datasets import load_dataset
from datasets import Dataset, DatasetDict
from datasets.iterable_dataset import IterableDataset
from huggingface_hub import HfApi
from huggingface_hub import login


class DatasetFileInfoMediator(object):
    def __init__(
            self,
            path: str,
            name: Optional[str] = None,
            api_token: Optional[str] = None,
    ):
        """
        Huggingface datasetのparquetファイルリストを取得するためのクラス

        Parameters
        ----------
        path: str
            huggingface dataset repository e.g. 'uonlp/CulturaX'
        name: str
            huggingface dataset repository の name e.g. 'en'
        api_token: str
            huggingface アクセス用のAPIトークン
        """
        self._path = path
        self._name = name
        self._api_token = api_token

    @staticmethod
    def get_web_response(
            url: str,
            api_token: Optional[str],
    ):
        headers = {"Authorization": f"Bearer {api_token}"} if api_token else None
        response = requests.get(url, headers=headers)
        msg = f'''
          Failed to access.
          Check to see if you need an api-token to access information.
          The currently designated api-token is {api_token}.
        '''
        assert response, msg
        return response

    def get_api_parquet_info(
            self,
            api_token: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """
        web-apiとしてparquetファイルを直接ダウンロードするためのアドレスを取得
        e.g.
        'https://huggingface.co/api/datasets/DKYoon/SlimPajama-6B/parquet/default/test/0.parquet'
        """
        token = api_token if api_token else self._api_token
        file_type: str = 'parquet'
        url = f"https://huggingface.co/api/datasets/{self._path}/{file_type}"

        response = self.get_web_response(url, token)
        urls_dict = response.json()
        name = self._name if self._name else 'default'
        return urls_dict.get(name)

    def get_parquet_info(
            self,
            api_token: Optional[str] = None,
    ) -> Dict[str, List[str]]:
        """
        dataset_load()などを介してdatasetをダウンロードするためのアドレスを取得
        e.g.
        'https://huggingface.co/datasets/DKYoon/SlimPajama-6B/resolve/refs%2Fconvert%2Fparquet/default/test/0000.parquet'
        """
        token = api_token if api_token else self._api_token
        file_type: str = 'parquet'
        url = f"https://datasets-server.huggingface.co/{file_type}?dataset={self._path}"

        response = self.get_web_response(url, token)
        urls_dict = response.json()

        parquet_list: List[Dict] = urls_dict.get('parquet_files')
        '''
        urls_dict['parquet_files']
        e.g.
        {'config': 'af','split': 'test', 'url': 'https://huggingface.co/datasets/.../0000.parquet', 'size': 23625527}
        {'config': 'af','split': 'train', 'url': 'https://huggingface.co/datasets/.../0000.parquet', 'size': 292286056}
          ...
        {'config': 'af','split': 'train', 'url': 'https://huggingface.co/datasets/.../0047.parquet', 'size': 296397064}
        {'config': 'af','split': 'validation', 'url': 'https://huggingface.co/datasets/.../0000.parquet', 'size': 23013126}
        '''
        name = self._name if self._name else 'default'
        new_dict = defaultdict(list)
        for rec in parquet_list:
            if rec['config'] != name:
                continue
            new_dict[rec['split']].append(rec['url'])
        return dict(new_dict)


class HubPushProcessedParquetFile(object):
    def __init__(
            self,
            map_func: Callable[[Dict], Dict],
            api_token: str,
            upload_repo: str,  # 'ttaront/filted_clx'
            # upload_dir:str,  # 'en', 'train/chunk'
            file_name_head: str = '',
    ):
        """
        参照するdatasetのparquetファイルパスを与えてデータをダウンロードし、
        self._mapfunc()でdataset.map()処理したのちに、指定したHuggingfaceHubに
        ファイルをpushするクラス

        Parameters
        ----------
        map_func:
            dataset.map()に渡して、datasetに対して行う処理を定義した関数
        api_token:
            huggingface アクセス用のAPIトークン
            書き込みの許可が認められたものが必要
        upload_repo:
            アップロード先のHuggingfaceHubのrepository e.g. 'ttaront/filted_clx'
        file_name_head:
            アップロードするファイル名の先頭に追加する文字（任意）
            オリジナルのファイル名の先頭に名前を追加する
        """
        self._map_func = map_func
        self._token = api_token
        self._upload_repo = upload_repo
        self._name_head = file_name_head

    def __call__(
            self,
            parquet_path: str,
            upload_dir: str,  # 'en', 'train/chunk'
            file_name_head: Optional[str] = None,
    ):
        """
        Parameters
        ----------
        parquet_path: str
            ダウンロードする*.parquetファイルのアドレス
        upload_dir: str
            アップロードファイルを格納するRepositoryのディレクトリを指定
        file_name_head: str
            アップロードするファイル名の先頭に追加する文字（任意）
            オリジナルのファイル名の先頭に名前を追加する
        """
        login(token=self._token)
        org_dataset_dict = load_dataset('parquet', data_files=parquet_path)
        org_name = parquet_path.split('/')[-1]  # *.parquet

        ''' 
        読み込んだDatasetDictは以下のように1つのDatasetを含んでいるという想定
        DatasetDict({
            train: Dataset({
                features: ['text', 'meta'],
                num_rows: 115092
            })
        })
        '''
        ds_group = org_dataset_dict.values()
        assert len(ds_group) == 1, f"The number of loaded dataset is not 1. ({len(ds_group)} datasets)"
        ds = next(iter(ds_group))

        # クリーニング処理
        filtered_ds = ds.map(self._map_func)

        # 空要素の場合除去
        filtered_ds = filtered_ds.filter(lambda example: example['text'] != "")

        # parquetファイルをローカルに保存
        chash_file = "tmp.parquet"
        filtered_ds.to_parquet(chash_file)
        org_dataset_dict.cleanup_cache_files()

        # 処理後のparquetファイルをアップロード
        name_head = file_name_head if file_name_head else self._name_head
        upload_path = f'/{upload_dir}/{name_head}{org_name}'
        api = HfApi()
        api.upload_file(
            path_or_fileobj=chash_file,
            path_in_repo=upload_path,
            repo_id=self._upload_repo,
            repo_type="dataset",
        )
        os.remove(chash_file)
