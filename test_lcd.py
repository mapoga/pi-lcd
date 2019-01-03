from time import sleep
import math
import Adafruit_CharLCD as Lcd
import lcd_menu


BUTTONS = {'UP': 3,
           'DOWN': 2,
           'LEFT': 4,
           'RIGHT': 1,
           'SELECT': 0}

LCD_W = 16
LCD_H = 2


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


# LCD
lcd = Lcd.Adafruit_CharLCDPlate()

# BTNS
btns = []
for key, val in BUTTONS.items():
    btn = Button(key, val, check_fct=lcd.is_pressed, check_args=[val])
    btn.continuous = key == 'UP'
    btns.append(btn)

menu = lcd_menu.Menu_h(name='menu',box_w=LCD_W, box_h=LCD_H,
                       loop=False, focus_end=False)
welcome = lcd_menu.Menu_h(name='welcome', box_w=LCD_W,
                          box_h=LCD_H, focus_end=False)
welcome.items = [lcd_menu.Line(txt='WELCOME', box_w=LCD_W,
                          align=lcd_menu.ALIGN_CENTER), ]
print(welcome.display_box())
lcd.message(welcome.display_box())
'''
while True:
    # Test Buttons
    for b in btns:
        if b.value:
            print(b)
'''



'''

#lcd.message('blop')
#time.sleep(1)
#lcd.clear()
#lcd.message(' woortt --')

current_msg = ''

def message(msg):
    global current_msg
    # only update what has changed
    # much faster for small changes
    
    old = str((' '*17) + '\n' + (' '*17))
    if current_msg:
        old = current_msg

    msg_split = msg.split('\n')
    old_split = old.split('\n')
    txt = ['', '']
    for line, row in enumerate(msg_split):
        for col in range(16):
            old_char = old_split[line][col]
            char = old_char
            try:
                if row[col] is not old_char:
                    char = row[col]
                    lcd.set_cursor(col, line)
                    lcd.write8(ord(char), True)
            except:
                if ' ' is not old_char:
                    char = ' '
                    lcd.set_cursor(col, line)
                    lcd.write8(ord(char), True)
            txt[line] += char

    current_msg = '\n'.join(txt)
    print(msg)
    cur = m_main.cursor_pos_box()
    lcd.set_cursor(cur[0], cur[1])


def on_pressed(button):
    m_main.focused_item().on_pressed(button)
    message(m_main.display_box())
    print(m_main.display())
    print(m_main.cursor_display_box())
    print('    ')


def BUTTONS():
    pressed = None

    def is_pressed(button):
        nonlocal pressed
        if lcd.is_pressed(button):
            if button is not pressed:
                pressed = button
                return True

    def not_pressed():
        for button in (Lcd.SELECT, Lcd.RIGHT, Lcd.DOWN, Lcd.UP, Lcd.LEFT):
            if lcd.is_pressed(button):
                return False
        return True

    while True:
        if not_pressed():
            pressed = None
        
        for button in (Lcd.SELECT, Lcd.RIGHT, Lcd.DOWN, Lcd.UP, Lcd.LEFT):
            if is_pressed(button):
                on_pressed(button)
                pass



#lcd.color = [100, 100, 100]
#lcd.cursor = True
#lcd.blink = True
#lcd.clear()
#print('active count: ', threading.active_count())
#thread_menu = threading.Thread(target=BUTTONS)
#thread_menu.start()
#print('active count: ', threading.active_count())
#thread_display = threading.Thread(target=diss)


lcd_brightness = 50
lcd_sleep = 5


class ButtonGroup(object):
    def __init__(self,lcd , btns=[]):
        self.lcd = lcd
        self.currently_pressed = False
        self.BUTTONS = btns
        self.continuous = True

    def on_pressed(self, btn):
        print('pressed: ', btn)

    def is_pressed(self, btn):
        if self.lcd.is_pressed(btn):
            if (btn is not self.currently_pressed) or (not self.single_press):
                self.currently_pressed = btn
                return True

    def not_pressed(self):
        for btn in self.BUTTONS:
            if lcd.is_pressed(button):
                return False
        return True



###############
#### MENU #####
###############

m_main = lcd_menu.Menu_h(box_w=16, box_h=2)
m_main.name = 'Main Menu'
m_main.focus_end = False
m_main.loop = True

m_home = lcd_menu.Menu_h(box_w=16, box_h=2)

def brightness(val):
    lcd.color = [val, val, val]

def settings(self):
    pass

def home(self):
    pass

def turntable(self):
    pass

def settings(self):
    print('settings')
    global m_main
    def bright_up(self):
        global lcd_brightness
        lcd_brightness += 10
        lcd_brightness = min(100, lcd_brightness)
        self.items[1].txt = str(lcd_brightness).rjust(3, ' ')
        brightness(lcd_brightness)
        message(m_main.display_box())

    def bright_down(self):
        global lcd_brightness
        lcd_brightness -= 10
        lcd_brightness = max(0, lcd_brightness)
        self.items[1].txt = str(lcd_brightness).rjust(3, ' ')
        brightness(lcd_brightness)
        message(m_main.display_box())

    def sleep_up(self):
        global lcd_sleep
        lcd_sleep += 1
        lcd_sleep = min(99, lcd_sleep)
        self.items[1].txt = str(lcd_sleep).rjust(2, ' ')
        message(m_main.display_box())

    def sleep_down(self):
        global lcd_sleep
        lcd_sleep -= 1
        lcd_sleep = max(0, lcd_sleep)
        self.items[1].txt = str(lcd_sleep).rjust(2, ' ')
        message(m_main.display_box())

    def do_any(self):
        print('ANY')
        message(m_main.display_box())


    m_settings = lcd_menu.Menu_v()
    m_settings.name = 'Settings Menu'
    m_settings.focus_end = False

    m_back = lcd_menu.Menu_h(box_w=16, box_h=1)
    l_back_name = lcd_menu.Line(txt='< Back', box_w=16)
    m_back.items = [l_back_name]
    m_back.do_select = home

    m_bright = lcd_menu.Menu_h(box_w=16, box_h=1)
    l_bright_name = lcd_menu.Line(txt='Bright:'.ljust(11), box_w=11)
    l_bright_value = lcd_menu.Line(txt=str(lcd_brightness).rjust(3, ' '), box_w=3)
    m_bright.items = [l_bright_name, l_bright_value]
    m_bright.do_more = bright_up
    m_bright.do_less = bright_down

    m_sleep = lcd_menu.Menu_h(box_w=16, box_h=1)
    l_sleep_name = lcd_menu.Line(txt='Sleep:'.ljust(11), box_w=12)
    l_sleep_value = lcd_menu.Line(txt=str(lcd_sleep).rjust(2, ' '), box_w=2)
    m_sleep.items = [l_sleep_name, l_sleep_value]
    m_sleep.do_more = sleep_up
    m_sleep.do_less = sleep_down

    #m_bright.do_any = do_any
    #m_sleep.do_any = do_any

    m_settings.items = [m_back, m_bright, m_sleep]
    m_settings.is_focused = True

    m_main.items = [m_settings]
    #m_main.do_any = do_any
    message(m_main.display_box())
    print(m_main.cursor_display_box())

def turntable(self):
    print('turntable')

def home(self):
    global m_main
    global m_home
    print('   ')
    print('homeeeeeeeeeeeeeeeeeeeee')
    m_home.name = 'Home Menu'
    m_home.focus_end = False
    #m_home.loop = True

    m_ttb = lcd_menu.Menu_v(box_w=5, box_h=2)
    m_ttb.name = 'item turntable 0'
    m_ttb.items = [lcd_menu.Line('TURN', box_w=5), lcd_menu.Line('TABLE', box_w=5)]
    m_ttb.do_select = turntable
    #m_ttb.cursor_pos = [4, 0]

    m_settings = lcd_menu.Menu_v(box_w=4, box_h=2)
    m_settings.name = 'item settings 1'
    m_settings.items = [lcd_menu.Line('SETT', box_w=4), lcd_menu.Line('INGS', box_w=4)]
    m_settings.do_select = settings

    m_ttb2 = lcd_menu.Menu_v(box_w=5, box_h=2)
    m_ttb2.name = 'item turntable 2'
    m_ttb2.items = [lcd_menu.Line('TURN', box_w=5), lcd_menu.Line('TABLE', box_w=5)]
    m_ttb2.do_select = turntable

    m_settings2 = lcd_menu.Menu_v(box_w=4, box_h=2)
    m_settings2.name = 'item settings 3'
    m_settings2.items = [lcd_menu.Line('SETT', box_w=4), lcd_menu.Line('INGS', box_w=4)]
    m_settings2.do_select = settings

    m_home.items = [m_ttb, m_settings, m_ttb2, m_settings2]
    m_home.do_select = turntable
    m_home.is_focused = True

    m_main.items = [m_home]
    message(m_main.display_box())
    print(m_main.cursor_display_box())



m_welcome = lcd_menu.Menu_v(box_w=16, box_h=1)
m_welcome.name = 'Welcome Menu'
m_welcome.focus_end = True
m_wel_top = lcd_menu.Line('Welcome', box_w=16)
m_wel_top.align = lcd_menu.ALIGN_CENTER
m_welcome.cursor_pos = [11, 0]
m_wel_bottom = lcd_menu.Line('TurnTable', box_w=16)
m_wel_bottom.align = lcd_menu.ALIGN_CENTER
m_welcome.items = [m_wel_top]
m_welcome.do_any = home



m_main.items = [m_welcome]
m_main.is_focused = True
#message(m_main.display_box())
lcd.message(m_main.display_box())
#lcd.clear()
#lcd.clear()
#time.sleep(0.3)
#lcd.message('blop')
print(m_main.display_box())
print(m_main.cursor_display_box())


'''