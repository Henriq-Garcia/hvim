import curses
from subprocess import Popen, PIPE
from os import system
from os.path import join, isdir, abspath

# Execute command and return output
def execute_cmd(cmd, cwd='.'):
    process = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True, cwd=cwd)
    output, error = process.communicate()
    return output.decode('utf-8').strip()

# List files and folders in the target directory
def ls(target_dir='.'):
    files, folders = {}, {}
    results = execute_cmd(f'ls -a', cwd=target_dir).split('\n')
    for result in results:
        path = abspath(join(target_dir, result))
        if result == '.':
            continue
        if isdir(path):
            folders[result] = path
        else:
            files[result] = path
    return files, folders, abspath(target_dir)

# Concatenate files and folders
def concat_subs(files, folders):
    folders = list(folders.keys())
    files = list(files.keys())
    files.sort()
    folders.sort()
    return folders + files

# Display directory content
def show_directory(stdscr, father, dir_files, selected_index):
    stdscr.clear()
    height, width = stdscr.getmaxyx()
    dir_display = father if len(father) < width else father[:width-3] + '...'
    stdscr.addstr(0, 0, f'Directory: {dir_display}', curses.A_BOLD)
    
    for idx, item in enumerate(dir_files):
        if idx + 1 >= height:
            break
        item_display = item if len(item) < width else item[:width-3] + '...'
        if idx == selected_index:
            stdscr.addstr(idx + 1, 0, f'-> {item_display}', curses.color_pair(1))
        else:
            stdscr.addstr(idx + 1, 0, f'   {item_display}', curses.color_pair(2))
    
    if len(dir_files) + 2 < height:
        stdscr.addstr(len(dir_files) + 2, 0, "[Press 'ctrl' + 't' to enter command mode]", curses.A_DIM)

# Command mode with history
def command_mode(stdscr, current_dir, history):
    while True:
        curses.echo()
        stdscr.clear()
        stdscr.addstr(0, 0, "Enter your command (press ENTER to cancel): ")
        stdscr.refresh()
        cmd = stdscr.getstr(1, 0).decode('utf-8')
        if len(cmd) == 0:
            break
        else:
            output = execute_cmd(cmd, cwd=current_dir)
            stdscr.addstr(1, 0, output)
    curses.noecho()

    curses.noecho()

def main(stdscr):
    curses.curs_set(0)
    curses.start_color()
    curses.mousemask(1)
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    selected_index = 0
    current_dir = '.'
    command_history = []

    while True:
        files, folders, current_dir = ls(current_dir)
        concat_dir_files = concat_subs(files, folders)
        show_directory(stdscr, current_dir, concat_dir_files, selected_index)
        key = stdscr.getch()
        
        if key == 10:
            selected_item = concat_dir_files[selected_index]
            selected_path = join(current_dir, selected_item)
            if isdir(selected_path):
                current_dir = selected_path
                selected_index = 0
            else:
                curses.endwin()
                system(f'vim {selected_path}')
                curses.initscr()
        elif key == curses.KEY_UP:
            selected_index = (selected_index - 1) % len(concat_dir_files)
        elif key == curses.KEY_DOWN:
            selected_index = (selected_index + 1) % len(concat_dir_files)
        elif key == 20:  # Ctrl + t to enter command mode
            command_mode(stdscr, current_dir, command_history)
        elif key == 27:  # ESC key to exit
            break

if __name__ == "__main__":
    curses.wrapper(main)
