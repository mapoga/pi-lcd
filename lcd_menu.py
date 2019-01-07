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

def get_loop_offset(pos, size):
    """Returns a position looped around a box

    Parameters:
        pos (list): List of int [x, y] Position
        box (list): List of int [width, height]

    Returns:
        list: List of int [x, y]

    """

    return [pos[0] % size[0], pos[1] % size[1]]

def pos_align_move(pos, string, size, offset, align, loop):
    align_offset = get_align_offset(string, size, align=align)
    offset = [offset[0] + align_offset[0] + pos[0], offset[1] + align_offset[1] + pos[1]]
    if loop:
        offset = get_loop_offset(offset, size)
    return offset

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


class App():

    def __init__(self, menu=None):
        self.menu = menu
        self.selected = menu


    def __str__(self):
        return str(self.menu)

    def cursor(self):
        return self.menu.cursor_display(pos=True)


    '''
    @property
    def focus(self):
        return self.menu.focus

    @focus.setter
    def focus(self, focus):
        self.menu.focus = focus
    
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
    '''


class Action():

    def __init__(self, action, triggers=[], args=(), kwargs={}):
        self.triggers = triggers
        self.action = action
        self.args = args
        self.kwargs = kwargs

    def do(self, *args, **kwargs):
        args += self.args
        kwargs.update(self.kwargs)
        return self.action(*args, **kwargs)

    def check(self, trigger):
        if trigger in self.triggers:
            return True

    def check_do(self, *args, **kwargs):
        if self.check(kwargs['trigger']):
            self.do(*args, **kwargs)



class Box():
    def __init__(self, txt='', size=[0,0], above=None, under=None, cursor=True, cursor_pos=[0,0] ,auto_size=True, align=[ALIGN_CENTER, ALIGN_CENTER], loop=False, offset=[0,0], parent=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._txt = txt
        self._size = size
        self.auto_size = auto_size
        self.align = align
        self.offset = offset
        self.loop = loop
        self.parent = parent
        self.above = above
        self._under = under
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
    def under(self):
        return self._under

    @under.setter
    def under(self, under):
        self._under = under
        self.under.above = self

    @property
    def txt(self):
        return string_align_move(str(self._txt), self.size, [-self.offset[0], -self.offset[1]], self.align, self.loop)

    @txt.setter
    def txt(self, txt):
        self._txt = txt

    @property
    def cursor_pos(self):
        return self.process_pos(self._cursor_pos)

    @cursor_pos.setter
    def cursor_pos(self, pos):
        self._cursor_pos = pos

    def bounds(self):
        size = string_size(self._txt)
        bottom_right = [size[0]-1, size[1]-1]
        return self.process_pos([0,0], bottom_right)

    def process_pos(self, *pos):
        new_pos = []
        for p in pos:
            new_pos.append(pos_align_move(p, self._txt, self.size, self.offset, self.align, self.loop))
        return list(*new_pos)



class Label(Box):

    def __init__(self, txt, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.txt = txt


class ActionReady():

    def __init__(self, actions=[], *args, **kwargs):
        #super().__init__(*args, **kwargs)
        self.actions = actions

    def check(self, trigger):
        for action in self.actions:
            if action.check(trigger):
                return True
        return False

    def do(self):
        for action in self.actions:
            action.do(menu=self, )

    def check_do(self, trigger=None):
        for action in self.actions:
            action.check_do(trigger=trigger, menu=self)


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
    def __init__(self, items=[], index=0, loop=False, *args, **kwargs):
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
        self.update_offset()


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

    def update_offset(self):
        pass

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


class ItemsMenu(Items, Box, ActionReady):

    def __init__(self, *args, orient=VERTICAL, div=Label(''), loop_div=Label(''), **kwargs):
        super().__init__(*args, **kwargs)
        self.orient = orient
        self._div = div
        self._loop_div = loop_div


    @property
    def txt(self):
        txt = str(self._orient_items(
                                    self.items,
                                    self.size,
                                    self.orient,
                                    self.loop,
                                    self.align,
                                    self.div,
                                    self.loop_div))
        return string_align_move(txt, string_size(txt), self.offset, self.align, self.loop)


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
    def needs_loop(items, size, orient, loop, item_div):
        axis = ItemsMenu.axis(orient)
        # Calculate if loop div is needed
        if loop:
            items_div = ItemsMenu._items_insert_divs(items, item_div, Label(''), False)
            sizes = [item.size for item in items_div]
            sizes_summed = [sum(i) for i in zip(*sizes)]
            items_length = sum(prod_iters(axis, sizes_summed))
            box_length = sum(prod_iters(axis, size))
            if items_length <= box_length:
                loop = False
        return loop

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

        loop = ItemsMenu.needs_loop(items, size, orient, loop, item_div)

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

    def update_offset(self):
        offset = [0, self.index]
        #print(offset)
        loop = ItemsMenu.needs_loop(self.items, self.size, self.orient, self.loop, self.div)
        items = ItemsMenu._items_insert_divs(self.items, self.div, self.loop_div, loop)
        index = items.index(self.selected_item())
        axis = ItemsMenu.axis(self.orient)

        # Offset at selected item position
        offset = [0,0]
        for i in range(index):
            item = self.items[i]
            if i < index:
                offset = [offset[0]+item.size[0], offset[1]+item.size[1]]
        self.offset = prod_iters(axis, offset)

        # Check if empty space at the end and get back a little
        if not self.loop:
            self_size = prod_iters(axis, self.size)
            self_length = sum(self_size)

            items_sizes = [i.size for i in items]
            items_sizes_sum = [sum(i) for i in zip(*items_sizes)]
            items_length = sum(prod_iters(axis, items_sizes_sum))

            item_size = prod_iters(axis, self.selected_item().size)
            item_length = sum(item_size)
            remain = items_length - (sum(self.offset))

            if remain < self_length:
                if items_length >= self_length:
                    self.offset = [axis[0]*(items_length-self_length), axis[1]*(items_length-self_length)]


        print(self.offset)


class ItemsChoice(Items, Box, ActionReady):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


    def __str__(self):
        self.txt = str(self.selected_item())
        return self.txt



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
    for i in range(15):
        menu.offset = [menu.offset[0]+1, menu.offset[1]]
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
    pprint(friend.bounds())