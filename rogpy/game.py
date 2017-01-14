# -*- coding: utf-8 -*-

from contextlib import contextmanager
import traceback
import sys
import esper
import random
import queue

from maps.mapcreation import dMap

try:
    import curses
    from textmodule import justify

    env = "linux"
except ImportError as e:
    env = "windows"
    from bearlibterminal import terminal as bear


class Terminal():
    def __init__(self, env):
        self.env = env

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
            bear.set("window: title='foo', size={}x{}, cellsize=16x24".format(SCREEN_X, SCREEN_Y))
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
        return Screen(self.env, w, h, x, y)

    def _w_new_win(self, w, h, x, y):
        return Screen(self.env, w, h, x, y)


class Screen():
    def __init__(self, env, w, h, x, y):
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
            self.layer = T.get_count()
            T.increment_count()
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
            d = bear.printf(self.x+x, self.y+y, str_)
            bear.color(prev)
            return d[1] # height
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

##################################
#  Define some Components:
##################################
class Velocity:
    def __init__(self, y=0, x=0):
        self.x = x
        self.y = y


class Renderable:
    def __init__(self, symbol, posx, posy, blocks, collides, color=None):
        self.symbol = symbol
        self.x = posx
        self.y = posy
        self.color = color
        self.blocks = blocks
        self.collides = collides



class Map:
    translate = {0: '.',
                 1: ' ',
                 2: '#',
                 3: '=',
                 4: '+',
                 5: '*'
                }
    def __init__(self, x, y, arr):
        self.y = y
        self.x = x
        self.mapArr = arr
        
        for j in range(self.y):
            for i in range(self.x):
                self.mapArr[j][i] = Map.translate[self.mapArr[j][i]]
                



class Fighter:
    def __init__(self, damage=5):
        self.damage = damage


class TakesDamage:
    def __init__(self, hp=10, armorvalue=1.0, fire_res=1.0, ice_res=1.0,
                 ele_res=1.0, poi_res=1.0):
        self.hp = hp
        self.armorvalue = armorvalue
        self.fire_res = fire_res
        self.ice_res = ice_res
        self.ele_res = ele_res
        self.poi_res = poi_res


class EnemyBehavior:
    pass


################################
#  Define some Processors:
################################
class ControlProcessor(esper.Processor):
    def __init__(self, miny, maxy, minx, maxx):
        super().__init__()
        self.minx = minx
        self.maxx = maxx - 1
        self.miny = miny
        self.maxy = maxy - 1

    def process(self):

        # This will iterate over every Entity that has BOTH of these components:
        for ent, (vel, rend) in self.world.get_components(Velocity, Renderable):
            attacked = False
            tox = rend.x + vel.x
            toy = rend.y + vel.y
            for to_ent, tar in self.world.get_component(Renderable):
                if tar.x == tox and tar.y == toy and tar.collides and world.has_component(ent, Fighter):
                    if ent != to_ent:
                        attacked = True
                        vel.x = 0
                        vel.y = 0
                        hc = self.world.component_for_entity(to_ent, TakesDamage)
                        fc = self.world.component_for_entity(ent, Fighter)
                        hc.hp -= fc.damage
                        if ent is player:
                            mq.put(
                                "Player attacked")
                        if hc.hp <= 0:
                            tar.collides = False
                            tar.symbol = '~'
                            tar.color = T.TK_RED
                            break

            if not attacked:
                if ent is player:
                    mq.put("Player moved")
                # Update the Renderable Component's position by it's Velocity:
                rend.x = tox
                rend.y = toy
                # An example of keeping the sprite inside screen boundaries. Basically,
                # adjust the position back inside screen boundaries if it tries to go outside:
                rend.x = max(self.minx, rend.x)
                rend.y = max(self.miny, rend.y)
                rend.x = min(self.maxx, rend.x)
                rend.y = min(self.maxy, rend.y)
                vel.x = 0
                vel.y = 0


class RenderProcessor(esper.Processor):
    def __init__(self, screen, player):
        super().__init__()
        self.screen = screen

    def process(self):
        # This will iterate over every Entity that has this Component, and render it:
        for ent, rend in self.world.get_component(Renderable):
            if ent is player:
                continue
            x = int(rend.x)
            y = int(rend.y)
            symbol = rend.symbol
            # color = rend.color

            self.screen.add_str(x, y, symbol, color=rend.color)  # , color

        rend = self.world.component_for_entity(player, Renderable)
        self.screen.add_str(rend.x, rend.y, rend.symbol, color=rend.color)


class RenderMapProcessor(esper.Processor):
    def __init__(self, screen):
        super().__init__()
        self.screen = screen

    def process(self):
        for ent, map in self.world.get_component(Map):
            for j in range(map.y):
                for i in range(map.x):
                    self.screen.add_str(i, j, "{}".format(map.mapArr[j][i]))


class MoveEnemyProcessor(esper.Processor):
    def __init__(self):
        super().__init__()

    def process(self):
        for ent, (vel, ebe) in self.world.get_components(Velocity, EnemyBehavior):
            if random.randint(0, 1) == 0:
                vel.x = random.choice([1, -1])
            else:
                vel.y = random.choice([1, -1])


################################
#  Other functions
################################

def can_move(world, obj, vect):
    ty = world.component_for_entity(obj, Renderable).y + vect[0]
    tx = world.component_for_entity(obj, Renderable).x + vect[1]

    can_move_ = True
    for ent, target in world.get_component(Renderable):
        if target.blocks:
            if target.x == tx and target.y == ty:
                can_move_ = False
    return can_move_


def render_messages(window):
    width = MAP_X
    height = SCREEN_Y - MAP_Y
    bbox = "[bbox={}]".format(width)
    window.clear_area(0, 0, width, height)
    while not mq.empty():
        msg = mq.get()
        mg_history.insert(0, msg)
        #words = msg.split(' ')
        #lines = reversed(list(justify(words, MAP_X)))
    cursor = 0
    for line in mg_history:
        if cursor <= height:
            line = bbox + line #works in bearlib only 
            
            cursor += window.add_str(0, cursor, line)
    window.refresh()


def render_messages_old(window):
    while not mq.empty():
        msg = mq.get()
        words = msg.split(' ')
        lines = reversed(list(justify(words, MAP_X)))
        for line in lines:
            window.insdelln(1)
            window.insstr("{}".format(line))
    window.refresh()

################################
#  The main core of the program:
################################

# Globals
MAP_X = 24
MAP_Y = 16
SCREEN_Y = 28
SCREEN_X = 60

# Messaging
mq = queue.Queue()
mg_history = []

T = Terminal(env)
T.get_term(SCREEN_Y, SCREEN_X)
with T.mgr() as stdscreen:
    map1 = dMap()
    map1.makeMap(MAP_X,MAP_Y,110,50,60) 
    print(map1.roomList)
    map1.print_map()
    # stdscreen.get_term()
    y, x = stdscreen.getmaxyx()

    if y < SCREEN_Y or x < SCREEN_X:
        raise Exception("Screen too small, try X={}, Y={}, ({}, {})".format(SCREEN_X,
                                                                            SCREEN_Y, x, y))
    myscreen = T.newwin(MAP_X, MAP_Y, 0, 0)
    msgw = T.newwin(MAP_X,SCREEN_Y - MAP_Y, 0, MAP_Y)
    # msgw = T.newwin(1,1,1,1)
    mq.put("Test")

    # myscreen.idcok(False)
    # myscreen.idlok(False)
    myscreen.keypad(1)
    T.set_colors()
    # curses.start_color()
    # curses.noecho()

    # curses.curs_set(0)

    T.init_pair(1)

    # myscreen.border(0)
    myscreen.move(0, 0)

    world = esper.World()

    control_processor = ControlProcessor(0, MAP_Y, 0, MAP_X)
    world.add_processor(control_processor, priority=102)
    global player
    player = world.create_entity()
    # global player
    render_processor = RenderProcessor(myscreen, player)
    world.add_processor(render_processor, priority=99)

    map_renderer = RenderMapProcessor(myscreen)
    world.add_processor(map_renderer, priority=100)

    enemy_mover = MoveEnemyProcessor()
    world.add_processor(enemy_mover, priority=101)

    # class TakesDamage:
    # def __init__(self, hp=10, armorvalue=1.0, fire_res=1.0, ice_res=1.0,
    # ele_res=1.0, poi_res=1.0):
    map = world.create_entity()
    world.add_component(map, Map(map1.size_x, map1.size_y, map1.mapArr))
    
    p_pos_x, p_pos_y = map1.get_entry()
    # p_pos_x, p_pos_y = 0,0

    dam_kwargs = {'hp': 20, 'armorvalue': 1.2, 'fire_res': 1.1, 'ice_res': 1.1,
                  'ele_res': 1.1, 'poi_res': 1.1}
    world.add_component(player, TakesDamage(**dam_kwargs))
    world.add_component(player, Velocity(0, 0))
    world.add_component(player, Fighter())
    world.add_component(player, Renderable('@', p_pos_x, p_pos_y, False, True, color=T.TK_GREY))



    # Create an enemy
    dam_kwargs = {'hp': 15, 'armorvalue': 1.0, 'fire_res': 1.0, 'ice_res': 1.0,
                  'ele_res': 1.0, 'poi_res': 1.0}
    enemy0 = world.create_entity()
    world.add_component(enemy0, TakesDamage(**dam_kwargs))
    world.add_component(enemy0, Velocity(0, 0))
    world.add_component(enemy0, Renderable('g', 1, 1, False, True, color=T.TK_GREEN))
    # world.add_component(enemy0, EnemyBehavior())

    # Create a tree
    tree = world.create_entity()
    world.add_component(tree, Renderable('^', 2, 3, True, False))

    world.process()
    myscreen.refresh()
    while True:
        myscreen.refresh()
        c = myscreen.getch()

        if c == T.KEY_DOWN:
            if world.has_component(player, Velocity):
                if can_move(world, player, [1, 0]):
                    world.component_for_entity(player, Velocity).y = 1
                else:
                    continue
        if c == T.KEY_UP:
            if world.has_component(player, Velocity):
                if can_move(world, player, [-1, 0]):
                    world.component_for_entity(player, Velocity).y = -1
                else:
                    continue
        if c == T.KEY_RIGHT:
            if world.has_component(player, Velocity):
                if can_move(world, player, [0, 1]):
                    world.component_for_entity(player, Velocity).x = 1
                else:
                    continue
        if c == T.KEY_LEFT:
            if world.has_component(player, Velocity):
                if can_move(world, player, [0, -1]):
                    world.component_for_entity(player, Velocity).x = -1
                else:
                    continue
        if c == T.DOT:
            pass

        world.process()

        render_messages(msgw)
        # msgw.touchwin()
        # msgw.refresh()

        # if c == curses.KEY_DOWN:

        if c == T.Q:
            break
            # else:
            # break

##################
# TODO-list
##################

# -Main menu, other menus
# -Hostile enemy behavior
# -Map with rooms
# -Items, inventory
# -Vendors
# -Fov

