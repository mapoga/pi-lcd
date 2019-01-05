HORIZONTAL = 0
VERTICAL = 1

ALIGN_LEFT = 0
ALIGN_CENTER = 1
ALIGN_RIGHT = 2
ALIGN_TOP = 0
ALIGN_BOTTOM = 2


def string_size(string):
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
    size = string_size(string)
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


def get_char_at_pos(string, pos, filler=' '):
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

def find_char_pos(string, char):
    rows = string.split('\n')
    for row_idx, row in enumerate(rows):
        index = row.find(char)
        if index >= 0:
            return [index, row_idx]

    return None


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
            new_str += get_char_at_pos(string, char_offset, filler=filler)
        if row < box[1]-1:
            new_str += '\n'

    return new_str


def string_align_move(string, box, offset, align_h, align_v, loop=False, filler=' '):
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

class Action(object):

    def __init__(self, trigger, action, action_args=[], action_kwargs=[]):
        self.trigger = trigger
        self.action = action
        self.action_args = action_args
        self.action_kwargs = action_kwargs

    def do(self):
        return self.action(*self.action_args, **self.action_kwargs)

    def check(self, trigger, dry_run=False):
        if trigger == self.trigger:
            if not dry_run:
                self.do()
            return True

class Menu(object):

    def __init__(self, name='', box=[16, 2], auto_size=False,
                 parent=None, items=[], loop=False, selected_end=True,
                 cursor_pos=[0, 0],
                 direction=HORIZONTAL, align_h=ALIGN_LEFT, align_v=ALIGN_TOP,
                 item_div='', loop_div='  '):
        # Hidden
        self._cursor_pos = [0, 0]
        self._items = []
        self._index = 0
        self._selected = None
        self._parent = None
        self._focused_item = None

        self.parent = parent
        self.cursor_pos = cursor_pos
        self.items = items

        self.name = name
        self.box = box
        self.loop = loop
        #self.selected_end = selected_end
        self.direction = direction
        self.align_h = align_h
        self.align_v = align_v
        self.offset = 0

        self.actions = []

        self.item_div = item_div
        self.loop_div = loop_div

    def __repr__(self):
        return '<Menu: {0}>'.format(self.items)

    def __str__(self):
        return self.display()


    ###########################################################################
    # Static Mehtods
    ###########################################################################


    @staticmethod
    def axis(direction):
        return [direction == HORIZONTAL,
                direction == VERTICAL]

    @staticmethod
    def _items_max_box(items):
        """Maximum size of combined items

        Parameters:
            items (list): list of Menu or str

        Returns:
            list: list of int [w, h] size
        """

        strings = [str(item) for item in items]
        sizes = [string_size(string) for string in strings]
        # print(sizes)
        return [max(i) for i in zip(*sizes)]

    @staticmethod
    def _items_insert_divs(items, axis, item_div, loop_div, loop):
        """Return a list of items with inserted dividers

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

            if (idx < (len(items) - 1)):
                # Insert item divider
                complete_list.append(item_div)

        if loop == True:
            # Insert loop dividier
            complete_list.append(loop_div)

        return complete_list

    @staticmethod
    def _items_expanded_aligned(items, offset, axis, align_h, align_v):
        """Expand and align items.
        Use their combined max box across the directional axis

        Parameters:
            items (list):
            offset (list): list of int [x, y]
            axis (list): list of bool [horizontal, vertical]
            align_h (int): range(0-2)
            align_v (int): range(0-2)

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
                size = string_size(string)
                item_box = [max(i) for i in zip(max_size_across_direction,
                                                size)]
                # align
                new_str = string_align_move(string, item_box, offset, align_h, align_v, loop=False)
                #new_str = string_move(string, item_box, offset, loop=False, filler=' ')
                new_items_str.append(new_str)

        #print(new_items_str)
        return new_items_str

    @staticmethod
    def _items_content(items, box, direction, loop, align_h, align_v, item_div, loop_div):
        """Full content of menu without move or crop

        Parameters:
            items (list):
            direction (bool): Vertical if True
            loop (bool): True if menu is looping
            align_h (int): range(0-2)
            align_v (int): range(0-2)
            item_div (str): String representing the item divider
            loop_div (str): String representing the loop divider

        Returns:
            str: Menu content
        """
        axis = Menu.axis(direction)

        # Calculate if loop div is needed
        if loop:
            sizes = [string_size(str(i)) for i in items]
            sizes_summed = [sum(i) for i in zip(*sizes)]
            items_length = sum(prod_iters(axis, sizes_summed))
            box_length = sum(prod_iters(axis, box))
            if items_length <= box_length:
                loop = False

        # string
        items = Menu._items_insert_divs(items, axis, item_div, loop_div, loop)
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
    def _items_content_moved(items, box, offset, direction, loop, align_h, align_v, item_div, loop_div):
        """Returns a moved version of _items_content

        Parameters:
            items (list):
            offset (list): list of int [x, y]
            direction (bool): Vertical if True
            loop (bool): True if menu is looping
            align_h (int): range(0-2)
            align_v (int): range(0-2)
            item_div (str): String representing the item divider
            loop_div (str): String representing the loop divider

        Returns:
            str: Content offset
        """
        content = Menu._items_content(items, box, direction, loop, align_h, align_v,
                                  item_div, loop_div)
        box = string_size(content)
        axis = Menu.axis(direction)
        offset = prod_iters(axis, [offset]*2)

        return string_move(content, box, offset, loop)


    ###########################################################################
    # Properties
    ###########################################################################


    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        for item in self.items:
            if isinstance(item, Menu):
                # Menu
                item.parent = self
            elif isinstance(item, str):
                # str
                pass
            else:
                raise TypeError('Items should be instance of Menu or str: {}'.format(item))
        self._items = items

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, parent):
        # Remove parent
        if parent == None:
            if self.has_item(self.parent_topmost().focus):
                # keep selected from last parent_topmost
                self.focus = self.parent_topmost().focus
            else:
                # selected on self
                self.focus = self

        elif not isinstance(parent, Menu):
            raise TypeError('Parent should be an instance of Menu or None: {}'.format(parent))

        self._parent = parent

    @property
    def focus(self):
        return self._focused_item

    @focus.setter
    def focus(self, item):
        if not (isinstance(item, Menu) or item == None):
            raise TypeError('focus should be an instance of Menu or None: {}'.format(item))
        self._focused_item = item


    @property
    def cursor_pos(self):
        pos = self._cursor_pos
        pos_min = [0,0]
        pos_max = [max(self.box[0]-1, 0), max(self.box[1]-1, 0)]
        pos = [max(p) for p in zip(pos_min, pos)]
        pos = [min(p) for p in zip(pos_max, pos)]
        
        return pos

    @cursor_pos.setter
    def cursor_pos(self, pos):
        self._cursor_pos = pos


    ###########################################################################
    # Methods
    ###########################################################################


    def content(self):
        return self._items_content(self.items, self.box, self.direction, self.loop,
                                   self.align_h, self.align_v,
                                   self.item_div, self.loop_div)

    def display(self):
        if not self.items:
            # No items
            return string_move(' ', self.box, [0, 0], False, filler=' ')

        # Has items
        content_moved = self._items_content_moved(
            self.items, self.box, self.offset, self.direction, self.loop,
            self.align_h, self.align_v, self.item_div, self.loop_div)
        align_pos = get_align_offset(content_moved, self.box, hor=self.align_h, vert=self.align_v)
        return string_move(content_moved, self.box, align_pos, False)

    def cursor_display(self, pos=False):
        display = ''
        # generate from self
        '''
        if self.parent_topmost().focus == self:
            pos_invert = [-self.cursor_pos[0], -self.cursor_pos[1]]
            display = string_move('1', self.box, pos_invert, False, filler=' ')
        '''
        '''
        if self.parent_topmost().focus == self and self.items:
            pos_invert = [-self.cursor_pos[0], -self.cursor_pos[1]]
            display = string_move('1', self.box, pos_invert, False, filler=' ')
        '''
        if not self.items:
            pos_invert = [-self.cursor_pos[0], -self.cursor_pos[1]]
            string = string_move('1', self.box, pos_invert, False, filler=' ')
        else:
            # generate from items 
            items = []
            for item in self.items:
                if isinstance(item, Menu):
                    # go deeper
                    items.append(item.cursor_display())
                else:
                    if item == self.selected():
                        pos_invert = [-self.cursor_pos[0], -self.cursor_pos[1]]
                        string = string_move('1', string_size(item), pos_invert, False, filler=' ')
                        items.append(string)
                    else:
                        # blank for unselected
                        items.append(string_move(' ', string_size(item), [0, 0], False, filler=' '))

            content_moved = self._items_content_moved(
                items, self.box, self.offset, self.direction, self.loop,
                self.align_h, self.align_v, self.item_div, self.loop_div)
            align_pos = get_align_offset(content_moved, self.box, hor=self.align_h, vert=self.align_v)
            display = string_move(content_moved, self.box, align_pos, False)

        if pos:
            return find_char_pos(display, '1')
        else:
            return display


    def set_box_to_content(self, w=True, h=True):
        content = self._items_content(self.items, self.box, self.direction, False,
                                   self.align_h, self.align_v,
                                   self.item_div, self.loop_div)
        size = string_size(content)
        if w:
            self.box[0] = size[0]
        if h:
            self.box[1] = size[1]

    def first(self):
        self.select_index(0)
        return self.selected()

    def last(self):
        self.select_index(len(self.items)-1)
        return self.selected()

    def next(self):
        self.select_index(self.selected_index() + 1)
        return self.selected()

    def prev(self):
        self.select_index(self.selected_index() - 1)
        return self.selected()

    def select_index(self, index):
        if self.loop:
            # loop
            self._index = index % len(self.items)
        else:
            # Ends
            self._index = max(min(index, len(self.items)-1), 0)
        self.offset = self.selected_index()

    def select(self, item):
        if item in self.items:
            self.select_index(self.items.index(item))
        else:
            raise ValueError('Selected item should be in items: {}',format(item))

    def selected_index(self):
        return self._index

    def selected(self):
        return self.items[self.selected_index()]

    def has_item(self, item, recursive=False):

        childrens = self.items
        while childrens:
            current = childrens.pop(0)
            if current == item:
                return True
            if recursive:
                childrens.extend(current.items)

    def has_parent(self, item, recursive=False):

        parent = self.parent
        while parent:
            current = parent
            if current == item:
                return True
            if recursive:
                parent = current.parent

    def parent_topmost(self, max_rec=100):
        recursions = 0
        parent = self.parent
        parent_topmost = self
        while parent and recursions < max_rec:
            recursions += 1
            parent_topmost = parent
            parent = parent.parent
        return parent_topmost

    def selected_parent_topmost(self):
        self.selected = self.parent_topmost

    '''
    def selected_offset(self):
        items = s
        content = self._items_content(self.items, self.box, self.direction, self.loop,
                                   self.align_h, self.align_v,
                                   self.item_div, self.loop_div)
    '''

    '''

    def on_pressed(self, btn):
        if not self.is_selecteded:
            print('first')
            self.is_selecteded = True
        else:
            if not self.selected_end:
                ele = self._focused_item()
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
        '''



if __name__ == "__main__":

    def pprint(p, sep='-'):
        print(sep*string_size(str(p))[0])
        print(p)
        print(sep*string_size(str(p))[0])


    box = [16, 2]

    app = Menu(name='app', box=box, align_h=1, align_v=0)
    app.loop = True

    welcome = Menu(name='welcome', direction=1, box=[16, 3],
        cursor_pos=[11, 1], items=['Welcome', 'Turntable'],
        align_h=1, align_v=1)
    #welcome.offset = 3
    #pprint(welcome.cursor_pos)

    pprint(app)
    pprint(welcome)
    pprint(welcome.cursor_display())
    #pprint(welcome)
    #app.items = [welcome]