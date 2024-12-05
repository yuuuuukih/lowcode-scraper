import json
import csv

class jsonl:
    """jsonlに関する処理のクラス
    """
    
    @classmethod
    def load_jsonl(cls, path: str) -> list[dict]:
        """.jsonlのpathを受け取り、list[dict]の形式で取得する。

        Args:
            path (str): 今回追加したい.jsonlまでのパス

        Returns:
            list[dict]: dictionaryデータをリストにまとめて返す
        """
        return [json.loads(line) for line in open(path, 'r', encoding='utf-8')]


    @classmethod
    def add_line_to_jsonl(cls, line: dict, path: str, not_first_line: bool = True, new_file: bool = True, encoding: str = 'utf-8') -> None:
        """.jsonlに対して、dictionary形式のデータを1つ追加

        Args:
            line (dict): .jsonlに追加したいdict型のデータ
            path (str): 今回追加したい.jsonlまでのパス
            not_first_line (bool, optional): 今回追加するdict型のデータが、.jsonlにおいて1行目か否か。1行目となる場合Falseを指定する。Defaults to True.
            new_file (bool, optional): 新しくファイルを作成する場合はTrue、Falseの場合は既にデータがある.jsonlに追加する形となる。Defaults to True.
            encoding (str, optional): .jsonlに書き込む際のencodeタイプを指定。Default utf-8.
        """
        cond: bool = not new_file or not_first_line
        mode = 'a' if cond else 'w'
        # mode = 'a' if cond and new_file else 'w'
        with open(path, mode=mode, encoding=encoding) as F:
            if cond:
                F.write('\n')
            json.dump(line, F, ensure_ascii=False)


    @classmethod
    def save_as_jsonl(cls, l: list[dict], path: str, encoding: str = 'utf-8') -> None:
        """新しく.jsonlを作成し、dictionary形式のデータを複数追加

        Args:
            l (list[dict]): .jsonlに追加したいdict型のデータを要素として持つリスト
            path (str): 今回追加したい.jsonlまでのパス
            encoding (str, optional): .jsonlに書き込む際のencodeタイプを指定。Default utf-8.
        """
        for i, item in enumerate(l):
            cls.add_line_to_jsonl(item, path, not_first_line=bool(i), encoding=encoding)
        print(f'Dataset (jsonl) is saved to {path} ')

    @classmethod
    def to_csv(cls, jsonl_path: str, csv_path: str, encoding: str = 'shift-jis', cp932: bool = False) -> None:
        """既存のjsonlファイルをcsvファイルに変更

        Args:
            jsonl_path (str): 変換したいjsonlファイルまでのパス
            csv_path (str): 今回保存したいcsvファイルまでのパス
            encoding (str, optional): csvファイルに書き込む際のencodeタイプ。Default shift-jis.
            cp932 (bool, optional): cp932にてencodingする。Defaults to False.
        """
        def _save_as_csv(arg_encoding):
            dataset_jsonl = cls.load_jsonl(jsonl_path)
            with open(csv_path, 'w', newline='', encoding=arg_encoding) as F:
                # dataset_jsonlの上位10個のデータを見て、もっともkey数が多いデータのkeyをCSVのヘッダーとする
                i_argmax = max(range(len(dataset_jsonl[:10])), key=lambda i: len(dataset_jsonl[i]))
                fieldnames = list(dataset_jsonl[i_argmax].keys())

                writer = csv.DictWriter(F, fieldnames=fieldnames)
                writer.writeheader()

                cant_encode_str: list[str] = ['\u203c', '\u2014', '\ufe0f', '\ufe0e']
                for row in dataset_jsonl:
                    for k, _ in row.items():
                        for c in cant_encode_str:
                            v = row[k]
                            if type(v) == str and c in v:
                                row[k] = v.replace(c, '')

                    try:
                        writer.writerow(row)
                    except UnicodeEncodeError as e:
                        print(f'{row=}')
                        print(e)
                        raise ValueError('here (to_csv method in jsonl.py')
        
        if cp932:
            # _save_as_csv(arg_encoding='cp932')
            try:
                _save_as_csv(arg_encoding='shift-jis')
            except UnicodeEncodeError as e:
                _save_as_csv(arg_encoding='cp932')
                print(e)
                print('Encoded by cp932')
        else:
            _save_as_csv(arg_encoding=encoding)

