from time import sleep
import math
import Adafruit_CharLCD as Lcd
from lcd_menu import Menu, Action
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
    
    box = [lcd._cols, lcd._lines]
    rows = string.split('\n')
    rows_prev = string_prev.split('\n')

    txt = []
    for y, line in enumerate(rows):
        for x, char in enumerate(line):
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


def deeper(menu):
    menu.parent_topmost().items = [menu.selected()]
# LCD
lcd = Lcd.Adafruit_CharLCDPlate()
lcd.blink(True)

# BTNS
btns = []
for key, val in BUTTONS.items():
    btn = Button(key, val, check_fct=lcd.is_pressed, check_args=[val])
    btn.continuous = key == 'UP'
    btns.append(btn)

deeper = Action(trigger=BUTTONS['SELECT'], action=deeper)

app = Menu(name='app', box=LCD_SIZE, loop=True)
welcome = Menu(name='welcome', box=LCD_SIZE,items=['Welcome'], align_h=1, align_v=1, cursor_pos=[4,0])
welcome.actions = [deeper]
settings = Menu(name='settings', box=[8,1], items=['Settings', 'Blop', 'Smash'])
home = Menu(name='home', box=LCD_SIZE, direction=1, items=['Turntable', 'Settings', 'Speed', 'Steps', 'Wait'], cursor_pos=[1,0])
app.items = [welcome]

lcd_fast_message(lcd, str(app))
lcd_cursor(lcd, app.cursor_display(pos=True))
pprint(str(app))
pprint(app.cursor_display())
pprint(app.focus)
pprint(app.selected().name)
#app.focus = welcome


while True:
    old_lcd_fast_message = str(app)
    for b in btns:
        if b.value:

            if b.name == 'RIGHT':
                app.focus.next()
                #app.focus.offset += 1
            elif b.name == 'LEFT':
                app.focus.prev()
                #app.focus.offset -= 1
            elif b.name == 'SELECT':
                #if app.focus == app:
                #    app.items = [home]
                #    app.focus = home
                selected = app.focus.selected()
                app.items = [selected]
                app.focus = selected


            lcd_fast_message(lcd, str(app), string_prev=old_lcd_fast_message)
            pprint(str(app))
            pprint(app.cursor_display())

            lcd_cursor(lcd, app.cursor_display(pos=True))