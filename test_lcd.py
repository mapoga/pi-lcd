from time import sleep
import math
import Adafruit_CharLCD as Lcd
from lcd_menu import PushButton, Box, Action, App, Label, ItemsMenu, ItemsChoice
import lcd_menu


BUTTONS = {'UP': 3,
           'DOWN': 2,
           'LEFT': 4,
           'RIGHT': 1,
           'SELECT': 0}

LCD_SIZE = [16, 2]


class Button(object):

    def __init__(self, name, id, txt='', continuous=False,
                 check_fct=None, check_args=(), check_kwargs={}):
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

def from_to(txt, f, t):
    print(' ')
    print(txt)
    print('From: ')
    pprint(f)
    print('To: ')
    pprint(t)


def below_fct(app, menu, *args, **kwargs):
    from_to('Go Below', menu, menu.below)
    app.menu = menu.below

def above_fct(app, menu, *args, **kwargs):
    from_to('Go Above', menu, menu.above)
    app.menu = menu.above

def next_fct(menu, *args, **kwargs):
    before = str(menu.selected_item())
    menu.next()
    from_to('Go Next', before, menu.selected_item())

def prev_fct(menu, *args, **kwargs):
    before = str(menu.selected_item())
    menu.prev()
    from_to('Go Prev', before, menu.selected_item())

def trigger_item_fct(menu, trigger, *args, **kwargs):
    from_to('trigger_item', menu, menu.selected_item())
    menu.selected_item().check_do(trigger)



# LCD
lcd = Lcd.Adafruit_CharLCDPlate()
lcd.blink(True)

app = App()


###############################################################################
# Buttons
###############################################################################
btns = []
for key, val in BUTTONS.items():
    btn = Button(key, val, check_fct=lcd.is_pressed, check_args=(val, ))
    #btn.continuous = key == 'UP'
    btns.append(btn)

###############################################################################
# Actions
###############################################################################

below = Action(triggers=(BUTTONS['SELECT'], ),
               action=below_fct,
               kwargs={'app': app, },
               )
below_any = Action(triggers=tuple(BUTTONS.values()),
                   action=below_fct,
                   kwargs={'app': app, },
                   )
above = Action(triggers=(BUTTONS['SELECT'], ),
               action=above_fct,
               kwargs={'app': app, },
               )

trigger_items_LR = Action(triggers=(BUTTONS['RIGHT'], BUTTONS['LEFT'], ),
                          action=trigger_item_fct,
                          )

vert_next = Action(triggers=(BUTTONS['DOWN'], ), action=next_fct)
vert_prev = Action(triggers=(BUTTONS['UP'], ), action=prev_fct)
hori_next = Action(triggers=(BUTTONS['RIGHT'], ), action=next_fct)
hori_prev = Action(triggers=(BUTTONS['LEFT'], ), action=prev_fct)

###############################################################################
# Menus
###############################################################################

# Creation
main = Box(size=[16, 2], auto_size=False, align=[0, 0])
welcome = PushButton('Welcome', parent=main, actions=[below_any])

# Home
home = ItemsMenu(parent=main, align=[0, 0], actions=[vert_next, vert_prev, trigger_items_LR], loop=False)
turntable = PushButton('Turntable', parent=home)
settings = PushButton('Settings', parent=home)
blop = PushButton('Blop', parent=home)
sauce = PushButton('sau\nsag', parent=home)
colors = ItemsChoice(parent=main, align=[0,0], orient=0, actions=[hori_next, hori_prev])

# Colors
red = PushButton('   Red ->', parent=colors, above=colors)
green = PushButton('<- Green ->', parent=colors, above=colors)
blue = PushButton('<- Blue ->', parent=colors, above=colors)
yellow = PushButton('<- Yellow ->', parent=colors, above=colors)
orange = PushButton('<- Orange   ', parent=colors, above=colors)

# Linking
welcome.below = home
home.items = [turntable, settings, sauce, colors, blop]
colors.items = [red, green, blue, yellow, orange]
app.menu = welcome


pprint(welcome)
pprint(home)
pprint(app.menu)
lcd_fast_message(lcd, str(welcome), string_prev=' ')

while True:
    for btn in btns:
        if btn.value:
            old_lcd_fast_message = str(app.menu)
            print(btn.name)
            print(app.menu)
            app.menu.check_do(btn.id)
            #app.menu = app.focus

            print('i am printing')
            lcd_fast_message(lcd, str(app.menu), string_prev=old_lcd_fast_message)
            #pprint(str(app))
            #pprint(app.cursor_display())
            #pprint(app.content())
            #pprint(app.selected_pos())
            #pprint(app.cursor_display())

            #lcd_cursor(lcd, app.menu.cursor())
