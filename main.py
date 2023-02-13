# Automatic File Transfer
from typing import Iterable
from glob import glob
import os
import json
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

def do_task(task: dict, event: threading.Event, q: queue.Queue) -> None:
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
                if getattr(thread, 'stop', False):
                    break
                try:
                    shutil.move(path, task['destiny'])
                    move_files += 1
                except:
                    ignored_paths.append(path)
                    errors += 1
            q.put((move_files, errors))
            event.wait(0.1)

def stats(threads: list[threading.Thread], queues: list[queue.Queue], q_backup: queue.Queue):
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

def main():
    # create a json file if it doesn't exits
    settings_path = os.path.join(os.path.dirname(__file__), 'app_settings.json')
    if not os.path.exists(settings_path):
        with open(settings_path, 'w') as file:
            file.write('[]')
    # read the json file
    with open(settings_path, 'r') as file:
        tasks: list[dict] = json.load(file)
    # main program
    os.system('cls')
    while True:
        print(' Automatic File Transfer '.center(os.get_terminal_size().columns, '-'))
        print('Select an option:')
        options = ('create task', 'delete task', 'edit task', 'start program', 'exit program')
        for k, v in enumerate(options, 1):
            print(f'[ {k} ] - {v}')
        option = int(input_ask('Option: ', answers=list(map(str, range(1, len(options) + 1))))) # options
        match option:
            case 1:  # create task
                task = {
                    'task_name': input('Task name: ').strip(),
                    'source': input_path('Source: ', 'dir').strip(),
                    'destiny': input_path('Destiny: ', 'dir').strip(),
                    'extensions': input('File extensions: (sep=";") ').strip().split(';'),
                    'ignored_files': input('Which files should I ignore? (sep=";") ').strip().split(';'),
                }
                tasks.append(task)
                with open(settings_path, 'w') as file:
                    file.write(json.dumps(tasks, indent=4))
            case 2:  # delete task
                if len(tasks) >= 1:
                    s = int(input_ask(f'Select task to delete: [1-{len(tasks)}] ',
                                      answers=list(map(str, range(1, len(tasks) + 1))),
                                      print_error='Error! Task not found!')) - 1
                    print(f'Deleting {tasks[s]["task_name"]}...')
                    del tasks[s]
                    with open(settings_path, 'w') as file:
                        file.write(json.dumps(tasks, indent=4))
                    print('Completed!')
                else:
                    print('\033[31mError! There are no tasks to remove.\033[m')
            case 3:  # edit task
                if len(tasks) >= 1:
                    s = int(input_ask(f'Select task to edit: [1-{len(tasks)}] ',
                                      answers=list(map(str, range(1, len(tasks) + 1))),
                                      print_error='Error! Task not found!')) - 1
                    print(f'Editing {tasks[s]["task_name"]}...')
                    print('Leave it blank if you don\'t want to change it.')
                    changed = {
                        'task_name': input('Task name: ').strip(),
                        'source': input_path('Source: ', 'dir', (True, '')).strip(),
                        'destiny': input_path('Destiny: ', 'dir', (True, '')).strip(),
                        'extensions': input('File extensions: (sep=";") ').strip().split(';'),
                        'ignored_files': input('Which files should I ignore? (sep=";") ').strip().split(';'),
                    }
                    for k in tasks[s].keys():
                        if changed[k] != '' and changed[k] != ['']:
                            tasks[s][k] = changed[k]
                    with open(settings_path, 'w') as file:
                        file.write(json.dumps(tasks, indent=4))
                else:
                    print('\033[31mError! There are no tasks to edit.\033[m')
            case 4:  # start program
                if len(tasks) >= 1:
                    print('Type "all" to run all tasks.')
                    selected = input_ask2(f'Select tasks to run: (sep=";") [1-{len(tasks)}] ', sep=';',
                                          answers=list(map(str, range(1, len(tasks) + 1))) + ['all'])
                    threads: list[threading.Thread] = []
                    qs: list[queue.Queue] = []
                    event = threading.Event()
                    if 'all' in selected:
                        for k, task in enumerate(tasks):
                            qs.append(queue.Queue())
                            threads.append(threading.Thread(target=do_task,
                                                            args=(task, event, qs[k]),
                                                            daemon=True))
                    else:
                        for k, s in enumerate(selected):
                            qs.append(queue.Queue())
                            threads.append(threading.Thread(target=do_task,
                                                            args=(tasks[int(s) - 1], event, qs[k]),
                                                            daemon=True))
                    for thread in threads:
                        thread.start()
                    print('\n\n')
                    q_backup = queue.Queue()
                    status_thread = threading.Thread(target=stats,
                                                     args=(threads, qs, q_backup),
                                                     daemon=True)
                    status_thread.start()
                    input('')
                    status_thread.do_run = False
                    status_thread.join()
                    st = q_backup.get()
                    print('\n', '\033[A' * 5, f'Tasks running: {st[0]}', ' ' * 40,
                          f'\nMoved files: {st[1]}', ' ' * 40,
                          f'\nErrors: {st[2]}', ' ' * 40,
                          ''.join(['\n' + ' ' * 50] * 2), sep='', end='')
                    print('\n\033[A\033[AStopping...', sep='', end=' ', flush=True)
                    for thread in threads:
                        thread.stop = True
                        thread.do_run = False
                        thread.join()
                    print('Done!')
                else:
                    print('\033[31mError! There are no tasks to run.\033[m')
            case 5:  # exit program
                print('Bye!')
                break

if __name__ == '__main__':
    main()
