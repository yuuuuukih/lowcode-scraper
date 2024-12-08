# LOWCODE-SCRAPER

## 必要なもの

### 1. ブラウザ関連
- このPJTではブラウザとしてMicrosoft Edgeを採用している
- 公式サイトよりEdgeをインストール後、Edgeの検索タブに`edge://version`と入力することで、インストールされているEdgeのバージョンを確認する
- [Microsoft Edge WebDriver](https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/?form=MA13LH)から自身の環境にあったdriverをダウンロード。Edgeのバージョンと揃える必要がある

### 2. BASEデータセットの用意
- このPJTではスクレイピング対象となるURLが整理されたBASEデータセットが必要となる
- BASEデータセットはjsonl形式を採用しており、フォーマットは以下
```base_dataset.jsonl
{"id": "000001", "url": "https://www.xxx.com/aaaaaaaaaa/"}
{"id": "000002", "url": "https://www.xxx.com/bbbbbbbbbb/"}
{"id": "000003", "url": "https://www.xxx.com/cccccccccc/"}
...
```
- 各データは`id`と`url`をキーに持つ

### 3. BASEデータセットのURL先WEBページにおけるcontent_layoutの確認
- content_layoutでは、スクレイピング対象となるWEBページを、1つのWEBサイトから取得したい要素群（データ）が1つか複数かで、single／multipleの2種類の分類する
    - 商品紹介ページにて、商品名・価格・製造元という1つのページから1つの要素群（データ）を取得する場合はsingle
    - レビューページにて、コメントしている人の名前・コメント内容・評価星数・like数という要素群（データ）を1つのページから複数データ取得する場合はmultiple
- 今回スクレイピングするWEBサイトがどちらに分類されるかを、事前に認識しておく必要がある

### 4. info_to_be_scrapedの定義
- 各ページで取得したい要素を以下のフォーマットで定義する
```scraping_info_config.py
info_to_be_scraped = {
    'user_name': {
        'css_selector': f'body > div > main > xxx > p',
        'func': lambda value: value
    },
    'score': {
        'css_selector': f'body > div > main > xxx > p',
        'func': lambda value: sp.safe_int(value.replace(' / 10', '').strip())
    },
    'comment': {
        'css_selector': f'body > div > main > xxx > p',
        'func': lambda value: value
    }
}
```

## 実行

### 1. 実行ファイル



### 2. 指定引数
