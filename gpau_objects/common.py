import sys
import json
from datetime import datetime
from typing import List, Dict, Optional

class Logger:
    VERBOSE: bool = True
    TYPES: Dict[str, str] = {
        'info': '\033[94m',
        'success': '\033[92m',
        'warning': '\033[93m',
        'interesting': '\033[36m',
        'error': '\033[91m',
        'fatal': '\033[95m',
        'end': '\033[0m'
    }
    WAS_SAME_LINE: bool = False
    LAST_LINE_LENGTH: int = 0
    ENABLED: bool = True
    VERBOSE_TYPES: List[str] = []

    @staticmethod
    def enable(enabled: bool=True) -> None:
        Logger.ENABLED = enabled

    @staticmethod
    def disable() -> None:
        Logger.ENABLED = False

    @staticmethod
    def write(message: str, ltype: str='info') -> None:
        if not Logger.ENABLED:
            return
        if Logger.VERBOSE_TYPES and ltype not in Logger.VERBOSE_TYPES:
            return
        padding = Logger.LAST_LINE_LENGTH - len(message)
        Logger.LAST_LINE_LENGTH = len(message)
        if Logger.WAS_SAME_LINE and padding > 0:
            message += ' ' * padding
        sys.stdout.write(message)

    @staticmethod
    def get_message(message: str, ltype: str='info', show_time: bool=True, color: Optional[str]=None) -> str:
        time = datetime.now().strftime('%H:%M:%S.%f')[:-3]
        parts = []
        color = color or (Logger.TYPES[ltype] if ltype in Logger.TYPES else Logger.TYPES['info'])
        if show_time: parts.append(color + '['+time+']' + Logger.TYPES['end'])
        parts.append(color + ltype.upper() + Logger.TYPES['end'])
        parts.append('>')
        parts.append(message)
        return " ".join(parts)

    @staticmethod
    def nl() -> None:
        Logger.write("\n", "newline")

    @staticmethod
    def log(message: str, ltype: str='info', show_time: bool=True, color: Optional[str]=None) -> None:
        message = Logger.get_message(message, ltype, show_time, color)
        if Logger.WAS_SAME_LINE:
            message = "\n" + message
            Logger.WAS_SAME_LINE = False
        Logger.write(message + "\n", ltype)

    @staticmethod
    def info(message: str) -> None:
        Logger.log(message, 'info')

    @staticmethod
    def success(message: str) -> None:
        Logger.log(message, 'success')

    @staticmethod
    def warning(message: str) -> None:
        Logger.log(message, 'warning')

    @staticmethod
    def error(message: str) -> None:
        Logger.log(message, 'error')

    @staticmethod
    def critical(message: str) -> None:
        Logger.log(message, 'fatal')

    @staticmethod
    def error_exit(message: str, exit_code: int=1) -> None:
        Logger.critical(message)
        sys.exit(exit_code)

    @staticmethod
    def json(message: str, ltype: str='json', show_time: bool=True) -> None:
        Logger.log(json.dumps(message, quote_keys=True, trailing_commas=False, indent=4), ltype, show_time)

    @staticmethod
    def same_line(message: str, ltype: str='info', show_time: bool=True) -> None:
        message = Logger.get_message(message, ltype, show_time).rstrip()
        Logger.write("\r" + message, ltype)
        Logger.WAS_SAME_LINE = True

    @staticmethod
    def progress(
        message: str,
        index: int=0,
        total: int=0,
        every_nth: int=1,
        ltype: str='....',
        show_time: bool=True,
        show_percentage: bool=True,
        show_index: bool=True,
        not_same_line: bool=False
    ) -> None:
        total = total - 1
        if total <= 0:
            return
        if index % every_nth != 0 and index != total and index != 0:
            return
        percentage = round(index / total * 100, 2)
        statuses = []
        if message: statuses.append(message)
        if show_percentage: statuses.append(f"[{percentage}%]")
        if show_index: statuses.append(f"({index}/{total})")
        if not_same_line:
            Logger.log(" ".join(statuses), ltype, show_time)
        else:
            Logger.same_line(" ".join(statuses), ltype, show_time)

    @staticmethod
    def colorized(message: str, ltype: str='info') -> None:
        color = Logger.TYPES[ltype] if ltype in Logger.TYPES else Logger.TYPES['info']
        print(color + message + Logger.TYPES['end'])
