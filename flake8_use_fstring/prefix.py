import re
import token as _token
from typing import Iterator, Tuple

from flake8.options.manager import (
    OptionManager as _OptionManager,
)

from .base import (
    BaseLogicalLineChecker as _Base,
)

FSTRING_REGEX = re.compile(r'^([a-zA-Z]*?[fF][a-zA-Z]*?){1}["\']')
NON_FSTRING_REGEX = re.compile(
    r'^[a-zA-Z]*(?:\'\'\'|\'|"""|")(.*?{.+?}.*)(?:\'|\'\'\'|"|""")$')


class MissingPrefixDetector(_Base):
    name = 'use-fstring-prefix'
    version = '1.0'
    greedy = '0'
    enabled = False

    def __getitem__(self, i: int) -> bool:
        if (not self.enabled):
            return False

        token = self.tokens[i]
        if token.exact_type != _token.STRING:
            return False

        if FSTRING_REGEX.search(token.string):  # already is an f-string
            return False

        # look ahead for % or .format and skip if present
        for next_index, next_token in enumerate(self.tokens[i + 1:], i + 1):
            if next_token.exact_type == _token.STRING:
                continue
            if next_token.exact_type == _token.PERCENT:
                return False
            if next_token.exact_type == _token.DOT:
                try:
                    next_token = self.tokens[next_index + 1]
                    if next_token.exact_type != _token.NAME:
                        break
                    if next_token.string == 'format':
                        return False
                except IndexError:
                    pass
            break

        value = token.string.replace('{{', '').replace('}}', '')
        return NON_FSTRING_REGEX.search(value) is not None

    def __call__(self, i: int) -> str:
        return 'FS003 f-string missing prefix'

    def __iter__(self) -> Iterator[Tuple[Tuple[int, int], str]]:
        for i in range(len(self.tokens)):
            if not self[i]:
                continue
            yield self.tokens[i].start, self(i)

    @classmethod
    def add_options(cls, option_manager: _OptionManager):
        option_manager.add_option(
            f'--{cls.OPTION_NAME}',
            action='store_true',
            default=False,
            parse_from_config=True,
        )

    g = None

    @classmethod
    def parse_options(cls, options):
        option_var = cls.OPTION_NAME.replace('-', '_')
        cls.enabled = vars(options)[option_var]

    OPTION_NAME = 'fstring-missing-prefix'
