import os
import time
import random
from tqdm import tqdm
from typing import Literal


from .url_data import BASE_DATA
from .scraper import INFO_TYPE, EL_INFO, Scraper
from .utils.jsonl import jsonl
from .utils.measure_exe_time import measure_exe_time


class Config:
    """DatasetCreatorの設定用
    """

    def __init__(
            self,
            browser_binary_path: str,
            driver_path: str,
            data_dir: str,
            dataset_name_base = 'base_dataset',
            dataset_name_scd = 'scraped_dataset',
            auto_save: bool = True
        ) -> None:
        """コンストラクタ

        Args:
            browser_binary_path (str): ブラウザの実行ファイル（ex: msedge.exe）までのパス。Scraperに必要
            driver_path (str): ブラウザのドライバ（ex: msedgedriver.exe）までのパス。Scraperに必要
            data_dir (str): dataを管理するディレクトリ。作成するjsonlやcsvはすべてこの直下に保存される。
            dataset_name_base (str, optional): BASE_DATA型のデータを保存するデータセットのファイル名。Default base_dataset.
            dataset_name_scd (str, optional): 製品情報であるINFO_TYPE型×データ数を保存するデータセットのファイル名。Default scraped_dataset.
            auto_save (bool, optional): Auto save。Trueの場合は、スクレイピングで取得した情報が逐次的にdataset_name_scd.jsonlに保存される。Falseは非推奨。Defaults to True.
        """
        self.browser_binary_path = browser_binary_path
        self.driver_path = driver_path
        self.data_dir = data_dir
        self.dataset_name_base = dataset_name_base
        self.dataset_name_scd = dataset_name_scd
        self.auto_save = auto_save
        
class DatasetCreator(Scraper):
    """スクレイピングで要素を取得し、jsonlやcsvとしてデータを保存
    """
    def __init__(self, config: Config) -> None:
        """コンストラクタ

        Args:
            config (Config): 設定したconfig
        """
        super().__init__(config.browser_binary_path, config.driver_path)
        
        self.__data_dir = config.data_dir
        self.__dataset_file_name = {
            'base': config.dataset_name_base,
            'scd': config.dataset_name_scd
        }
        self.__auto_save = config.auto_save

        # 保存するデータセットのパス
        self.__base_data_path = os.path.join(self.__data_dir, f"{self.__dataset_file_name['base']}.jsonl")
        self.__scd_jsonl_path = os.path.join(self.__data_dir, f"{self.__dataset_file_name['scd']}.jsonl")

    def get_application_number_dataset(self, do_sampling: bool = True, sampling_num: int = 10, seed_value: int = 42) -> list[BASE_DATA]:
        """base_datasetから要素をランダムに抽出し、list形式で返す

        Args:
            do_sampling (bool, optional): 抽出するか否か。Defauts to True.
            sampling_num (int, optional): 抽出する場合、いくつの要素を抽出するか。Defaults to 10.
            seed_value (int, optional): ランダムサンプリング用のシード値。Defaults to 42.
        
        Returns:
            list[BASE_DATA]: サンプリングされたBASE_DATAのリスト
        """
        random.seed(seed_value)
        base_dataset: list[BASE_DATA] = jsonl.load_jsonl(self.__base_data_path)
        sampled_dataset: list[BASE_DATA] = random.sample(base_dataset, sampling_num) if do_sampling else base_dataset
        return sampled_dataset

    @measure_exe_time 
    def get_product_info_list(self, base_dataset: list[BASE_DATA], info_to_be_scraped: dict[str, EL_INFO], new_file: bool = True) -> list[INFO_TYPE]:
        """base_datasetを受け取り、すべての要素についてスクレイピングで情報を取得する
        
        Args:
            base_dataset (list[BASE_DATA]): list形式でまとめたBASE_DATA
            info_to_be_scraped (dict[str, EL_INFO]): Scraper用。scraper.pyを参照。
            new_file (bool, optional): スクレイピングで取得したデータを新しいファイルとして上書き保存するかを指定する。既存のファイルに追加したい場合はFalseにする。Defaults to True.

        Returns:
            list[INFO_TYPE]: auto_saveがTrueの場合はからのlistを返す。auto_saveがFalseの場合は取得した情報をlist形式で返す。すべての情報をPCで一時的に保存するため注意が必要。
        """
        product_info_list: list[INFO_TYPE] = []

        for i, base_data in tqdm(enumerate(base_dataset), total=len(base_dataset)):
            product_info: INFO_TYPE = self.scrape_data(base_data['url'], base_data['id'], info_to_be_scraped)
            # たまにページから要素が取得可能であるにもかかわらず取得できずにnullを返すことがあるため、
            # その時は'title'というkeyを用いてもう一度だけやり直すか否かを判定する。
            # （要素が取得可能である場合、titleがnullになるのはおかしいという考えのもと）
            if 'title' in product_info.keys() and product_info['title'] == 'null':
                print('Get product_info again!')
                time.sleep(5)
                product_info: INFO_TYPE = self.scrape_data(base_data['url'], base_data['id'], info_to_be_scraped)

            if self.__auto_save:
                jsonl.add_line_to_jsonl(product_info, self.__scd_jsonl_path, not_first_line=bool(i), new_file=new_file)
            else:
                product_info_list.append(product_info)
        # auto_saveがTrueの場合は、スクレイピングデータを保存しないため、空のリストを返す。
        return product_info_list

    def save_product_info_data(self, product_info_list: list[INFO_TYPE]) -> None:
        """get_product_info_listで取得した情報を保存

        auto_saveがTrueの場合は、既に保存されているため何も実行しない

        Args:
            product_info_list (list[INFO_TYPE]): get_product_info_listで取得した情報をlist形式でまとめたもの
        """
        if self.__auto_save:
            print('auto_save is activated.')
        else:
            jsonl.save_as_jsonl(product_info_list, self.__scd_jsonl_path)

    def convert_jsonl_to_csv(self, mode: Literal['scd', 'base'] = 'scd', encoding = 'shift-jis', cp932: bool = False) -> None:
        """data_dir直下に保存されたjsonlファイルをcsvに変換

        Args:
            mode (Literal['scd', 'base'], optional): 'scd'と'base'をとることができる。scdの場合はdataset_name_scdの名前で保存された.jsonlを、baseの場合はdataset_name_baseの名前で保存された.jsonlをcsvに変換する。Defaults scd.
            encoding (str, optional): csvに書き込む際のencodeタイプを指定。Defaults to shift-jis.
            cp932 (bool, optional): cp932でのencodingを試みる。Trueの場合、まずshift-jisでトライし、失敗した場合にcp932にてencodingする。jsonl.to_csv()用。Defaults to False.
        """
        jsonl_path = os.path.join(self.__data_dir, f'{self.__dataset_file_name[mode]}.jsonl')
        csv_path = os.path.join(self.__data_dir, f'{self.__dataset_file_name[mode]}.csv')
        
        jsonl.to_csv(jsonl_path, csv_path, encoding=encoding, cp932=cp932)

