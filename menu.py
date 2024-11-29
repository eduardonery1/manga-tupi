import curses
from sys import exit


def __menu(stdscr, menu, msg, result) -> str:
    menu.append("Sair")
    stdscr.clear()
    curses.curs_set(0)  

    screen_height, screen_width = stdscr.getmaxyx()
    display_height = screen_height - 2  # Leave space for padding at the top and bottom

    curses.start_color()

    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Black text on yellow background
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)


    current_option = 0
    start_index = 0  # Index of the first displayed option

    while True:
        stdscr.clear()
        
        stdscr.attron(curses.color_pair(2))
        stdscr.addstr(1, screen_width//5 - len(msg)//2, msg.upper())
        stdscr.attroff(curses.color_pair(2))
    
        end_index = start_index + display_height
        visible_options = menu[start_index:end_index] 
        # Display menu
        for idx, row in enumerate(visible_options):
            if start_index + idx == current_option:
                stdscr.attron(curses.color_pair(1))  # Highlight current option
                stdscr.addstr(idx + 2, 2, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(idx + 2, 2, row)
        key = stdscr.getch()

        # Arrow key navigation
        if key == curses.KEY_UP:
            current_option = (current_option - 1) % len(menu)
            if current_option < start_index:
                start_index = current_option
            elif current_option == len(menu) - 1 and display_height < len(menu):
                    start_index = current_option - display_height + 1

        elif key == curses.KEY_DOWN:
            current_option = (current_option + 1) % len(menu)
            if current_option >= end_index or current_option == 0:
                start_index = current_option
        elif key == curses.KEY_ENTER or key in [10, 13]:
            result.append(menu[current_option])
            break

def menu(opts: list[str], msg="") -> str:
    selected = [] 
    curses.wrapper(lambda stdscr: __menu(stdscr, opts, msg, result=selected))
    if selected[0] == "Sair":
        exit()
    return selected[0]

if __name__ == "__main__":
   main() 

