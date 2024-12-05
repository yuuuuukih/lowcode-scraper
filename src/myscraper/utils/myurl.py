class myurl:
    """URLに関する処理の管理を行う。
    """

    @classmethod
    def join_url(cls, root_url: str, id: str) -> str:
        """root urlとそれに続くパスを指定することでURLに変換する

        Args:
            root_url (str): root url
            id (str): root urlに続くパス

        Returns:
            (str): rootのURLとそれに続く相対アドレスを結合し、URLを文字列として返す
        """
        return f"{root_url.rstrip('/')}/{id.lstrip('/').rstrip('/')}/"  

    @classmethod
    def join_urls(cls, *args: str) -> str:
        """引数の順番に結合し、URLに変換する
        """
        for i in range(len(args)):
            if i == 0:
                next_str: str = args[0]
                continue
            next_str: str = cls.join_url(next_str, args[i])
        return next_str
