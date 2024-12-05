import time
import datetime
import functools


def get_now(utc: int = +9) -> datetime.datetime:
    """現在の年月日と時刻を取得

    Args:
        utc (int, optional): 標準時から何時間ずれているかを指定できる。+9は日本時刻を表す。Defaults to +9.
    """
    dt_now = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=utc)))
    # print(dt_now.strftime('%Y-%m-%d %H:%M:%S'))
    return dt_now


def measure_exe_time(func):
    """実行時間を計測するdecorator
    """
    functools.wraps(func)
    def _wrapper(*args, **kwargs):
        print(f"START: {get_now().strftime('%Y-%m-%d %H:%M:%S')}")

        start_time = time.time()
        v = func(*args, **kwargs)
        end_time = time.time()

        exe_time = end_time - start_time
        hours, remainder = divmod(exe_time, 3600)
        minutes, seconds = divmod(remainder, 60)
        formatted_time = f'{int(hours)}h {int(minutes)}m {int(seconds)}s'
        print(f'The execution time of the {func.__name__} func is {formatted_time}')

        return v
    return _wrapper
