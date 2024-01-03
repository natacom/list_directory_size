# -*- coding: utf-8 -*-

from __future__ import annotations
import os
import sys
from tqdm import tqdm
from typing import TypeGuard

output_file = './output.txt'
disc = ('- ')
delimiter = (': ')
indent_base = ('  ')

unitMap = {
    'K': 10 ** 3,
    'M': 10 ** 6,
    'G': 10 ** 9,
    'T': 10 ** 12,
    'P': 10 ** 15,
    'E': 10 ** 18,
}
charMap = {
    0: ' ', 1: '▏', 2: '▎', 3: '▍', 4: '▌', 5: '▋', 6: '▊', 7: '▉', 8: '█',
}


def get_progress(current: float, max: float, char_num: int) -> str:
    ratio = round(current / max * 8 * char_num)
    full_num = ratio // 8
    remain_num = ratio % 8
    return (charMap[8] * full_num + charMap[remain_num]).ljust(char_num)


def get_human_readable_size(size: int) -> str:
    # Find appropriate unit and order
    unit = ''
    order = 1
    for _unit, _order in unitMap.items():
        if size < _order:
            break
        else:
            unit = _unit
            order = _order
    # Calc human readable number
    if unit in unitMap:
        if size < order * 10:
            return f'{size / order:.1f}{unit}'
        else:
            return f'{round(size / order)}{unit}'
    else:
        return str(size)


class DirInfo:
    def __init__(self, path: str, size: int = 0):
        self.__path = path
        self.__size = size
        self.__children = list()

    def __iadd__(self, rhs: DirInfo):
        if rhs not in self.__children:
            rhs.__path = os.path.basename(rhs.__path)
            self.__children.append(rhs)
            self.__size += rhs.__size
        return self

    def __lt__(self, rhs: DirInfo):
        return self.__size < rhs.__size

    def output(self, parent_size, indent_num: int):
        # print(f'size: {self.__size} / {parent_size}')
        indent = indent_base.join(['' for _ in range(indent_num + 1)])
        size_str = get_human_readable_size(self.__size).rjust(4)
        bars = ''
        if parent_size > 0:
            bars = f' [{get_progress(self.__size, parent_size, 10)}] '
        return f'{indent}{disc}{size_str}{bars}{delimiter}{self.__path}'

    def print_all(self, parent_size: int = 0, depth_limit: int = -1,
                  depth: int = 0) -> None:
        if depth_limit < 0 or depth <= depth_limit:
            # print(self.__path)
            output = self.output(parent_size, depth)
            print(output)
            with open(output_file, mode='a', encoding='utf-8') as f:
                f.write(f'{output}\n')
            self.__children.sort(reverse=True)
            for child in self.__children:
                child.print_all(self.__size, depth_limit, depth + 1)


def get_dir_size_tree(path, depth: int = 0) -> TypeGuard(DirInfo):
    info = DirInfo(path)
    with os.scandir(path) as it:
        iterator = tqdm(list(it)) if depth == 0 else \
                   tqdm(list(it), leave=False) if depth == 1 else it
        for entry in iterator:
            if entry.is_file():
                info += DirInfo(entry.path, entry.stat().st_size)
            elif entry.is_dir():
                info += get_dir_size_tree(entry.path, depth + 1)
    return info


if __name__ == '__main__':
    # handle args
    wd = os.getcwd() if len(sys.argv) < 2 else sys.argv[1]
    depth = -1 if len(sys.argv) < 3 else sys.argv[2]
    # calculate directory size recursively
    info = get_dir_size_tree(os.path.abspath(wd))
    os.remove(output_file)
    info.print_all(depth_limit=int(depth))
