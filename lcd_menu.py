
ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2

SELECT                  = 0
RIGHT                   = 1
DOWN                    = 2
UP                      = 3
LEFT                    = 4

class Line(object):

    def __init__(self, txt='', box_w=16, align=ALIGN_LEFT):
        self.txt = txt
        self.box_w = box_w
        self.loop = True
        self.align = align
        self.position = 0
        self.loop_divider = '   '
        self.filler = ' '
        self.is_focused = False

    def __repr__(self):
        return self.display_box()

    def auto_box_w(self):
        self.box_w = len(self.txt)

    @property
    def box_h(self):
        return 1

    @property
    def is_focused(self):
        return self._is_focused

    @is_focused.setter
    def is_focused(self, val):
        self._is_focused = val
        if self.is_focused:
            print('Focused:')
            print(self)
            pass

    @property
    def w(self):
        if self.loop and len(self.txt) > self.box_w:
            return len(self.txt) + len(self.loop_divider)
        else:
            return len(self.txt)

    @property
    def h(self):
        return 1

    def display(self):
        if self.loop and len(self.txt) > self.box_w:
            return self.txt + self.loop_divider
        else:
            return self.txt

    def display_box(self):
        # alignement
        align_offset = 0 
        if self.align == ALIGN_CENTER:
            align_offset = round((self.box_w/2)-(self.w/2))
        elif self.align == ALIGN_RIGHT:
                align_offset = self.box_w - self.w

        if self.loop and len(self.txt) > self.box_w:
            align_offset = 0
        align_offset += self.position
        txt = ''

        # offset
        for i in range(self.box_w):
            t = self.filler
            try:

                pos = i-align_offset
                # looping
                if self.loop:
                    if len(self.txt) > self.box_w:
                        pos = pos % self.w
                    else:
                        pos = pos % (self.box_w + 1)
                if pos >= 0:
                    t = self.display()[pos]
            except:
                pass

            txt += t

        return txt


class Menu_Abstract(object):

    def __init__(self, name='', box_w=16, box_h=2, auto_size=False,
                 parent=None, items=[], loop=False, focus_end=True,
                 cursor_pos=[0, 0]):
        self.name = name
        self.box_w = box_w
        self.box_h = box_h
        self.loop = loop
        self.parent = parent
        self.focus_end = focus_end
        # Hidden
        self._cursor_pos = cursor_pos
        self._items = items
        self._items_focus_idx = 0
        self._is_focused = False
        # Buttons
        self.btn_next = [RIGHT, ]
        self.btn_prev = [LEFT, ]
        self.btn_select = [SELECT, ]
        self.btn_more = [UP, ]
        self.btn_less = [DOWN, ]
        # Actions
        self.do_more = None
        self.do_less = None
        self.do_select = None
        self.do_any = None

    def __repr__(self):
        return '<Menu_Abstract: {0}>'.format(self.items)


    @property
    def cursor_pos(self):
        pos = self._cursor_pos
        disp_min = [0,0]
        disp_max = [self.box_w-1, self.box_h-1]
        disp_max = max(disp_min, disp_max)
        pos = max(disp_min, pos)
        pos = min(disp_max, pos)
        return pos

    @cursor_pos.setter
    def cursor_pos(self, pos=[0,0]):
        self._cursor_pos = pos

    def cursor_display(self):
        if self.focus_end:
            txt = ''
            for row in range(self.h):
                for col in range(self.w):
                    if row == self.cursor_pos[1] and col == self.cursor_pos[0] and self.is_focused:
                        txt += '1'
                    else:
                        txt += '0'
                if row < self.h-1:
                    txt += '\n'
            return txt
        else:
            return self.display(cursor=True)

    def cursor_display_box(self):
        return self.display_box(txt=self.cursor_display())

    def cursor_pos_box(self):
        txt = self.cursor_display_box().split('\n')
        for row in range(self.box_h):
            for col in range(self.box_w):
                val = '0'
                try:
                    val = txt[row][col]
                except:
                    pass
                if val == '1':
                    return [col, row]
        return self.cursor_pos




    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, val):
        self._items = val
        for i in self.items:
            try:
                i.parent = self
            except:
                pass

    @property
    def is_focused(self):
        return self._is_focused

    @is_focused.setter
    def is_focused(self, val):
        self._is_focused = val

        if self.is_focused:
            print('Focused: {0}'.format(self.name))
            self.items_focus_idx = self.items_focus_idx
        else:
            for i in self.items:
                i.is_focused = False

    @property
    def items_focus_idx(self):
        return self._items_focus_idx
        
    @items_focus_idx.setter
    def items_focus_idx(self, idx):
        self._items_focus_idx = idx
        if not self.focus_end:
            for i in self.items:
                if i == self.focused_item():
                    i.is_focused = True
                else:
                    i.is_focused = False

    def focused_item(self):
        return self.items[self.items_focus_idx]


    def next(self):
        if self.focus_end and self.parent:
            self.parent.next()
        else:
            if self.loop:
                self.items_focus_idx = (self.items_focus_idx + 1) % len(self.items)
            else:
                self.items_focus_idx = min(self.items_focus_idx + 1, len(self.items) - 1)

    def prev(self):
        if self.focus_end and self.parent:
            self.parent.prev()
        else:
            if self.loop:
                self.items_focus_idx = (self.items_focus_idx - 1) % len(self.items)
            else:
                self.items_focus_idx = max(self.items_focus_idx - 1, 0)

    def on_pressed(self, btn):
        if not self.is_focused:
            print('first')
            self.is_focused = True
        else:
            if not self.focus_end:
                ele = self.focused_item()
            else:
                ele = self
            #print('On pressed elements: ', ele)
            try:
                ele.do_any(ele)
                print('ANY: {0}'.format(self.name))
            except:
                pass
            try:
                if btn in self.btn_next:
                    self.next()
                elif btn in self.btn_prev:
                    self.prev()
                elif btn in self.btn_select:
                    ele.do_select(ele)
                elif btn in self.btn_more:
                    ele.do_more(ele)
                elif btn in self.btn_less:
                    ele.do_less(ele)
            except:
                pass

class Menu_h(Menu_Abstract):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.divider_line = Line('  ')
        self.divider_line.auto_box_w()
        self.loop_divider = Line('  ')
        self.loop_divider.auto_box_w()

    def __repr__(self):
        return self.display_box()

    def auto_box_w(self):
        self.box_w = self.w

    def auto_box_h(self):
        box_heights = [i.box_h for i in self.items]
        self.box_w = max(box_heights)

    def auto_box(self):
        self.auto_box_w()
        self.auto_box_h()

    def offset_h(self, offset=0, txt=None):
        if txt:
            disp_txt = txt
        else:
            disp_txt = self.display()

        old_rows = disp_txt.split('\n')

        rows = []
        for row in old_rows:
            txt = ''
            for i in range(self.box_w):
                t = ''
                try:
                    pos = i + offset
                    # looping
                    if self.loop:
                        if len(row) > self.box_w:
                            pos = pos % self.w
                            #pos = pos % (self.box_w + 1)
                        else:
                            pos = pos % (self.box_w + 1)
                    #print('pos: ', pos)
                    if pos >= 0:
                        t = row[pos]
                except:
                    pass

                txt += t

            rows.append(txt)
        return '\n'.join(rows)

    def item_pos(self, item_idx):
        #print('item idx: ', item_idx)
        total = []
        try:
            for idx in range(item_idx):
                total.append(self.items[idx].box_w)
        except:
            pass
        return sum(total) + (self.divider_line.box_w * max(0, item_idx) )


    @property
    def w(self):
        total = []
        for i in self.items:
            total.append(i.box_w)

        answer = sum(total)
        if self.divider_line:
            answer += (self.divider_line.box_w * (len(total) - 1))
        if self.loop and self.loop_divider:
            answer += self.loop_divider.box_w

        return answer

    @property
    def h(self):
        total = []
        for i in self.items:
            total.append(i.box_h)
        return max(total)

    def display(self, cursor=False):
        rows = []
        for row in range(self.box_h):
            cols = []
            for idx, item in enumerate(self.items):
                txt = ''
                try:
                    if not cursor:
                        txt = item.display_box().split('\n')[row]
                    else:
                        txt = item.display_box(txt=item.cursor_display()).split('\n')[row]
                except:
                    txt = ''.join([' ' for i in range(item.box_w)])
                cols.append(txt)
                if (idx < len(self.items) - 1):
                    if not cursor:
                        cols.append(self.divider_line.display_box())
                    else:
                        cur_div_txt = '0'*self.divider_line.w
                        cur_div = Line(txt=cur_div_txt, box_w=self.divider_line.box_w)
                        cols.append(cur_div.display_box())
                elif self.loop:
                    if not cursor:
                        cols.append(self.loop_divider.display_box())
                    else:
                        cur_div_txt = '0'*self.loop_divider.w
                        cur_div = Line(txt=cur_div_txt, box_w=self.loop_divider.box_w)
                        cols.append(cur_div.display_box())

            rows.append(''.join(cols))
        return '\n'.join(rows)

    def display_box(self, txt=None):
        if txt:
            disp_txt = txt
        else:
            disp_txt = self.display()

        if self.loop:
            amount = self.item_pos(self.items_focus_idx)
        else:
            focused_pos = self.item_pos(self.items_focus_idx)
            if self.w - focused_pos < self.box_w:
                amount = self.w-self.box_w
            else:
                amount = focused_pos

        return self.offset_h(offset=amount, txt=disp_txt)


class Menu_v(Menu_Abstract):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.btn_next = [DOWN, ]
        self.btn_prev = [UP, ]
        self.btn_select = [SELECT, ]
        self.btn_more = [RIGHT, ]
        self.btn_less = [LEFT, ]
        #self.divider_line = Line('---', box_w=3)
        self.divider_line = None
        #self.loop_divider = Line('!!!!!!!!!!!!!!!!!', box_w=box_w)
        self.loop_divider = None

    def __repr__(self):
        return self.display_box()

    def auto_box_w(self):
        box_widths = [i.box_w for i in self.items]
        self.box_w = max(box_widths)

    def auto_box_h(self):
        self.box_h = self.h

    def auto_box(self):
        self.auto_box_w()
        self.auto_box_h()

    def offset_v(self, offset=0, txt=None):
        if txt:
            disp_txt = txt
        else:
            disp_txt = self.display()

        rows = disp_txt.split('\n')
        txt = []
        for i in range(self.box_h):
            t = ' '*self.box_w
            try:
                pos = i + offset
                # looping
                if self.loop:
                    if len(rows) > self.box_h:
                        pos = pos % self.h
                    else:
                        pos = pos % (self.box_h + 1)
                if pos >= 0:
                    t = rows[pos]
            except:
                pass

            txt.append(t)
        return '\n'.join(txt)



    def item_pos(self, item_idx):
        total = []
        try:
            for idx in range(item_idx):
                total.append(self.items[idx].box_h)
        except:
            pass
        if self.divider_line:
            return sum(total) + (self.divider_line.box_h * max(0, item_idx) )
        else:
            return sum(total)

    @property
    def w(self):
        total = []
        for i in self.items:
            total.append(i.box_w)
        return max(total)

    @property
    def h(self):
        total = []
        for i in self.items:
            total.append(i.box_h)

        answer = sum(total)
        if self.divider_line:
            answer += (self.divider_line.box_h * (len(total) - 1))
        if self.loop and self.loop_divider:
            answer += self.loop_divider.box_h

        return answer

    def display(self, cursor=False):
        rows = []
        for idx, item in enumerate(self.items):
            if not cursor:
                rows.append(''.join(item.display_box()))
            else:
                rows.append(''.join(item.display_box(txt=item.cursor_display())))
            if idx < len(self.items) - 1:
                if self.divider_line:
                    if not cursor:
                        rows.append(self.divider_line.display_box())
                    else:
                        cur_div_txt = '0'*self.divider_line.w
                        cur_div = Line(txt=cur_div_txt, box_w=self.divider_line.box_w)
                        rows.append(cur_div.display_box())
            elif self.loop:
                if self.loop_divider:
                    if not cursor:
                        rows.append(self.loop_divider.display_box())
                    else:
                        cur_div_txt = '0'*self.loop_divider.w
                        cur_div = Line(txt=cur_div_txt, box_w=self.loop_divider.box_w)
                        rows.append(cur_div.display_box())
        return '\n'.join(rows)

    def display_box(self, txt=None):
        if txt:
            disp_txt = txt
        else:
            disp_txt = self.display()

        if self.loop:
            amount = self.item_pos(self.items_focus_idx)
        else:
            focused_pos = self.item_pos(self.items_focus_idx)
            if self.h - focused_pos < self.box_h:
                amount = self.h-self.box_h
            else:
                amount = focused_pos

        return self.offset_v(offset=amount, txt=disp_txt)

            

if __name__ == "__main__":

    back_item = Menu_v(box_w = 4)
    back_item_title = Line('BACK')
    back_item_title.auto_box_w()
    back_item_value = Line('<---')
    back_item_value.box_w = back_item_title.box_w
    back_item.items = [back_item_title, back_item_value]


    real_Menu = Menu_h(box_h=2)

    ttb_item = Menu_v(box_w = 5)
    ttb_item_title = Line('TURN', box_w=5)
    ttb_item_value = Line('TABLE')
    ttb_item_value.box_w = ttb_item_title.box_w
    ttb_item.items = [ttb_item_title, ttb_item_value]

    stops_item = Menu_v(box_w=4)
    stops_item_title = Line('Stop')
    stops_item_title.auto_box_w()
    stops_item_value = Line('32')
    stops_item_value.box_w = stops_item_title.box_w
    stops_item_value.align = ALIGN_CENTER
    stops_item.items = [stops_item_title, stops_item_value]

    wait_item = Menu_v(box_w=4)
    wait_item_title = Line('Wait')
    wait_item_title.auto_box_w()
    wait_item_value = Line('5')
    wait_item_value.box_w = wait_item_title.box_w
    wait_item_value.align = ALIGN_CENTER
    wait_item.items = [wait_item_title, wait_item_value]

    setting_item = Menu_v(box_w=4)
    setting_item_title = Line('Settings')
    setting_item_title.auto_box_w()
    setting_item_value = Line('')
    setting_item_value.box_w = setting_item_title.box_w
    setting_item_value.align = ALIGN_CENTER
    setting_item.items = [setting_item_title, setting_item_value]
    setting_item.auto_box()

    real_Menu.items = [ttb_item, back_item, stops_item, wait_item, setting_item]
    print(real_Menu.display())

    real_Menu.focus_end = False
    #real_Menu.loop = True
    real_Menu.on_pressed(SELECT)
    print('turns\n')
    for i in range(5):
        real_Menu.on_pressed(RIGHT)
        print(real_Menu)

    print(ttb_item.cursor_display())


    '''

    real_menuV = Menu_v()
    real_menuV.focus_end = False

    ttb_itemV = Menu_h()
    ttb_itemV_title = Line('TURN')
    ttb_itemV_title.auto_box_w()
    ttb_itemV_value = Line('TABLE')
    ttb_itemV_title.auto_box_w()
    ttb_itemV.items = [ttb_itemV_title, ttb_itemV_value]

    back_itemV = Menu_h()
    back_itemV_title = Line('Back')
    back_itemV_title.auto_box_w()
    back_itemV_value = Line('<---')
    back_itemV_title.auto_box_w()
    back_itemV.items = [back_itemV_title, back_itemV_value]

    stops_itemV = Menu_h()
    stops_itemV_title = Line('Stop')
    stops_itemV_title.auto_box_w()
    stops_itemV_value = Line('32')
    stops_itemV_title.auto_box_w()
    stops_itemV.items = [stops_itemV_title, stops_itemV_value]

    wait_itemV = Menu_h()
    wait_itemV_title = Line('Wait')
    wait_itemV_title.auto_box_w()
    wait_itemV_value = Line('5')
    wait_itemV_title.auto_box_w()
    wait_itemV.items = [wait_itemV_title, wait_itemV_value]

    settings_itemV = Menu_v()
    settings_itemV_title = Line('Sett', box_w=16)
    settings_itemV_value = Line('iinn', box_w=16)
    settings_itemV_third = Line('ngss', box_w=16)
    settings_itemV_value.align = ALIGN_RIGHT
    settings_itemV_third.align = ALIGN_CENTER
    settings_itemV.items = [settings_itemV_title, settings_itemV_value, settings_itemV_third]
    settings_itemV.auto_box()

    real_menuV.items = [ttb_itemV, back_itemV, stops_itemV, settings_itemV, wait_itemV]
    real_menuV.loop = True
    print('______________')
    print(real_menuV.display())
    print('______________')
    print('______________')
    print(real_menuV.h)

    def sel(self):
        print('select', self)

    real_menuV.focus_end = False
    back_itemV.do_select = sel
    real_menuV.on_pressed(SELECT)
    for i in range(25):
        #print(real_menuV.items_focus_idx)
        #print(real_menuV.item_pos(real_menuV.items_focus_idx))
        real_menuV.on_pressed(LEFT)
        print(real_menuV)
        #print(real_menuV.offset_v(-i))
        print('---------')
    #real_menuV.next()
    '''
