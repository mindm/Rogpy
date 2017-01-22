from sys import platform as _platform
from contextlib import contextmanager
import traceback

try:
    import curses
    from textmodule import justify
except ImportError as e:
    from bearlibterminal import terminal as bear


class Terminal():
    def __init__(self):
        if _platform == "win32":
            self.env = "windows"
        elif _platform == "linux" or _platform == "linux2":
            self.env = "linux"
        else:
            raise Exception("Unrecognized operating system")

    def get_term(self, y, x):
        self.max_y = y
        self.max_x = x
        if self.env == "linux":
            self.mgr = self._l_mgr
            self.getmaxyx = self._l_getmaxyx
            self.newwin = self._l_new_win
            self._l_set_keys()
            self.set_colors = self._l_set_colors
            
        elif self.env == "windows":
            self.mgr = self._w_mgr
            self.newwin = self._w_new_win
            self.getmaxyx = self._w_getmaxyx
            self._w_set_keys()
            self.set_colors = self._w_set_colors
            self.count = 2
        return self

    def get_count(self):
        return self.count
    
    def increment_count(self):
        self.count += 2
        
    def mgr(self):
        pass

    def getmaxyx(self):
        pass

    def init_pair(self, n):
        pass

    def newwin(self, w, h, x, y):
        pass
        
    def set_colors(self):
        pass

    def _l_init_pair(self, n):
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_BLUE)
        curses.init_pair(3, curses.COLOR_RED, curses.COLOR_BLACK)

    def _l_getmaxyx(self):
        return self.mystd.getmaxyx()

    def _w_getmaxyx(self):
        return self.max_y, self.max_x

    def _l_set_keys(self):
        self.KEY_UP = curses.KEY_UP
        self.KEY_DOWN = curses.KEY_DOWN
        self.KEY_RIGHT = curses.KEY_RIGHT
        self.KEY_LEFT = curses.KEY_LEFT
        self.DOT = ord('.')
        self.Q = ord('q')

    def _w_set_keys(self):
        self.KEY_UP = bear.TK_UP
        self.KEY_DOWN = bear.TK_DOWN
        self.KEY_RIGHT = bear.TK_RIGHT
        self.KEY_LEFT = bear.TK_LEFT
        self.Q = bear.TK_Q
        self.DOT = bear.TK_PERIOD
        
    def _l_set_colors(self):
        curses.use_default_colors()
        for i in range(0, curses.COLORS):
            curses.init_pair(i + 1, i, -1)
        self.TK_GREEN = curses.color_pair(3)
        self.TK_RED = curses.color_pair(2)
        self.TK_BLUE = curses.color_pair(5)
        self.TK_GREY = curses.color_pair(9)
        
    def _w_set_colors(self):
        self.TK_GREEN = bear.color_from_name("green")
        self.TK_RED = bear.color_from_name("red")
        self.TK_BLUE = bear.color_from_name("blue")
        self.TK_GREY = bear.color_from_name("grey")
        #self.TK_GREEN = bear.color_from_name("#00FF2F")

    @contextmanager
    def _l_mgr(self):
        try:
            ex = 'Terminated gracefully'
            self.mystd = curses.initscr()
            curses.start_color()
            curses.noecho()
            curses.curs_set(0)
            yield self
        except Exception as e:
            ex = traceback.format_exc()
        finally:
            curses.endwin()
            print(ex)

    @contextmanager
    def _w_mgr(self):
        try:
            ex = ''
            bear.open()
            bear.set("window: title='foo', size={}x{}, cellsize=16x24".format(self.max_x, self.max_y))
            bear.set("0xE000: font-2_anim.png, size=16x24")
            bear.color("white")
            bear.refresh()
            yield self
        except Exception as e:
            ex = traceback.format_exc()
        finally:
            bear.close()
            print(ex)

    def _l_new_win(self, w, h, x, y):
        return Screen(self, self.env, w, h, x, y)

    def _w_new_win(self, w, h, x, y):
        return Screen(self, self.env, w, h, x, y)


class Screen():
    def __init__(self, term, env, w, h, x, y):
        self.T = term
        self.env = env
        self.h = h
        self.w = w
        self.y = y
        self.x = x
        self.count = 2
        if self.env == 'linux':
            self.scr = curses.newwin(h, w, y, x)
            self.add_str = self._l_add_str
            self.keypad = self._l_keypad
            self.refresh = self._l_refresh
            self.getch = self._l_getch
            self.clear_area = self._l_clear_area
        elif self.env == 'windows':
            self.scr = None
            self.layer = self.T.get_count()
            self.T.increment_count()
            bear.layer(self.layer)
            bear.crop(x, y, w, h)
            self.add_str = self._w_add_str
            self.getch = self._w_getch
            self.refresh = self._w_refresh
            self.clear_area = self._w_clear_area

    def add_str(self, x, y, str_, color=None):
        pass

    def move(self, y, x):
        pass

    def keypad(self, n):
        pass

    def refresh(self):
        pass

    def getch(self):
        pass
    
    def clear_area(self, x, y, w, h):
        pass

    def _l_getch(self):
        return self.scr.getch()

    def _w_getch(self):
        return bear.read()

    def _l_refresh(self):
        self.scr.refresh()

    def _w_refresh(self):
        bear.refresh()

    def _l_keypad(self, n):
        self.scr.keypad(n)

    def _l_add_str(self, x, y, str_, color=None):
        try:
            if color is not None:
                self.scr.addstr(y, x, str_, color)
                newy, newx = self.scr.getyx()
                return newy-y +1
                # self.scr.addstr(y, x, str_, curses.color_pair(2))
            else:
                self.scr.addstr(y, x, str_)
                newy, newx = self.scr.getyx()
                with open('log', 'a') as f:
                    f.write("{} {} {}\n".format(newx, newy, str_))
                return newy-y +1
        except curses.error:
            pass

    def _w_add_str(self, x, y, str_, color=None):
        bear.layer(self.layer)
        if color is not None:
            #print("with color {}".format(color))
            prev = bear.state(bear.TK_COLOR)
            bear.color(color)
            leng, height = bear.printf(self.x+x, self.y+y, str_)
            bear.color(prev)
            return height
        else:
            leng,height = bear.printf(self.x+x, self.y+y, str_)
            return height

    def _w_clear_area(self, x, y, w, h):
        bear.layer(self.layer)
        nx = self.x + x
        ny = self.y + y
        bear.clear_area(nx, ny, w, h)
        
    def _l_clear_area(self, x, y, w, h):
        #self.scr.clear()
        pass