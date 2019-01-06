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


def below_fct(menu, app):
    from_to('Go Below', menu, menu.below)
    app.menu = menu.below

def above_fct(menu, app):
    from_to('Go Above', menu, menu.above)
    app.menu = menu.above

def next_fct(menu):
    before = str(menu.selected_item())
    menu.next()
    from_to('Go Next', before, menu.selected_item())


def prev_fct(menu):
    before = str(menu.selected_item())
    menu.prev()
    from_to('Go Prev', before, menu.selected_item())

def trigger_selected_item_fct(menu, *triggers):
    from_to('trigger_selected_item', menu, menu.selected_item())
    print('triggers: ', triggers)
    print(menu.selected_item().actions)
    for i in menu.selected_item().actions:
        print(i.triggers)
    print(menu.selected_item().check(triggers))
    menu.selected_item().check_do(triggers)



# LCD
lcd = Lcd.Adafruit_CharLCDPlate()
lcd.blink(True)

app = App()


###############################################################################
# Buttons
###############################################################################
btns = []
for key, val in BUTTONS.items():
    btn = Button(key, val, check_fct=lcd.is_pressed, check_args=[val])
    #btn.continuous = key == 'UP'
    btns.append(btn)

###############################################################################
# Actions
###############################################################################

#focus_deeper = Action(trigger=BUTTONS['SELECT'], action=focus_deeper_fct)
#focus_back = Action(trigger=BUTTONS['SELECT'], action=focus_back_fct)

below = Action(triggers=(BUTTONS['SELECT'], ), action=below_fct, args=(app, ))
below_any = Action(triggers=tuple(BUTTONS.values()), action=below_fct, args=(app, ))
above = Action(triggers=(BUTTONS['SELECT'], ), action=above_fct, args=(app, ))
#trigger_selected_item = Action(triggers=(BUTTONS['RIGHT'], BUTTONS['LEFT'], ),
#                               action=trigger_selected_item_fct,
#                               args=(BUTTONS['RIGHT'], BUTTONS['LEFT'], )
#                               )
trigger_selected_item = Action(triggers=(BUTTONS['RIGHT'], BUTTONS['LEFT'], ),
                               action=trigger_selected_item_fct,
                               )

down = Action(triggers=(BUTTONS['DOWN'], ), action=next_fct)
up = Action(triggers=(BUTTONS['UP'], ), action=prev_fct)
right = Action(triggers=(BUTTONS['RIGHT'], ), action=next_fct)
left = Action(triggers=(BUTTONS['LEFT'], ), action=prev_fct)

###############################################################################
# Menus
###############################################################################

# Creation
main = Box(size=[16, 2], auto_size=False, align=[0, 0])
welcome = PushButton('Welcome', parent=main, actions=[below_any])

home = ItemsMenu(parent=main, align=[0, 0], actions=[up, down, trigger_selected_item])
turntable = PushButton('Turntable', parent=home)
settings = PushButton('Settings', parent=home)
blop = PushButton('Blop', parent=home)
sauce = PushButton('sauce', parent=home)
colors = ItemsMenu(parent=main, align=[0,0], orient=0, actions=[left, right])

red = PushButton('Red', parent=colors, above=colors)
green = PushButton('Green', parent=colors, above=colors)
blue = PushButton('Blue', parent=colors, above=colors)
yellow = PushButton('Yellow', parent=colors, above=colors)
orange = PushButton('Orange', parent=colors, above=colors)

# Linking
welcome.below = home
home.items = [turntable, settings, blop, sauce, colors]
colors.items = [red, green, blue, yellow, orange]
app.menu = welcome


pprint(welcome)
pprint(home)
pprint(app.menu)
lcd_fast_message(lcd, str(welcome), string_prev=' ')

while True:
    old_lcd_fast_message = str(app.menu)
    for btn in btns:
        if btn.value:
            print(btn.name)
            print(app.menu)
            app.menu.check_do(btn.id)
            #app.menu = app.focus


            lcd_fast_message(lcd, str(app.menu), string_prev=old_lcd_fast_message)
            #pprint(str(app))
            #pprint(app.cursor_display())
            #pprint(app.content())
            #pprint(app.selected_pos())
            #pprint(app.cursor_display())

            #lcd_cursor(lcd, app.menu.cursor())
