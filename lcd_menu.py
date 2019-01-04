HORIZONTAL = 0
VERTICAL = 1

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2
ALIGN_TOP = 0
ALIGN_BOTTOM = 2

SELECT = 0
RIGHT = 1
DOWN = 2
UP = 3
LEFT = 4


def str_size(string):
    """Dimensions of string once printed. Units are char.

    Parameters:
        string (str):

    Returns:
        list: List of int [width, height]
    """

    rows = string.split('\n')
    col = max([len(row) for row in rows])

    return [col, len(rows)]

def sum_iters(*iterables):
    """Sum iterables component-wise

    Parameters:
        *iterables (list): sequence of iterables

    Returns:
        list:

    """
    return [sum(i) for i in zip(*iterables)]

def prod_iters(*iterables):
    """Product iterables component-wise

    Parameters:
        *iterables (list): sequence of iterables

    Returns:
        list:

    """
    zipped = zip(*iterables)
    prod = []
    for cols in zipped:
        p = 1
        for col in cols:
            p *= col
        prod.append(p)
    return prod

def get_align_offset(string, box, hor=ALIGN_LEFT, vert=ALIGN_TOP):
    """Returns the positional offset of aligning a string inside a box

    Parameters:
        string (str): String to align
        box (list): List of int [width, height] Box size
        hor (int): Horizontal align constant
        vert (int): Vertical align constant

    Returns:
        list: List of int [x, y]

    """

    str_list = string.split('\n')
    size = str_size(string)
    delta = [box[0]-size[0], box[1]-size[1]]
    center_x = float(hor)*float(delta[0])/2.0
    center_y = float(vert)*float(delta[1])/2.0

    return [round(center_x), round(center_y)]




def get_loop_offset(pos, box):
    """Loops a position around a box

    Parameters:
        pos (list): List of int [x, y] Position
        box (list): List of int [width, height]

    Returns:
        list: List of int [x, y]

    """

    return [pos[0] % box[0], pos[1] % box[1]]


def offset_string(string, box, offset):
    """Move a string inside a box

    Parameters:
        string (str): 
        box (list): List of int [width, height]
        offset (list): List of int [x, y]

    Returns:
        string: Modified string
    """
    
    #str_list = string.split('\n')
    new_str = ''
    for row in range(box[1]):
        for col in range(box[0]):
                x = col-offset[0]
                y = row-offset[1]
                new_str += get_char(string, [x, y])
                '''
            try:
                if x < 0 or y < 0:
                    raise
                new_str += str_list[y][x]
            except:
                new_str += ' '
                '''
    return new_str
'''
def get_offset_char(string, box, pos, offset):
    str_list = string.split('\n')
    new_str = ' '
    for row in range(box[1]):
        for col in range(box[0]):
            if [col, row] == pos:
                try:
                    x = col-offset[0]
                    y = row-offset[1]
                    if x < 0 or y < 0:
                        raise
                    new_str = str_list[y][x]
                except:
                    pass
    return new_str

def get_offset_char2(string, box, pos):
    for row in range(box[1]):
        for col in range(box[0]):
            if [col, row] == pos:
                x = pos[0]
                y = pos[1]
                return get_char(string, pos)
    return ' '
'''

def get_char(string, pos):
    str_list = string.split('\n')
    try:
        if pos[0] < 0 or pos[1] < 0:
            raise
        return str_list[ pos[1] ][ pos[0] ]
    except:
        return ' '


class Menu(object):

    def __init__(self, name='', box=[16, 2], auto_size=False,
                 parent=None, items=[], loop=False, focus_end=True,
                 cursor_pos=[0, 0],
                 direction=HORIZONTAL, align_h=ALIGN_LEFT, align_v=ALIGN_TOP,
                 item_divider='', loop_divider='  '):
        self.name = name
        self.box = box
        self.loop = loop
        self.parent = parent
        self.focus_end = focus_end
        self.direction = direction
        self.align_h = align_h
        self.align_v = align_v
        self.offset = 0
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

        self.item_divider = item_divider
        self.loop_divider = loop_divider

    def __repr__(self):
        return '<Menu: {0}>'.format(self.items)

    def __str__(self):
        return self.display_box()

    @property
    def items_with_divs(self):
        """Return list of items with added dividers

        Returns:
            list: list of items
        """

        str_items = [Menu.item_as_str(item) for item in self.items]
        complete_list = []
        str_list = []

        # Insert Dividers
        for idx, string in enumerate(str_items):
            str_list.append(string)
            complete_list.append(self.items[idx])
            if (idx < len(str_items) - 1):
                str_list.append(self.item_divider)
                complete_list.append(self.item_divider)

        # Insert Loop Dividier
        if self.loop == True:
            complete_list.append(self.loop_divider)

        return complete_list

    @staticmethod
    def item_as_str(item):
        if isinstance(item, str):
            # txt
            #w, h = Menu.str_size(i)
            return item
        elif isinstance(item, str):
            # Menu
            return

    def items_to_strings(self):
        items = self.items_with_divs
        items_str = [Menu.item_as_str(item) for item in items]
        items_size = [str_size(string) for string in items_str]
        max_item_size = [max(i) for i in zip(*items_size)]
        base_offset = [0, 0]
        new_items_str = []

        for item in items:
            # item
            string = Menu.item_as_str(item)

            if(string):
                # if string is not empty
                size = str_size(string)
                new_str = ''
                str_list = string.split('\n')
                # box
                axis_flipped = [not b for b in self.axis]
                max_item_size_along_direction = prod_iters(
                    axis_flipped, max_item_size)
                item_box = [max(i) for i in zip(
                    max_item_size_along_direction, size)]

                # offset
                offset = base_offset
                align_offset = get_align_offset(string, item_box,
                                                hor=self.align_h,
                                                vert=self.align_v)
                offset = [offset[0] + align_offset[0],
                          offset[1] + align_offset[1]]

                # item_box loop
                for row in range(item_box[1]):
                    for col in range(item_box[0]):
                        # offset character
                        char_offset = offset

                        # apply offset
                        #new_str += get_offset_char(string, item_box,
                        #                           [col, row], char_offset)
                        char_offset = [col-offset[0], row-offset[1]]
                        new_str += get_char(string, [char_offset[0], char_offset[1]])
                    # put back newline char
                    if row < item_box[1]-1:
                        new_str += '\n'

                new_items_str.append(new_str)
        return new_items_str

    def max_items_box(self):
        strings = self.items_to_strings()
        return max([str_size(string) for string in strings])

    def display_box(self):
        return str_size(self.display())

    @property
    def content(self):
        strings = self.items_to_strings()
        items_box = self.max_items_box()
        ordered_strings = strings

        if self.direction == HORIZONTAL:
            new_string = ''
            ordered_strings = []
            for row in range(items_box[1]):
                cols = ''
                for string in strings:
                    str_list = string.split('\n')
                    cols += str_list[row]
                ordered_strings.append(cols)

        return '\n'.join(ordered_strings)

    @property
    def content_offset(self):
        string = self.content
        str_list = string.split('\n')
        box = str_size(string)
        #print('box: ', box)
        offset = prod_iters(self.axis, [self.offset]*2)

        new_str = ''
        for row in range(box[1]):
            for col in range(box[0]):
                # offset character
                char_offset = [offset[0]+col, offset[1]+row]

                if self.loop:
                    char_offset = get_loop_offset(char_offset, box)
                    #print('off: ', char_offset)

                # apply offset
                new_str += get_char(string, [char_offset[0], char_offset[1]])
                '''
                try:
                    new_str += str_list[char_offset[1]][char_offset[0]]
                except:
                    new_str += ' '
                '''
            # put back newline char
            if row < box[1]-1:
                new_str += '\n'
        return new_str




    @property
    def axis(self):
        return [self.direction == HORIZONTAL,
               self.direction == VERTICAL]





    @property
    def w(self):
        box = Menu.str_size(self.display_box())
        return box[0]


    @property
    def h(self):
        box = Menu.str_size(self.display_box())
        return box[1]


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

class Menu_h(Menu):


    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.item_divider = Line('  ')
        self.item_divider.auto_box_w()
        self.loop_divider = Line('  ')
        self.loop_divider.auto_box_w()

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
        return sum(total) + (self.item_divider.box_w * max(0, item_idx) )

    '''
    @property
    def w(self):
        total = []
        for i in self.items:
            total.append(i.box_w)

        answer = sum(total)
        if self.item_divider:
            answer += (self.item_divider.box_w * (len(total) - 1))
        if self.loop and self.loop_divider:
            answer += self.loop_divider.box_w

        return answer
    '''

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
                if isinstance(item, Menu):
                    txt = item.display().split('\n')[row]
                '''
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
                        cols.append(self.item_divider.display_box())
                    else:
                        cur_div_txt = '0'*self.item_divider.w
                        cur_div = Line(txt=cur_div_txt, box_w=self.item_divider.box_w)
                        cols.append(cur_div.display_box())
                elif self.loop:
                    if not cursor:
                        cols.append(self.loop_divider.display_box())
                    else:
                        cur_div_txt = '0'*self.loop_divider.w
                        cur_div = Line(txt=cur_div_txt, box_w=self.loop_divider.box_w)
                        cols.append(cur_div.display_box())
                '''
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


class Menu_v(Menu):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.btn_next = [DOWN, ]
        self.btn_prev = [UP, ]
        self.btn_select = [SELECT, ]
        self.btn_more = [RIGHT, ]
        self.btn_less = [LEFT, ]
        #self.item_divider = Line('---', box_w=3)
        self.item_divider = None
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
        if self.item_divider:
            return sum(total) + (self.item_divider.box_h * max(0, item_idx) )
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
        if self.item_divider:
            answer += (self.item_divider.box_h * (len(total) - 1))
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
                if self.item_divider:
                    if not cursor:
                        rows.append(self.item_divider.display_box())
                    else:
                        cur_div_txt = '0'*self.item_divider.w
                        cur_div = Line(txt=cur_div_txt, box_w=self.item_divider.box_w)
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

    #menu = Menu(name='menu', direction=Menu.VERTICAL, items= ['Blop', 'Cola!!'])
    #print(menu.display())
    txts_div = ['BLOP\nlol\noff', 'COLAAA!', 'man']
    print(str_size(txts_div[0]))
    direction = 1
    box = [16, 2]

    m = Menu(name='menu', box=box, direction=0, items=txts_div, align_h=0, align_v=1, item_divider='', loop_divider='--')
    #m.loop = True
    #print(m.items_with_divs)
    #print(m.items_to_strings())
    #print('\n'.join(['0'*m.display_box()[0]]*m.display_box()[1]))
    print(m.items_with_divs)
    print(m.items_to_strings())
    print(str_size(m.content))
    print(m.content)
    #m.loop = True

    print(' ')
    print('start')
    print(' ')
    print('-------------')
    for i in range(0, 10):
        print(m.content_offset)
        print('-------------')
        m.offset -= 1

    '''
    for i in txts_div:
        offset = get_align_offset(i, box, hor=1, vert=1)
        print('-'*box[0])
        print('offset: ', offset)
        string = offset_string(i, box, offset)
        print(string)
    '''
