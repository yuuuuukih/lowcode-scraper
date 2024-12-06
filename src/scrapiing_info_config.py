from myscraper.scraper import Scraper as sp
from myscraper.create_dataset import EL_INFO

def get_unit_airline_review_info_to_be_scraped(index: int) -> dict[str, EL_INFO]:
    """航空会社のレビューサイトからコメント等を取得するための情報を定義

    Args:
        index (int): 複数のコメントの取得に際し、CSSセレクタ内にて変化する数字の部分の受け取る
    
    Returns:
        (dict[str, EL_INFO]): 各航空会社のコメントに関して、info_to_be_scraped形式の要素を返す
    """

    unit_airline_review_info_to_be_scraped: dict[str, EL_INFO] = {
        'user_name': {
            'css_selector': f'body > div > main > div.w-full.max-w-full.overflow-x-clip.flex-grow > div > div:nth-child(3) > div > div > div > div.flex.flex-col.space-y-12.items-start.w-full > a:nth-child({index}) > div.flex.flex-row.items-center.space-x-2 > div > p:nth-child(1)',
            'func': lambda value: value
        },
        'score': {
            'css_selector': f'body > div > main > div.w-full.max-w-full.overflow-x-clip.flex-grow > div > div:nth-child(3) > div > div > div > div.flex.flex-col.space-y-12.items-start.w-full > a:nth-child({index}) > div.flex.flex-row.items-center.space-x-1.mt-4 > p',
            'func': lambda value: sp.safe_int(value.replace('/10', '').strip())
        },
        'comment': {
            'css_selector': f'body > div > main > div.w-full.max-w-full.overflow-x-clip.flex-grow > div > div:nth-child(3) > div > div > div > div.flex.flex-col.space-y-12.items-start.w-full > a:nth-child({index}) > div.flex.flex-col.gap-8.w-full.items-start > p',
            'func': lambda value: value
        }
    }

    return unit_airline_review_info_to_be_scraped
    
