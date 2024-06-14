from typing import Iterable
from glob import glob
import os
import shutil
import threading
import queue

def input_ask(prompt: str = '', answers: str | Iterable[str] = 'sn', print_error: str = 'Invalid input! Try again!') -> str:
    while True:
        ans = input(prompt)
        if ans in answers and ans != '':
            return ans
        print(f'\033[31m{print_error}\033[m')

def input_ask2(prompt: str = '', sep: str = ' ', answers: Iterable[str] = ['s', 'n'], print_error: str = 'Try again!') -> list[str]:
    while True:
        errs = []
        anss = input(prompt).strip().split(sep)
        for ans in anss:
            if ans not in answers:
                errs.append(ans)
        if len(errs) >= 1:
            if len(errs) == 1:
                print(f'\033[31m{errs[0]} is not valid choice. {print_error}\033[m')
            else:
                print(f'\033[31m{", ".join(errs[:-1])} and {errs[-1]} are not valid choices. {print_error}\033[m')
            del errs
        else:
            return anss

def input_path(prompt: os.PathLike = '', path_type: str = 'any', exception: tuple[bool, str] = (False, '')) -> str:
    while True:
        if path_type in ('any', 'file', 'dir'):
            err = 'Path' if path_type == 'any' else 'File' if path_type == 'file' else 'Directory'
            ans = input(prompt)
            if exception[0] and ans == exception[1]:
                return ans
            else:
                if path_type == 'any' and os.path.exists(ans):
                    return os.path.abspath(ans)
                elif path_type == 'file' and os.path.isfile(ans):
                    return os.path.abspath(ans)
                elif path_type == 'dir' and os.path.isdir(ans):
                    return os.path.abspath(ans)
                else:
                    print(f'\033[31m{err} does not exist. Try again!\033[m')
        else:
            raise Exception(f'{path_type} is not valid path type.')

def do_task(task: dict[str, str | list[str]], event: threading.Event, q: queue.Queue) -> None:
    thread = threading.current_thread()
    move_files, errors = 0, 0
    if task['ignored_files'] == ['']:
        ignored_paths = []
    else:
        ignored_paths = list(map(lambda ig: os.path.join(task['source'], ig), task['ignored_files']))
    while getattr(thread, 'do_run', True):
        paths = glob(task['source'] + r'\*')
        for path in paths:
            ext = os.path.splitext(path)[-1].lower()
            if ext[1:] in task['extensions'] and path not in ignored_paths:
                if not getattr(thread, 'do_run', True):
                    break
                try:
                    shutil.move(path, task['destiny'])
                    move_files += 1
                except Exception as err:
                    
                    ignored_paths.append(path)
                    errors += 1
            q.put((move_files, errors))
            # event.wait(0.1)

def stats(threads: list[threading.Thread], queues: list[queue.Queue], q_backup: queue.Queue) -> None:
    thread = threading.current_thread()
    value_backup = [(0, 0)]
    while getattr(thread, 'do_run', True):
        try:
            get_value = [q.get(False) for q in queues]
        except queue.Empty:
            get_value = value_backup
        value_backup = get_value
        print('\n', '\033[A' * 4, f'Tasks running: {len(threads)}', ' ' * 40,
             f'\nMoved files: {sum([value[0] for value in get_value])}', ' ' * 40,
             f'\nErrors: {sum([value[1] for value in get_value])}', ' ' * 40,
             '\nPress ENTER to stop operation...', ' ' * 40, sep='', end='')
    q_backup.put((len(threads), sum([value[0] for value in get_value]), sum([value[1] for value in get_value])), False)