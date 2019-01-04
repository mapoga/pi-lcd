HORIZONTAL = 0
VERTICAL = 1

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2
ALIGN_TOP = 0
ALIGN_BOTTOM = 2


def str_size(string):
    """2D dimension of string once printed. Units are char.

    Parameters:
        string (str):

    Returns:
        list: List of int [width, height]
    """

    rows = string.split('\n')
    col = max([len(row) for row in rows])

    return [col, len(rows)]


def prod_iters(*iterables):
    """Product of iterables component-wise

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
    delta = [-box[0]+size[0], -box[1]+size[1]]
    center_x = float(hor)*float(delta[0])/2.0
    center_y = float(vert)*float(delta[1])/2.0

    return [round(center_x), round(center_y)]


def get_loop_offset(pos, box):
    """Returns a position looped around a box

    Parameters:
        pos (list): List of int [x, y] Position
        box (list): List of int [width, height]

    Returns:
        list: List of int [x, y]

    """

    return [pos[0] % box[0], pos[1] % box[1]]


def get_char(string, pos, filler=' '):
    """Returns the character at 2D position in string.
    If none found use filler.

    Parameters:
        string (str): 
        pos (list): List of int [x, y] Position
        filler (str): Single character for filling. Space by default

    Returns:
        str: single character
    """

    str_list = string.split('\n')
    try:
        if pos[0] < 0 or pos[1] < 0:
            raise
        return str_list[pos[1]][pos[0]]
    except:
        return filler


def string_move(string, box, offset, loop, filler=' '):
    """Move and return a string inside a box

    Parameters:
        string (str): 
        box (list): List of int [width, height]
        offset (list): List of int [x, y]
        loop (bool): True if string is looping
        filler (str): Single character for filling. Space by default

    Returns:
        string: Modified string
    """

    new_str = ''
    for row in range(box[1]):
        for col in range(box[0]):
            char_offset = [col+offset[0], row+offset[1]]
            if loop:
                char_offset = get_loop_offset(char_offset, box)
            new_str += get_char(string, char_offset, filler=filler)
        if row < box[1]-1:
            new_str += '\n'

    return new_str


def string_align_move(string, box, offset, align_h, align_v,
                 loop=False, filler=' '):
    """Align and position a string in relation to a box 

    Parameters:
        string (str):
        box (list): list of int [widht, height]
        offset (list): list of int [x, y]
        align_h (int): range(0-2)
        align_v (int): range(0-2)
        loop (bool): True if string is looping
        filler (str): Single character for filling. Space by default

    Returns:
        str: Aligned and moved string

    """

    # calculate offset
    align_offset = get_align_offset(string, box,
                                    hor=align_h,
                                    vert=align_v)
    offset = [offset[0] + align_offset[0],
              offset[1] + align_offset[1]]
    # apply offset
    return string_move(string, box, offset, loop, filler=filler)

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
        self.btn_next = []
        self.btn_prev = []
        self.btn_select = []
        self.btn_more = []
        self.btn_less = []
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
        return self.content_offset_boxed()

    @staticmethod
    def axis(direction):
        return [direction == HORIZONTAL,
                direction == VERTICAL]

    @staticmethod
    def _items_insert_divs(items, item_div, loop_div, loop):
        """Return list of items with added dividers

        Parameters:
            items (list): list of Menu or str
            item_div (str): String representing the item divider
            loop_div (str): String representing the loop divider
            loop (bool): True if menu is looping

        Returns:
            list: list of items
        """

        complete_list = []
        for idx, item in enumerate(items):

            # Insert item
            complete_list.append(item)

            if (idx < len(items) - 1):
                # Insert item divider
                complete_list.append(item_div)


        if loop == True:
            # Insert loop dividier
            complete_list.append(loop_div)

        return complete_list

    

    @staticmethod
    def _items_expanded_aligned(items, offset, axis, align_h, align_v):
        """Align items in relation to their combined max box and direction

        Returns:
            list: list of strings.
        """

        # Max size
        max_item_size = Menu._items_max_box(items)
        # direction
        axis_flipped = [not b for b in axis]
        max_size_across_direction = prod_iters(axis_flipped, max_item_size)

        new_items_str = []
        for item in items:

            string = str(item)
            if(string):
                # box
                size = str_size(string)
                item_box = [max(i) for i in zip(max_size_across_direction,
                                                size)]
                # align
                new_str = string_align_move(string, item_box,
                                            offset, align_h,
                                            align_v, loop=False)
                new_items_str.append(new_str)
        return new_items_str

    @staticmethod
    def _items_max_box(items):
        """Maximum size items have

        Returns:
            list: list of int [w, h] size
        """

        strings = [str(item) for item in items]
        sizes = [str_size(string) for string in strings]
        #print(sizes)
        return [max(i) for i in zip(*sizes)]

    @staticmethod
    def items_content(items, direction, loop, align_h, align_v,
                item_divider, loop_divider):
        """Full content of menu wihtout offset

        Returns:
            str: Menu content
        """
        axis = Menu.axis(direction)

        items = Menu._items_insert_divs(items, item_divider, loop_divider, loop)
        strings = Menu._items_expanded_aligned(items, [0,0], axis, align_h, align_v)
        items_box = Menu._items_max_box(items)
        ordered_strings=strings

        if direction == HORIZONTAL:
            new_string=''
            ordered_strings=[]
            for row in range(items_box[1]):
                cols=''
                for string in strings:
                    str_list=string.split('\n')
                    cols += str_list[row]
                ordered_strings.append(cols)

        return '\n'.join(ordered_strings)

    @staticmethod
    def items_content_offset(items, offset, direction, loop, align_h, align_v,
                       item_divider, loop_divider):
        """Return and offseted version of the content

        Returns:
            str: Content offset
        """
        content = Menu.items_content(items, direction, loop, align_h, align_v,
                                  item_divider, loop_divider)
        box = str_size(content)
        axis = Menu.axis(direction)
        offset = prod_iters(axis, [offset]*2)

        return string_move(content, box, offset, loop)


    @property
    def content(self):
        return self.items_content(self.items, self.direction, self.loop,
                                  self.align_h, self.align_v,
                                  self.item_divider, self.loop_divider)

    @property
    def content_offset(self):
        return self.items_content_offset(self.items, self.offset, self.direction, self.loop,
                                  self.align_h, self.align_v,
                                  self.item_divider, self.loop_divider)

    def content_offset_boxed(self):
        return string_move(self.content_offset, self.box, [0, 0], False)



    def display_box(self):
        return str_size(self.display())




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




if __name__ == "__main__":

    #menu = Menu(name='menu', direction=Menu.VERTICAL, items= ['Blop', 'Cola!!'])
    #print(menu.display())
    txts_div = ['BLOP\nlol\noff', 'COLAAA!', 'man']
    print(str_size(txts_div[0]))
    direction = 1
    box = [16, 2]

    m = Menu(name='menu', box=box, direction=0, items=txts_div, align_h=1, align_v=1, item_divider='', loop_divider='--')
    m.loop = True
    #print(m.content)

    #print(m.items)
    #_items_insert_divs = Menu._items_insert_divs(m.items, m.item_divider, m.loop_divider, m.loop)
    #print(_items_insert_divs)


    print(str_size(m.content))
    print(m.content)
    print(' ')
    print('start')
    print(' ')
    print('-------------')
    #m.box = [6,3]
    for i in range(0, 10):
        print(m)
        print('-------------')
        m.offset += 1
    '''
    box = [6, 3]
    offset = [0,1]
    loop = True
    string = 'Blop\nlol\nCoca'
    str_mod = string_move(string, box, offset, loop)
    print(string)
    print(str_mod)
    '''