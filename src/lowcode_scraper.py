from argparse import ArgumentParser
from myscraper.url_data import BASE_DATA
from myscraper.create_dataset import DatasetCreator, Config, EL_INFO
from typing import Callable

from scraping_info_config import get_unit_airline_review_info_to_be_scraped


def main():
    """
    設定している情報を元にスクレイピングを行う

    Notes:
        事前にBASE_DATA形式のjsonlデータを用意する必要がある
    """

    # =========================
    #          Setting
    # =========================

    parser = ArgumentParser()
    # ブラウザ関連設定
    parser.add_argument('--browser_binary_path', required=True, help='ブラウザの実行ファイル（ex: msedge.exe）までのパス', default='C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe')
    parser.add_argument('--driver_path', required=True, help='ブラウザのドライバ（ex: msedgedriver.exe）までのパス')
    # データパス関連設定
    parser.add_argument('--data_dir', required=True, help='BASE形式のデータが格納されているフォルダまでのパス')
    parser.add_argument('--base_dataset_name', required=True, help='BASE形式データのファイル名（拡張子.jsonlは除く）')
    parser.add_argument('--scraped_dataset_name', required=True, help='取得したデータを格納するファイル名')
    # BASEデータからのサンプリング設定
    parser.add_argument('--do_sampling', default=False, action='store_true', help='BASEデータセットのデータ数が多く、すべてに対してスクレイピングしたくない時にフラグを立てると、ランダムでデータを取得しスクレイピングを行う')
    parser.add_argument('--sampling_num', type=int, default=5, help='サンプリングを行う際に、BASEデータからいくつのデータをランダムで取得するかを設定する。Default to 5')
    # 取得する要素群が1つのWEBサイトに複数あるか否かの設定
    parser.add_argument('--content_layout', required=True, choices=['single', 'multiple'], help='1つのWEBサイトから取得したい要素群（データ）が1つか複数かを指定する（ex: 商品紹介ページのような場合はsingle, レビューページのような場合はmultiple）')
    parser.add_argument('--multiple_top_k', type=int, default=3, help='--content_layoutでmultipleを選択した場合に、1ページから取得する要素群の数を指定する。Default to 3')
    # その他
    parser.add_argument('--csv_encoding_format', default='utf-8-sig', help='jsonlからcsvへ変換する際のEncoding formatを指定する。Default utf-8-sig')
    args = parser.parse_args()

    """
    下のinfo_to_be_scrapedは自力で記述。より良い方法は検討中
    """
    if args.content_layout == 'single':
        info_to_be_scraped: dict[str, EL_INFO] = None
    elif args.content_layout == 'multiple':
        unit_info_to_be_scraped: Callable[[int], dict[str, EL_INFO]] = lambda index: get_unit_airline_review_info_to_be_scraped(index)

    # =========================
    #       End of Seting
    # =========================

    config = Config(
        browser_binary_path=args.browser_binary_path,
        driver_path=args.driver_path,
        data_dir=args.data_dir,
        dataset_name_base=args.base_dataset_name,
        dataset_name_scd=args.scraped_dataset_name,
        auto_save=True
    )

    dc = DatasetCreator(config)
    sampled_dataset: list[BASE_DATA] = dc.get_application_number_dataset(do_sampling=args.do_sampling, sampling_num=args.sampling_num)

    if args.content_layout == 'single':
        scraped_data = dc.get_product_info_list(sampled_dataset, info_to_be_scraped)
    elif args.content_layout == 'multiple':
        for i in range(args.multiple_top_k):
            new_file: bool = True if i==0 else False
            scraped_data = dc.get_product_info_list(sampled_dataset, unit_info_to_be_scraped(i+1), new_file=new_file)

    dc.convert_jsonl_to_csv(mode='scd', encoding=args.csv_encoding_format)


if __name__ == '__main__':
    main()
