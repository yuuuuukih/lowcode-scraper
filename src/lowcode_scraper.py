import re
from argparse import ArgumentParser
from myscraper.url_data import BASE_DATA
from myscraper.create_dataset import DatasetCreator, Config, EL_INFO
from myscraper.scraper import Scraper as sp
from datetime import datetime
from typing import Literal, Callable

from scrapiing_info_config import get_unit_airline_review_info_to_be_scraped


def main():
    """
    設定している情報を元にスクレイピングを行う

    Notes:
        事前にBASE_DATA形式のjsonlデータを用意する必要がある
    """

    TOPK: int = 10
    DATA_DIR = '/Volumes/ext-ssd/program_files/lowcode-scraper/data'
    BASE_DATASET_NAME = 'base_reviews'
    SCRAPED_DATASET_NAME = 'airline_reviews'
    DO_SAMPLING = False
    unit_info_to_be_scraped = lambda index: get_unit_airline_review_info_to_be_scraped(index)

    config = Config(
        data_dir=DATA_DIR,
        dataset_name_base=BASE_DATASET_NAME,
        dataset_name_scd=SCRAPED_DATASET_NAME,
        auto_save=True
    )

    dc = DatasetCreator(config)
    sampled_dataset: list[BASE_DATA] = dc.get_application_number_dataset(do_sampling=DO_SAMPLING, sampling_num=10)
    for i in range(TOPK):
        new_file: bool = True if i==0 else False
        scraped_data = dc.get_product_info_list(sampled_dataset, unit_info_to_be_scraped(i+1))



if __name__ == '__main__':
    main()
