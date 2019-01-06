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


def get_align_offset(string, box, align=[ALIGN_LEFT, ALIGN_TOP]):
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
    center_x = float(align[0])*float(delta[0])/2.0
    center_y = float(align[1])*float(delta[1])/2.0

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

def pos_align_move(pos, string, size, offset, align, loop):
    align_offset = get_align_offset(string, size, align=align)
    offset = [offset[0] + align_offset[0] + pos[0], offset[1] + align_offset[1] + pos[1]]
    if loop:
        offset = get_loop_offset(offset, size)
    return offset

class App():

    def __init__(self, menu=None):
        self.menu = menu


    def __str__(self):
        return str(self.menu)

    @property
    def focus(self):
        return self.menu.focus

    @focus.setter
    def focus(self, focus):
        self.menu.focus = focus

    def cursor(self):
        return self.menu.cursor_display(pos=True)

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


class Action():

    def __init__(self, action, trigger=None, args=(), kwargs={}):
        self.trigger = trigger
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def do(self, *args, **kwargs):
        args += self.args
        kwargs.update(self.kwargs)
        return self.action(*args, **kwargs)

    def check(self, trigger):
        if trigger == self.trigger:
            return True

    def check_do(self, trigger, *args, **kwargs):
        if self.check(trigger):
            self.do(*args, **kwargs)



class Box():
    def __init__(self, txt='', size=[0,0], cursor=True, cursor_pos=[0,0] ,auto_size=True, align=[ALIGN_CENTER, ALIGN_CENTER], loop=False, offset=[0,0], parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._txt = str(txt)
        self._size = size
        self.auto_size = auto_size
        self.align = align
        self.offset = offset
        self.loop = loop
        self.parent = parent
        self.cursor = cursor
        self._cursor_pos = cursor_pos

    def __str__(self):
        return self.txt

    @property
    def size(self):
        if self.auto_size:
            try:
                try:
                    return self.parent.item_size_request(self)
                    #print('Size: Request')
                except:
                    #print('Size: Parent')
                    return self.parent.size
            except:
                try:
                    #print('Size: Self')
                    return string_size(self._txt)
                except:
                    pass
        return self._size

    @size.setter
    def size(self, size):
        self._size = size

    @property
    def txt(self):
        return self.string_align_move(self._txt, self.size, [-self.offset[0], -self.offset[1]], self.align, self.loop)

    @txt.setter
    def txt(self, txt):
        self._txt = str(txt)

    @property
    def cursor_pos(self):
        return self.pos_align_move([self._cursor_pos[0], self._cursor_pos[1]], self._txt, self.size, [self.offset[0], self.offset[1]], self.align, self.loop)

    @cursor_pos.setter
    def cursor_pos(self, pos):
        self._cursor_pos = pos

    @staticmethod
    def get_align_offset(string, size, align):
        """Returns the positional offset of aligning a string inside a box

        Parameters:
            string (str): String to align
            box (list): List of int [width, height] Box size
            align (list): list of int

        Returns:
            list: List of int [x, y]

        """

        str_list = string.split('\n')
        str_size = string_size(string)
        delta = [-size[0]+str_size[0], -size[1]+str_size[1]]
        center_x = float(align[0])*float(delta[0])/2.0
        center_y = float(align[1])*float(delta[1])/2.0

        return [round(center_x), round(center_y)]

    @staticmethod
    def get_loop_offset(pos, size):
        """Returns a position looped around a box

        Parameters:
            pos (list): List of int [x, y] Position
            box (list): List of int [width, height]

        Returns:
            list: List of int [x, y]

        """

        return [pos[0] % size[0], pos[1] % size[1]]

    @staticmethod
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

    @staticmethod
    def string_move(string, size, offset, loop, filler=' '):
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
        for row in range(size[1]):
            for col in range(size[0]):
                char_offset = [col+offset[0], row+offset[1]]
                if loop:
                    char_offset = get_loop_offset(char_offset, size)
                new_str += get_char_at_pos(string, char_offset, filler=filler)
            if row < size[1]-1:
                new_str += '\n'

        return new_str

    @staticmethod
    def string_align_move(string, size, offset, align, loop, filler=' '):
        """Align and position a string in relation to a size 

        Parameters:
            string (str):
            size (list): list of int [widht, height]
            offset (list): list of int [x, y]
            align_h (int): range(0-2)
            align_v (int): range(0-2)
            loop (bool): True if string is looping
            filler (str): Single character for filling. Space by default

        Returns:
            str: Aligned and moved string

        """

        # calculate offset
        align_offset = get_align_offset(string, size, align=align)
        offset = [offset[0] + align_offset[0], offset[1] + align_offset[1]]
        # apply offset
        return string_move(string, size, offset, loop, filler=filler)

    @staticmethod
    def pos_align_move(pos, string, size, offset, align, loop):
        align_offset = get_align_offset(string, size, align=align)
        offset = [offset[0] + align_offset[0] + pos[0], offset[1] + align_offset[1] + pos[1]]
        if loop:
            offset = get_loop_offset(offset, size)
        return offset

    def downstream_cursor_pos(self):
        pass


class Label(Box):

    def __init__(self, txt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.txt = txt


class ActionReady():

    def __init__(self, actions=[], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.actions = actions

    def check(self, trigger):
        for action in self.actions:
            if action.check(trigger):
                return True

    def do(self):
        for action in self.actions:
            action.do(self)

    def check_do(self, trigger):
        for action in self.actions:
            action.check_do(trigger, self)


class PushButton(Box, ActionReady):

    def __init__(self, label='', *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_label(label)

    def __str__(self):
        self.txt = str(self.label)
        return self.txt

    def set_label(self, label):
        if isinstance(label, Label):
            self.label = label
        else:
            self.label = Label(label)

class Items():
    def __init__(self, items, index=0, loop=False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._items = []
        self.items = items
        self._index = index
        self.loop = loop

    @property
    def index(self):
        if self.loop:
            return self._index % len(self.items)
        else:
            return max(min(self._index, len(self.items)-1), 0)

    @index.setter
    def index(self, index):
        self._index = index


    @property
    def items(self):
        for item in self._items:
            item.parent = self
        return self._items

    @items.setter
    def items(self, items):
        #self._items = items
        new_items = []
        for item in items:
            if isinstance(item, Box):
                new_items.append(item)
            else:
                new_item.append(Label(label))
            item.parent = self
        self._items = new_items


    def first(self):
        self.index = 0
        return self.index

    def last(self):
        self.index = len(self.items)-1
        return self.index

    def next(self):
        self.index = self.index + 1
        return self.index

    def prev(self):
        self.index = self.index - 1
        return self.index

    def select_item(self, item):
        self.index = self.items.find(item)

    def selected_item(self):
        return self.items[self.index]


class ItemsMenu(Items, Box):

    def __init__(self, *args, orient=VERTICAL, div=Label(''), loop_div=Label(''), **kwargs):
        print(args)
        super().__init__(*args, **kwargs)
        self.orient = orient
        self._div = div
        self._loop_div = loop_div

    def __str__(self):
        self.txt = str(self._orient_items(
                                    self.items,
                                    self.size,
                                    self.orient,
                                    self.loop,
                                    self.align,
                                    self.div,
                                    self.loop_div))
        return self.txt

    @property
    def div(self):
        if isinstance(self._div, Box):
            self._div.parent = self
            return self._div
        else:
            div = Label(self._div)
            div.parent = self
            return div

    @property
    def loop_div(self):
        if isinstance(self._loop_div, Box):
            self._loop_div.parent = self
            return self._loop_div
        else:
            div = Label(self._loop_div)
            div.parent = self
            return div

    def item_size_request(self, item):
        item_size = string_size(str(item._txt))
        orient_max = [max(size) for size in zip(item_size, self.size)]

        if self.orient == VERTICAL:
            return [orient_max[0], item_size[1]]
        if self.orient == HORIZONTAL:
            return [item_size[0], orient_max[1]]
        return self.size

    @staticmethod
    def axis(direction):
        return [direction == HORIZONTAL,
                direction == VERTICAL]

    @staticmethod
    def _items_insert_divs(items, item_div, loop_div, loop):
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
                if len(item_div._txt) > 0:
                    complete_list.append(item_div)

        if loop == True:
            # Insert loop dividier
            if len(loop_div._txt) > 0:
                complete_list.append(loop_div)

        return complete_list

    @staticmethod
    def _orient_items(items, size, orient, loop, align, item_div, loop_div):
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
        axis = ItemsMenu.axis(orient)

        # Calculate if loop div is needed
        if loop:
            items_div = ItemsMenu._items_insert_divs(items, item_div, loop_div, False)
            sizes = [item.size for item in items_div]
            sizes_summed = [sum(i) for i in zip(*sizes)]
            items_length = sum(prod_iters(axis, sizes_summed))
            box_length = sum(prod_iters(axis, size))
            if items_length <= box_length:
                loop = False

        # string
        items = ItemsMenu._items_insert_divs(items, item_div, loop_div, loop)
        strings = [str(item) for item in items]
        ordered_strings = strings

        if orient == HORIZONTAL:
            # Re orient
            new_string = ''
            ordered_strings = []
            for row in range(size[1]):
                cols=''
                for string in strings:
                    if string:
                        str_list=string.split('\n')
                        cols += str_list[row]
                ordered_strings.append(cols)

        return '\n'.join(ordered_strings)


class ItemsChoice(Items, Box):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def __str__(self):
        self.txt = str(self.selected_item())
        return self.txt




class Menu(object):

    def __init__(self, name='', box=[16, 2], auto_size=False,
                 parent=None, items=[], loop=False, selected_end=True,
                 cursor_pos=[0, 0],
                 direction=HORIZONTAL, align_h=ALIGN_LEFT, align_v=ALIGN_TOP,
                 item_div='', loop_div='  ', auto_box=True, sub=[]):
        # Hidden
        self._cursor_pos = [0, 0]
        self._items = []
        self._index = 0
        self._selected = None
        self._parent = None
        self._focused_item = None
        self.auto_box = auto_box

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
        self.offset = [0,0]

        self.actions = []

        self.item_div = item_div
        self.loop_div = loop_div

        if self.auto_box:
            self.set_box_to_content()

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
        ordered_strings = strings

        if direction == HORIZONTAL:
            new_string=''
            ordered_strings=[]
            for row in range(items_box[1]):
                cols=''
                for string in strings:
                    str_list=string.split('\n')
                    cols += str_list[row]
                ordered_strings.append(cols)
        pprint(ordered_strings)
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
        #offset = prod_iters(axis, [offset]*2)
        #print(offset)

        return string_move(content, box, offset, loop)


    ###########################################################################
    # Properties
    ###########################################################################


    @property
    def items(self):
        return self._items

    @items.setter
    def items(self, items):
        for item in items:
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
        item_div = string_move(' ', string_size(self.item_div), [0, 0], False, filler=' ')
        loop_div = string_move(' ', string_size(self.item_div), [0, 0], False, filler=' ')
        display = ''

        if not self.items:
            char = ' '
            if self.parent_topmost().focus == self:
                char = '1'
            # does look useful
            pos_invert = [-self.cursor_pos[0], -self.cursor_pos[1]]
            display = string_move(char, self.box, pos_invert, False, filler=' ')
        else:
            # generate from items 
            items = []
            for item in self.items:
                if item == self.selected():
                    char = ' '
                    if self.parent_topmost().focus == self:
                        char = '1'
                    else:
                        if isinstance(item, Menu):
                            # go deeper
                            items.append(item.cursor_display())
                            continue
                    pos_invert = [-self.cursor_pos[0], -self.cursor_pos[1]]
                    string = string_move(char, string_size(str(item)), pos_invert, False, filler=' ')
                    items.append(string)
                else:
                    # blank for unselected
                    items.append(string_move(' ', string_size(str(item)), [0, 0], False, filler=' '))

            content_moved = self._items_content_moved(
                items, self.box, self.offset, self.direction, self.loop,
                self.align_h, self.align_v, item_div, loop_div)
            align_pos = get_align_offset(content_moved, self.box, hor=self.align_h, vert=self.align_v)
            display = string_move(content_moved, self.box, align_pos, False)

        if pos:
            return find_char_pos(display, '1')
        else:
            return display


    def selected_pos(self):
        items = []
        for item in self.items:
            char = ' '
            if item == self.selected():
                char = '1'
            items.append(string_move(char, string_size(str(item)), [0, 0], False, filler=' '))

        content = self._items_content(items, self.box, self.direction, self.loop,
                                   self.align_h, self.align_v,
                                   self.item_div, self.loop_div)
        offset = find_char_pos(content, '1')
        if offset:
            return offset
        return [0, 0]


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
        self.offset = self.selected_pos()

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

    #def selected_parent_topmost(self):
    #    self.selected = self.parent_topmost

    def check_actions(self, trigger):
        for action in self.actions:
            action.check(trigger, self)


if __name__ == "__main__":

    def pprint(p, sep='-'):
        print(sep*string_size(str(p))[0])
        print(p)
        print(sep*string_size(str(p))[0])

    def print_fct(widget, txt):
        print('print_fct: ', txt, widget.__repr__())
    print_action = Action(trigger='DOWN', action=print_fct, args=('Malade', ))

    welcome = Label('welcome')
    welcome.offset = [5,0]
    welcome.loop = True
    pprint(welcome._txt)
    #pprint(b.size)

    print(' ')
    pprint('welcome: {}'.format(welcome))
    home = PushButton(label='home', actions=[print_action], align=[ALIGN_LEFT, ALIGN_TOP])
    friend = PushButton(label='my friend', actions=[print_action])
    #items = Items([welcome, home, friend])

    choice = ItemsChoice([welcome, home, friend], size=[8, 3], auto_size=False)
    pprint(choice)
    choice.next()
    pprint(choice)
    choice.next()
    pprint(choice)
    print(welcome.parent)
    choice.selected_item().do()

    pprint(welcome._txt)
    pprint(home._txt)
    pprint(friend._txt)
    menu = ItemsMenu([welcome, home, friend],
                    size=[16, 3],
                    auto_size=False,
                    orient=0,
                    div=' ',
                    loop_div='',
                    loop=True)
    print('DIV: ', menu.div)
    for item in menu.items:
        pprint(item)
    pprint(menu)
    menu.offset = [-8,1]
    pprint(menu)
    pprint(friend)
    pprint(friend.cursor_pos)
    friend.offset = [0,0]
    pprint(friend)
    pprint(friend.cursor_pos)
    friend.cursor_pos = [4,0]
    pprint(friend)
    pprint(friend.cursor_pos)

    friend.offset = [-2,0]
    pprint(friend)
    pprint(friend.cursor_pos)