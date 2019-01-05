from time import sleep
import math
import Adafruit_CharLCD as Lcd
from lcd_menu import Menu, Action, App
import lcd_menu


BUTTONS = {'UP': 3,
           'DOWN': 2,
           'LEFT': 4,
           'RIGHT': 1,
           'SELECT': 0}

LCD_SIZE = [16, 2]


class Button(object):

    def __init__(self, name, id, txt='', continuous=False,
                 check_fct=None, check_args=[], check_kwargs={}):
        self.name = name
        self.id = id
        self.txt = txt or name
        self.continuous = continuous
        self.last_value = False
        # Check
        self.check_fct = check_fct
        self.check_args = check_args
        self.check_kwargs = check_kwargs

    def __repr__(self):
        return '<Button> {0}'.format(self.name)

    @property
    def value(self):
        if self.check_fct:
            old_last = self.last_value
            # custom check
            value = self.check_fct(*self.check_args, **self.check_kwargs)
            self.last_value = value
            # true or
            if value:
                return not old_last or self.continuous
        self.last_value = False
        return


def lcd_fast_message(lcd, string, string_prev=''):
    # only update what has changed
    # much faster for small changes
    
    #box = [lcd._cols, lcd._lines]
    rows = string.split('\n')
    rows_prev = string_prev.split('\n')

    for y in range(lcd._lines):
        for x in range(lcd._cols):
            try:
                char = rows[y][x]
            except:
                char = ' '
            try:
                char_prev = rows_prev[y][x]
            except:
                char_prev = ' '
            if char != char_prev:
                lcd.set_cursor(x, y)
                lcd.write8(ord(char), True)

def lcd_cursor(lcd, pos):
    if pos:
        lcd.blink(True)
        lcd.set_cursor(*pos)
    else:
        lcd.blink(False)

def pprint(p, sep='-'):
    print(sep*lcd_menu.string_size(str(p))[0])
    print(p)
    print(sep*lcd_menu.string_size(str(p))[0])


def focus_deeper_fct(menu):
    dest = str(menu.selected())
    try:
        dest = menu.selected().name
    except:
        pass
    print('focus deeper: {} -> {}'.format(menu.name,dest))
    if isinstance(menu.selected(), Menu):
        menu.parent_topmost().focus = menu.selected()


def focus_back_fct(menu):
    global app
    print('focus back: {} -> {}'.format(menu.name, menu.parent.name))
    app.focus = menu.parent
    app.menu = app.focus
    print('2'*20)


def next_fct(menu):
    print('NEXT')
    try:
        menu.focus.next()
    except:
        pass

def prev_fct(menu):
    try:
        menu.focus.prev()
    except:
        pass


# LCD
lcd = Lcd.Adafruit_CharLCDPlate()
lcd.blink(True)

# BTNS
btns = []
for key, val in BUTTONS.items():
    btn = Button(key, val, check_fct=lcd.is_pressed, check_args=[val])
    #btn.continuous = key == 'UP'
    btns.append(btn)
app = None
focus_deeper = Action(trigger=BUTTONS['SELECT'], action=focus_deeper_fct)
focus_back = Action(trigger=BUTTONS['SELECT'], action=focus_back_fct)
down = Action(trigger=BUTTONS['DOWN'], action=next_fct)
up = Action(trigger=BUTTONS['UP'], action=prev_fct)
right = Action(trigger=BUTTONS['RIGHT'], action=next_fct)
left = Action(trigger=BUTTONS['LEFT'], action=prev_fct)
app = App()

#app = Menu(name='app', box=LCD_SIZE, loop=True)
#app.actions = [deeper]
welcome = Menu(name='welcome', box=LCD_SIZE,items=['Welcome'], align_h=1, align_v=1, cursor_pos=[4,0])
welcome.actions = [focus_deeper]
settings = Menu(name='settings', box=[8,1], items=['Yeah!', 'Blop', 'Smash'], item_div='--')
settings.actions = [focus_back, right, left]
home = Menu(name='home', box=LCD_SIZE, direction=1,
    items=['Turntable', settings, 'Speed', 'Steps', 'Wait'], cursor_pos=[1,0])
home.actions = [focus_deeper, down, up]
#app.items = [welcome]
app.menu = home


blop = Menu(name='blop', items=['Blop'], auto_box=True)
pprint(blop)
blop.set_box_to_content()
pprint(blop)

lcd_fast_message(lcd, str(app))
lcd_cursor(lcd, app.cursor())
pprint(str(app))
#pprint(app.cursor_display())
pprint(app.focus)
#pprint(app.selected().name)
#app.focus = welcome


while True:
    old_lcd_fast_message = str(app)
    for b in btns:
        if b.value:
            print(app.focus.name)
            print('1'*20)
            app.focus.check_actions(b.id)
            print('3'*20)
            #app.menu = app.focus
            '''
            if b.name == 'RIGHT':
                app.focus.next()
                #app.focus.offset += 1
            elif b.name == 'LEFT':
                app.focus.prev()
                #app.focus.offset -= 1
            elif b.name == 'SELECT':
                pass
                #if app.focus == app:
                #    app.items = [home]
                #    app.focus = home
                #selected = app.focus.selected()
                #app.items = [selected]
                #app.focus = selected
            '''


            lcd_fast_message(lcd, str(app), string_prev=old_lcd_fast_message)
            #pprint(str(app))
            #pprint(app.cursor_display())
            #pprint(app.content())
            #pprint(app.selected_pos())
            #pprint(app.cursor_display())

            lcd_cursor(lcd, app.cursor())