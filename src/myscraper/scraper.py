import os
import time
from typing import TypedDict, Callable, TypeVar

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options


"""
スクレイピングで取得した情報をdictionary形式としてまとめる際の型。TypedDict-likeを想定。
"""
INFO_TYPE = TypeVar('INFO_TYPE')

class EL_INFO(TypedDict):
    """スクレイピングで取得したい要素に関する情報をまとめる際の型

    configで設定する際に必要な引数内で使用する

    Notes:
        - css_selector: 取得したい要素のCSS SELECTOR
        - func: スクレイピングで取得する要素を加工する関数。要素はstring形式で取得されるため、不必要な文字列を除去したりint等別の型に変換したりすることを想定。
        - html_attr (optional): テキストではなく要素のHTML属性を取得したい場合は指定。'title'等を指定可能。
    """
    css_selector: str
    func: Callable[[str], str | int | float]
    html_attr: str


class Scraper:
    """スクレイピングで要素を取得

    このコードではブラウザにEdgeを用いている。
    使用する場合はhttps://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH から、各々の環境にあったdriverをダウンロードする必要がある。
    そのうえで、msedge.exeとmsedgedriver.exeまでのパスを、set_edge_pathから設定する必要がある。
    """
    def __init__(self) -> None:
        """コンストラクタ
        
        Notes:
            - msedge.exeとmsedgedriver.exeまでのパスを、set_edge_pathから設定する
            - driverのoptionは適宜変更
        """
        # Set tha path for browser
        self.set_edge_path(
            edge_binary_path=r'/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge',
            edge_driver_path=r'/Volumes/ext-ssd/program_files/lowcode-scraper/Microsoft Edge WebDriver arm64/msedgedriver.exe'
        )
        # Set the options for scraping
        self.options = Options()
        self.options.binary_location = self.edge_binary_path
        self.options.add_argument('--headless') # headless mode
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--blink-settings=imagesEnabled=false') # no images
        self.options.add_argument('--disable-background-networking') # disable extensions, translation, ...
        self.options.add_argument('--disable-extensions') # disable extensions
        self.options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.117 Safari/537.36 Edg/79.0.309.65')
        self.options.add_argument('--log-level=3')
        self.options.add_argument('--disable-logging')
        self.options.add_experimental_option('excludeSwitches',["enable-automation", "enable-logging"])
        # self.options.add_argument(f'--proxy-server={os.environ["PROXY"]}')  # For proxy
 
    def set_edge_path(self, edge_binary_path, edge_driver_path) -> None:
        """Edgeに関するバイナリーファイルのパスを設定

        Args:
            edge_binary_path (str): msedge.exeまでのパス
            edge_driver_path (str): ダウンロードできるedge用のドライバーmsedgedriver.exeまでのパス
        """
        self.edge_binary_path = edge_binary_path
        self.edge_driver_path = edge_driver_path

    def scrape_data(self, url: str, id: str, info_to_be_scraped: dict[str, EL_INFO]) -> INFO_TYPE:
        """1つのURLからinfo_to_be_scrapedで設定した要素に関してスクレイピングし、dictionary形式で取得

        Args:
            url (str): スクレイピングするURL
            id (str): 取得したデータに振るunique idを設定する。往々にしてurlがidになり得る。
            info_to_be_scraped (dict[str, EL_INFO]): スクレイピングで取得したい要素について、それぞれのEL_INFOをdictinayとしてまとめたもの。
        
        Returns:
            INFO_TYPE: info_to_be_scrapedのkeyとそれらのスクレイピング結果に、idとurl情報を追加しdictionary形式でまとめたもの
        """

        def _fetch_element(key: str, no_el_val: str = 'null', html_attr: str = '') -> str:
            """BeautifulSoupで取得したhtmlを解析し、要素を取得

            Args:
                key (str): info_to_be_scrapedで設定したkey
                no_el_val (str, optional): 要素を取得できなかった場合に返す文字列を設定する。Defaults to 'null'.
                html_attr (str, optional): タグに囲まれたテキストではなく、タグのhtml属性(href, title等)を取得したい場合に指定する
            
            Returns:
                str: スクレイピングで取得した要素。テキストであることに注意。
            """
            try:
                if len(html_attr) == 0:
                    el = soup.select_one(info_to_be_scraped[key]['css_selector']).text
                else:
                    el = soup.select_one(info_to_be_scraped[key]['css_selector']).get(html_attr)
            except AttributeError:
                el = no_el_val
            return el
        
        driver = webdriver.Edge(service=Service(self.edge_driver_path), options=self.options)

        try:
            time.sleep(3)
            driver.get(url)
            driver.implicitly_wait(10)

            html = driver.page_source.encode('utf-8')
            soup = BeautifulSoup(html, 'html.parser')

            product_info: INFO_TYPE = {
                'id': id,
            }
            for key,  info in info_to_be_scraped.items():
                try:
                    html_attr = info['html_attr']
                except KeyError:
                    html_attr = ''

                try:
                    product_info[key] = info['func'](_fetch_element(key, html_attr=html_attr))
                except Exception as e:
                    print(e)
                    print(url)
                    print(key)
                    print(info)

            product_info['url'] = url

        finally:
            driver.quit()
        return product_info
    
    @classmethod
    def safe_int(cls, v: str) -> int | str | None:
        """安全にint型に変換
        
        _fetch_elementがno_el_evalとして数字以外を返す可能性があるため

        Args:
            v: intに変換したいテキスト
        
        Returns:
            int | str: int型に変換できない場合は、文字列としてそのまま返す
        """
        if v != None:
            try:
                int_v = int(v)
            except ValueError:
                int_v = v
            return int_v
    
    @classmethod
    def safe_float(cls, v: str) -> float | str | None:
        """安全にfloat型に変換
        
        _fetch_elementがno_el_evalとして数字以外を返す可能性があるため

        Args:
            v: floatに変換したいテキスト

        Returns:
            float | str: float型に変換できない場合は、文字列としてそのまま返す
        """
        if v != None:
            try:
                int_v = float(v)
            except ValueError:
                int_v = v
            return int_v
