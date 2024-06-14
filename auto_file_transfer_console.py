# Automatic File Transfer
from utilities import *
# from typing import Iterable
# from glob import glob
import os
import json
import threading
import queue

def main():
    # create a json file if it doesn't exist
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
                        # thread.stop = True
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
