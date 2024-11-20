import curses


def __menu(stdscr, menu, result) -> str:
    menu.append("EXIT")
    # Clear the screen
    stdscr.clear()
    curses.curs_set(0)  # Hide the cursor
    
    # Initialize colors
    curses.start_color()
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_YELLOW)  # Black text on yellow background

    # Define menu 
    current_option = 0
    screen_height, screen_width = stdscr.getmaxyx()
    display_height = screen_height - 2  # Leave space for padding at the top and bottom
    start_index = 0  # Index of the first displayed option

    while True:
        stdscr.clear()
        end_index = start_index + display_height
        visible_options = menu[start_index:end_index] 
        # Display menu
        for idx, row in enumerate(visible_options):
            if start_index + idx == current_option:
                stdscr.attron(curses.color_pair(1))  # Highlight current option
                stdscr.addstr(idx + 1, 2, row)
                stdscr.attroff(curses.color_pair(1))
            else:
                stdscr.addstr(idx + 1, 2, row)

        # Get user input
        key = stdscr.getch()

        # Arrow key navigation
        if key == curses.KEY_UP:
            current_option = (current_option - 1) % len(menu)
            if current_option < start_index or current_option == len(menu) - 1:
                start_index = current_option
        elif key == curses.KEY_DOWN:
            current_option = (current_option + 1) % len(menu)
            if current_option >= end_index or current_option == 0:
                start_index = current_option
        elif key == curses.KEY_ENTER or key in [10, 13]:
            #stdscr.addstr(len(menu) + 3, 2, f"You selected '{menu[current_option]}'")
            #stdscr.refresh()
            #stdscr.getch()  # Wait for another key press
            result.append(menu[current_option])
            break

def menu(opts: list[str]) -> str:
    selected = [] 
    curses.wrapper(lambda stdscr: __menu(stdscr, opts, result=selected))
    return selected[0]

if __name__ == "__main__":
   main() 

