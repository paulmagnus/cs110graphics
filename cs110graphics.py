## @package cs110graphics
# Contains a CSPy-friendly version of a Tkinter based graphics library.
#
# Paul Magnus '18, Ines Ayara '20, Matthew R. Jenkins '20
#
# Summer 2017
from tkinter import *  # for pretty much everything graphics related
import math  # for rotate
import inspect
from PIL import Image as image  # for Image class
from PIL import ImageTk as itk  # for Image class

## This window acts as a canvas which other objects can be put onto.
#
# Required Parameters:
# - width - int - Width of canvas.
# - height - int - Height of canvas.
# - background - str - Background color of canvas. Can be either the name of a
#color ("yellow"), or a hex code ("#FFFF00").
# - name - str - The title of the window.
# - first_function - proc(Window) - When the window is created, it runs this
# function after everything is run. (default: None)
# - master - unknown type - necessary for the creation of the Tkinter widgets. 
# (default: None)
class Window:
    def __init__(self, width, height, background, name, first_function=None,
                 master=None):
        # type checking
        assert isinstance(width, int) and isinstance(height, int) and \
            isinstance(background, str) and isinstance(name, str), \
            "Make sure width is an int, height is an int, background is a " + \
            "string, and name is a string."
        # saving the given variables
        self._width = width
        self._height = height
        self._background = background
        self._name = name
        self._first_function = first_function
        # self._graphics contains a running tally of what objects are on the
        # canvas
        # [0] = depth, [1] = tag, [2] = object ID
        self._graphics = []
        # initalizing a frame and canvas using tkinter
        self._root = Tk()
        self._frame = Frame(master)
        self._frame.pack()
        self._canvas = Canvas(self._frame)
        self._canvas.pack()
        self._canvas.focus_set()
        # using our built in functions to set height, width, and background
        self.set_height(height)
        self.set_width(width)
        self.set_title(name)
        self.set_background(background)
        # running first function
        self._first_function(self)

    ## Adds an object of type GraphicalObject to the Window object.
    # Required Parameters:
    # - graphic - GraphicalObject
    def add(self, graphic):
        # type checking
        assert isinstance(graphic, GraphicalObject), \
            "Make sure graphic is a GraphicalObject."
        # deferring to each object since each object requires a different
        # method of construction
        graphic._add_to()

    ## Removes an object of type GraphicalObject to the Window object, assuming
    # the object being deleted exists.    
    # Required Parameters:
    # - graphic - GraphicalObject
    def remove(self, graphic):
        # type checking and making sure the object is in the list
        assert isinstance(graphic, GraphicalObject) and \
            [graphic._depth, graphic._tag, graphic] in self._graphics, \
            "Make sure graphic is a GraphicalObject and the graphic has " + \
            "been added to the board."
        # removes from the window, then the list, then sets the tag to None and
        # disables the object (for readding later)
        graphic._remove_from(self)
        self._graphics.remove([graphic._depth, graphic._tag, graphic])
        graphic._tag = None
        graphic._enabled = False

    ## Returns the height of the window as an integer.
    def get_height(self):
        return self._height

    ## Returns the width of the window as an integer.
    def get_width(self):
        return self._width

    ## Sets the background color of the canvas.
    # Required Parameters:
    # - background - string
    def set_background(self, background):
        # type checking
        assert isinstance(background, str), \
            "Make sure the background color is a string."
        self._background = background
        self._canvas.configure(bg=background)

    ## Sets the height of the canvas.
    # Required Parameters:
    # - height - int
    def set_height(self, height):
        # type checking
        assert isinstance(height, int), \
            "Make sure the height is an int."
        self._height = height
        self._canvas.configure(height=height)

    ## Sets the title of the window holding the canvas.
    # Required Parameters:
    # - name - string
    def set_title(self, name):
        # type checking
        assert isinstance(name, str), \
            "Make sure the window title is a string."
        self._name = name
        self._root.title(name)

    ## Sets the width of the canvas.
    # Required Parameters:
    # - width - height
    def set_width(self, width):
        # type checking
        assert isinstance(width, int), \
            "Make sure the width is an int."
        self._width = width
        self._canvas.configure(width=width)

    # Whenever an object is updated through external functions, its tag is
    # overwritten. This function goes into self._graphics and replaces the old
    # tag with a newer one, as well as replacing its depth with a newer one.
    def _update_tag(self, graphic):
        # goes through every item in self._graphics, then saves the object's
        # tag and depth if it's found
        for item in self._graphics:
            if item[2] == graphic:
                item[1] = graphic._tag
                item[0] = graphic._depth


## This initalizes the graphics system.
#
# Required Parameters:
# - first_function - func
#
# Optional Parameters:
# - width - int
# - height - int
# - background - string
# - name - string
def StartGraphicsSystem(first_function, width=400, height=400,
                        background="white", name="Graphics Window"):
    # creates a window with each parameter
    win = Window(width, height, background, name, first_function)
    # this emulates a mainloop tkinter instance, and allows for quieter
    # exception handling. it still won't handle tk.afters too well. TODO
    try:
        while True:
            win._canvas.update()
            win._canvas.after(200)
    except TclError:
        pass


## An event which gets bound to an object. Used by EventHandler objects.
#
# Required Parameters:
# - event - TkEvent - The event which the user want applied an an object.
class Event:
    def __init__(self, event):
        # converting each necessary tkinter event parameter to something easier
        # to get access to and easier to understand
        self._type = event.type
        self._location = (event.x, event.y)
        self._rootLocation = (event.x_root, event.y_root)
        self._keysym = event.keysym
        self._num = event.num

    ## Returns the mouse button that is attached to the event. Returns None if
    # the button fails to exist (like if the Event handles a key press).
    def get_button(self):
        # this is mostly to handle user stupidity - why would you put
        # get_button in a handle_key function if get_key exists?
        if self._num == "??":
            return None
        # dictionary to translate each number to a string
        numTranslation = {
            1: "Left Mouse Button",
            2: "Middle Mouse Button",
            3: "Right Mouse Button"
        }
        return numTranslation[self._num]

    ## Returns the description of the event.
    def get_description(self):
        # dictionary to translate each number to a string
        descriptionTranslation = {
            '2': "Key Press",
            '3': "Key Release",
            '4': "Mouse Press",
            '5': "Mouse Release",
            '6': "Mouse Move",
            '7': "Mouse Enter",
            '8': "Mouse Leave",
        }
        return descriptionTranslation[self._type]

    ## Returns the keyboard key that is attached to the event. Returns None if
    # the key fails to exist (like if the Event handles a mouse press).
    def get_key(self):
        # this is mostly to handle user stupidity - why would you put
        # get_key in a handle_mouse function if get_button exists?
        if self._keysym == "??":
            return None
        return self._keysym

    ## Returns a tuple of the x and y coordinates of the mouse location in the
    # canvas.    
    def get_mouse_location(self):
        return self._location

    ## Returns a tuple of the x and y coordinates of the mouse location in the
    # window.
    def get_root_mouse_location(self):
        return self._rootLocation


## Handles an event. These are overloaded by the user, so by default they're 
# empty except for the pass command.
class EventHandler:
    def __init__(self):
        pass

    ## Handles a key press.
    # Optional Parameters:
    # - event - Event - when included, you can use any Event method whenever
    # this function is run.
    def handle_key_press(self, event):
        pass

    ## Handles a key release.
    # Optional Parameters:
    # - event - Event - when included, you can use any Event method whenever
    # this function is run.
    def handle_key_release(self, event):
        pass

    ## Handles when a mouse enters an object.
    # Optional Parameters:
    # - event - Event - when included, you can use any Event method whenever
    # this function is run.
    def handle_mouse_enter(self, event):
        pass

    ## Handles when a mouse leaves an object.
    # Optional Parameters:
    # - event - Event - when included, you can use any Event method whenever
    # this function is run.
    def handle_mouse_leave(self, event):
        pass

    ## Handles a mouse move.
    # Optional Parameters:
    # - event - Event - when included, you can use any Event method whenever
    # this function is run.
    def handle_mouse_move(self, event):
        pass

    ## Handles a mouse press.
    # Optional Parameters:
    # - event - Event - when included, you can use any Event method whenever
    # this function is run.
    def handle_mouse_press(self, event):
        pass

    ## Handles a mouse release.
    # Optional Parameters:
    # - event - Event - when included, you can use any Event method whenever
    # this function is run.
    def handle_mouse_release(self, event):
        pass


# "Overwrites" the event handler and calls an external EventHandler.
def _call_handler(handler, event):
    # checks if argument count is > 1 and then appends the event to the handler
    # if it is
    arg_count = len(inspect.getargs(handler.__code__)[0])
    if arg_count == 1:
        handler()
    else:
        handler(event)


## This window is a parent class of any object which can be put into Window. No
# constructor exists in this class, but its methods are used by other objects
# that extend/inherit this class.
class GraphicalObject:
    def __init__(self):
        self._depth = 50
        self._center = (200, 200)
        self._has_handlers = False

    ## Adds a handler to the graphical object.
    # Required Parameters:
    # - handler_object - an object with a GraphicalObject representation within
    # it (such as an object which has a Circle object in it)
    def add_handler(self, handler_object):
        def key_press(event):
            tkEvent = Event(event)
            _call_handler(handler_object.handle_key_press, tkEvent)

        def key_release(event):
            tkEvent = Event(event)
            _call_handler(handler_object.handle_key_release, tkEvent)

        def mouse_enter(event):
            tkEvent = Event(event)
            _call_handler(handler_object.handle_mouse_enter, tkEvent)

        def mouse_leave(event):
            tkEvent = Event(event)
            _call_handler(handler_object.handle_mouse_leave, tkEvent)

        def mouse_move(event):
            tkEvent = Event(event)
            _call_handler(handler_object.handle_mouse_move, tkEvent)

        def mouse_press(event):
            tkEvent = Event(event)
            _call_handler(handler_object.handle_mouse_press, tkEvent)

        def mouse_release(event):
            tkEvent = Event(event)
            _call_handler(handler_object.handle_mouse_release, tkEvent)

        # this is to enable readding handlers after each object's tag is
        # changed
        self._parent_object = handler_object
        self._has_handlers = True
        # the duplicates are necessary to allow support for multiple mouse
        # buttons
        types = ["<Key>", "<KeyRelease>", "<Enter>", "<Leave>",
                 "<Motion>", "<Button-1>", "<Button-2>", "<Button-3>",
                 "<ButtonRelease-1>", "<ButtonRelease-2>", "<ButtonRelease-3>"]
        funcs = [key_press, key_release, mouse_enter, mouse_leave, mouse_move,
                 mouse_press, mouse_press, mouse_press,
                 mouse_release, mouse_release, mouse_release]
        # goes through each bind and binds it to canvas if it's a key based
        # object and binds it to the graphical object if it's not a key based
        # object
        for i in range(len(types)):
            if "Key" in types[i]:
                self._window._canvas.bind(types[i], funcs[i])
            else:
                self._window._canvas.tag_bind(self._tag, types[i], funcs[i])

    ## Returns the center of the graphical object.
    def get_center(self):
        return self._center

    ## Returns the depth of the graphical object.
    def get_depth(self):
        return self._depth

    ## Moves a graphical object dx pixels horizontally and dy pixels vertically.
    #
    # Required Parameters:
    # - dx - int
    # - dy - int
    def move(self, dx, dy):
        # type checking
        assert isinstance(dx, int) and isinstance(dy, int), \
            "Make sure dx and dy are both ints."
        self._center = (self._center[0] + dx, self._center[1] + dy)
        # goes through each point and increments it by dx or dy depending if
        # its index is even or odd
        for i in range(len(self._points)):
                self._points[i] = (self._points[i][0] + dx,
                                   self._points[i][1] + dy)
        self._refresh()

    ## Moves a graphical object to a point.
    # Required Parameters:
    # - point - tuple of (int * int)
    def move_to(self, point):
        # type checking
        assert isinstance(point, tuple) and len(point) == 2 and \
            isinstance(point[0], int) and isinstance(point[1], int), \
            "Make sure point is a tuple of (int * int)."
        difference = (self._center[0] - point[0], self._center[1] - point[1])
        self._center = point
        # goes through each point and increments it by dx or dy depending if
        # its index is even or odd
        for i in range(len(self._points)):
                self._points[i] = (self._points[i][0] - difference[0],
                                   self._points[i][1] - difference[1])
        self._refresh()

    ## Removes and adds an object after it's been changed.
    def _refresh(self):
        # since this is run for every object we need a special case if the
        # object is a graphical object and not a fillable
            # in that case, we remove it and readd it without using any canvas
            # operators, add handlers if they exist, and return
        if isinstance(self, Text) or isinstance(self, Image):
            self._remove_from(self._window)
            self._add_to()
            self._window._update_tag(self)
            if self._has_handlers:
                self.add_handler(self._parent_object)
        else:
            # from here on out we're assuming fillables only.
            # we remove the object from the window, and then if the object is
            # disabled we readd it with the HIDDEN state, otherwise just readd
            # it
            self._remove_from(self._window)
            if self._enabled is False:
                self._tag = self._window._canvas.create_polygon(
                    *self._points,
                    width=self.get_border_width(),
                    fill=self.get_fill_color(),
                    outline=self.get_border_color(),
                    state=HIDDEN
                )
            else:
                self._tag = self._window._canvas.create_polygon(
                    *self._points,
                    width=self.get_border_width(),
                    fill=self.get_fill_color(),
                    outline=self.get_border_color()
                )
            # we then update the tag, and then readd handlers if they exist
            # if we don't then the event will only run once and then not again
            self._window._update_tag(self)
            if self._has_handlers:
                self.add_handler(self._parent_object)

    ## Removes a graphical object from the canvas.
    def _remove_from(self, window):
        window._canvas.delete(self._tag)

    ## Sets the depth of the GraphicalObject.
    # Required Parameters:
    # - depth - int
    def set_depth(self, depth):
        # type checking
        assert isinstance(depth, int), \
            "Make sure depth is an int."
        self._depth = depth
        self._window._update_tag(self)
        self._window._graphics.sort()
        # get rid of all objects and readd them in depth order
        for graphic in reversed(self._window._graphics):
            graphic[2]._refresh()


## This window is a parent class of any object which can have its colors
# modified. No constructor exists in this class, but its methods are used by
# other objects that extend/inherit this class.
class Fillable(GraphicalObject):
    def __init__(self):
        GraphicalObject.__init__(self)
        # default values - otherwise when an object is changed later it reverts
        # any changes that were made
        self._border_color = "black"
        self._border_width = 2
        self._fill_color = "white"
        self._pivot = self._center

    ## Returns the border color of a Fillable.
    def get_border_color(self):
        return self._border_color

    ## Returns the border width of a Fillable.
    def get_border_width(self):
        return self._border_width

    ## Returns the depth of a Fillable.
    def get_fill_color(self):
        return self._fill_color

    ## Returns the pivot point of a Fillable.
    def get_pivot(self):
        return self._pivot

    ## Rotates the object.
    # Required Parameters:
    # - degrees - int
    def rotate(self, degrees):
        # type checking
        # print("DEBUG: before rotate: " + str(self._center))
        assert isinstance(degrees, int), \
            "Make sure degrees is an int."
        # calculates radians, runs _rotate_helper, moves back to its center and
        # refreshes
        radians = (math.pi / 180) * degrees
        for i in range(len(self._points)):
            self._points[i] = _rotate_helper(self._points[i],
                                             radians,
                                             self._pivot)
        # print("DEBUG: after rotate: " + str(self._center))
        self.move_to(self._center)
        self._refresh()

    ## Scales the Fillable up or down depending on the factor.
    # Required Parameters:
    # - factor - float
    def scale(self, factor):
        # type checking
        assert isinstance(factor, float), \
            "Make sure the scale factor is a float."
        # saves the center, moves the object to the origin, modifies every
        # point so it's scaled, moves it back to the center and refreshes
        temp_center = self._center
        self.move_to((0, 0))
        for i in range(len(self._points)):
            temp_tuple = (int(self._points[i][0] * factor),
                          int(self._points[i][1] * factor))
            self._points[i] = temp_tuple
        self._pivot = (round(self._pivot[0] * factor),
                       round(self._pivot[1] * factor))
        self.move_to(temp_center)
        self._center = temp_center
        self._refresh()

    def move(self, dx, dy):
        GraphicalObject.move(self, dx, dy)

        # update pivot
        self._pivot = (self._pivot[0] + dx, self._pivot[1] + dy)

    def move_to(self, point):
        difference = (self._pivot[0] - self._center[0],
                      self._pivot[1] - self._center[1])
        
        GraphicalObject.move_to(self, point)

        self._pivot = (self._center[0] + difference[0],
                       self._center[1] + difference[1])

    ## Sets the border color of the Fillable.
    # Required Parameters:
    # - color - string
    def set_border_color(self, color):
        # type checking
        assert isinstance(color, str), \
            "Make sure the border color is a string."
        self._border_color = color
        self._window._canvas.itemconfigure(self._tag, outline=color)

    ## Sets the border width of the Fillable.
    # Required Parameters:
    # - width - int
    def set_border_width(self, width):
        # type checking
        assert isinstance(width, int), \
            "Make sure the border width is an int."
        self._border_width = width
        self._window._canvas.itemconfigure(self._tag, width=width)

    ## Sets the fill color of the Fillable.
    # Required Parameters:
    # - color - string
    def set_fill_color(self, color):
        # type checking
        assert isinstance(color, str), \
            "Make sure the fill color is a string."
        self._fill_color = color
        self._window._canvas.itemconfigure(self._tag, fill=color)

    ## Sets the pivot point of the Fillable.
    # Required Parameters:
    # - pivot - tuple of (int * int)
    def set_pivot(self, pivot):
        # type checking
        assert isinstance(pivot, tuple) and len(pivot) == 2 and \
            isinstance(pivot[0], int) and isinstance(pivot[1], int), \
            "Make sure the pivot is a tuple of (int * int)."
        self._pivot = pivot


# Aids in rotation.
def _rotate_helper(point, angle, pivot):
    # type checking
    # print("DEBUG: point = " + str(point) + ", angle = " + str(angle) + ", pivot = " + str(pivot))
    assert isinstance(point, tuple) and len(point) == 2 and \
        isinstance(angle, float) and isinstance(pivot, tuple) and \
        len(pivot) == 2 and isinstance(point[0], int) and \
        isinstance(point[1], int) and isinstance(pivot[0], int) and \
        isinstance(pivot[1], int), \
        "Make sure point is a tuple of (int * int), angle is a float, " + \
        "and pivot is a tuple of (int * int)."
    point = (point[0] - pivot[0], point[1] - pivot[1])
    newX = round(point[0] * math.cos(angle) + point[1] * math.sin(angle))
    newY = round(point[1] * math.cos(angle) - point[0] * math.sin(angle))
    return (newX + pivot[0], newY + pivot[1])


## An image, which can be added to a Window object.
#
# Required Parameters:
# - window - Window - the window which the object will be added to.
# - image_loc - str - The name of an image within the current working directory.
# (If the current working directory is /foo/bar, then the image the user wants
# to use has to be in that directory. There is no support for using internet
# links at this time.)
#
# Optional Parameters:
# - center - tuple of int * int - sets the center of the Image. (default: (200,
# 200))
# - width - int - sets the width of the image. (default: 25)
# - height - int - sets the height of the image. (default: 25)
class Image(GraphicalObject):
    def __init__(self, window, image_loc, width=100, height=100,
                 center=(200, 200)):
        # type checking
        assert isinstance(window, Window) and image_loc is not "" \
            and isinstance(width, int) and isinstance(height, int) \
            and isinstance(center, tuple) and len(center) == 2 and \
            isinstance(center[0], int) and isinstance(center[1], int), \
            "Make sure window is a Window, image location is not blank, " + \
            "width is an int, height is an int, and center is a tuple of " + \
            "(int * int)."
        # setting up inheritance
        GraphicalObject.__init__(self)
        # saving variables
        self._window = window
        self._image_loc = "./" + image_loc
        self._center = center
        self._width = width
        self._height = height
        # necessary for rotation - it's handled differently than the default
        # rotate function
        self._angle = 0
        # generating image based on image location
        self._img = _image_gen(self._image_loc, self._width, self._height)
        # creating object as hidden and adding it to window._graphics
        self._enabled = False
        self._tag = self._window._canvas.create_image(self._center[0],
                                                      self._center[1],
                                                      image=self._img,
                                                      state=HIDDEN)
        self._window._graphics.append([self._depth, self._tag, self])

    ## Adds a graphical object to the canvas.

    def _add_to(self):
        self._tag = self._window._canvas.create_image(self._center[0],
                                                      self._center[1],
                                                      image=self._img)
        self._enabled = True

        self._window._update_tag(self)

    ## Moves a graphical object dx pixels horizontally and dy pixels vertically.
    # Required Parameters:
    # - dx - int
    # - dy - int
    def move(self, dx, dy):
        # type checking
        assert isinstance(dx, int) and isinstance(dy, int), \
            "Make sure dx and dy are both ints."
        self._center = (self._center[0] + dx, self._center[1] + dy)
        self._remove_from(self._window)
        self._img = _image_gen(self._image_loc, self._width, self._height)
        self._refresh()

    ## Moves a graphical object to a point.
    # Required Parameters:
    # - point - tuple of (int * int)
    def move_to(self, point):
        # type checking
        assert isinstance(point, tuple) and len(point) == 2 and \
            isinstance(point[0], int) and isinstance(point[1], int), \
            "Make sure point is a tuple of (int * int)."
        self._center = point
        self._remove_from(self._window)
        self._img = _image_gen(self._image_loc, self._width, self._height)
        self._refresh()

    ## Resizes the Image.
    # Required Parameters:
    # - width - int
    # - height - int
    def resize(self, width, height):
        # type checking
        assert isinstance(width, int) and isinstance(height, int), \
            "Make sure width and height are both ints."
        self._width = width
        self._height = height
        # depending on if the object is rotated or not, it will either be
        # re-rotated at whatever self._angle is, or it will be removed and
        # readded
        if self._angle != 0:
            self.rotate(0)
        else:
            self._remove_from(self._window)
            self._img = _image_gen(self._image_loc, width, height)
            self._refresh()

    ## Rotates an object by degrees.
    # Required Parameters:
    # - degrees - int
    def rotate(self, degrees):
        # type checking
        assert isinstance(degrees, int), \
            "Make sure degrees is an int."
        # adds degrees to angle, checks whether angle >= 360 and modulos it if
        # it is
        self._angle += degrees
        if self._angle >= 360:
            self._angle = self._angle % 360
        # removes object from window, converts it to a format which can be
        # rotated, resizes it, then rotates it, makes a photo image,
        # and refreshes it
        # this needs a special version of _image_gen since we're handling
        # rotation. _image_gen doesn't handle rotation.
        self._remove_from(self._window)
        img_temp = image.open(self._image_loc)
        img_temp = img_temp.convert('RGBA')
        img_temp = img_temp.resize((self._width, self._height),
                                   image.ANTIALIAS)
        img_temp = img_temp.rotate(self._angle)
        self._img = itk.PhotoImage(img_temp)
        self._refresh()

    ## Scales the image according to the factor.
    # Required Parameters:
    # - factor - float
    def scale(self, factor):
        # type checking
        assert isinstance(factor, float), \
            "Make sure the scale factor is a float."
        self._width = int(self._width * factor)
        self._height = int(self._height * factor)
        # depending on whether the object is rotated, resize or rotate is run
        # with the new width and height values saved
        if self._angle != 0:
            self.rotate(self._angle)
        else:
            self.resize(self._width, self._height)

    ## Returns a tuple of the width and height of the image.
    def size(self):
        return (self._width, self._height)


# Creates a resized image and returns an image of type itk.PhotoImage.
def _image_gen(image_loc, width, height):
    # opens and resizes an object based on the width and height
    img_temp = image.open(image_loc)
    img_temp = img_temp.resize((width, height), image.ANTIALIAS)
    return itk.PhotoImage(img_temp)


## Text which can be added to a Window object.
#
# Required Parameters:
# - window - Window - the window which the object will be added to.
# - text - str - The text which is displayed.
#
# Optional Parameters:
# - center - tuple of int * int - sets the center of the Image. (default: (200,
# 200))
# - width - int - sets the size of the text. (default: 12)
class Text(GraphicalObject):
    def __init__(self, window, text, size=12, center=(200, 200)):
        # type checking
        assert isinstance(window, Window) and isinstance(size, int) \
            and isinstance(center, tuple) and len(center) == 2 and \
            isinstance(center[0], int) and isinstance(center[1], int), \
            "Make sure the window is a Window, the size is an int, and " + \
            "the center is a tuple of (int * int)."
        # for inheritance
        GraphicalObject.__init__(self)
        # setting variables, creating object and adding it to window._graphics
        self._window = window
        self._text = text
        self._center = center
        self._size = size
        self._enabled = False
        self._tag = self._window._canvas.create_text(self._center[0],
                                                     self._center[1],
                                                     text=str(self._text),
                                                     font=("Helvetica",
                                                           self._size),
                                                     state=HIDDEN)
        self._window._graphics.append([self._depth, self._tag, self])

    ## Adds a graphical object to the canvas.
    def _add_to(self):
        self._tag = self._window._canvas.create_text(self._center[0],
                                                     self._center[1],
                                                     text=str(self._text),
                                                     font=("Helvetica",
                                                           self._size))
        self._enabled = True

        self._window._update_tag(self)

    ## Moves a graphical object dx pixels horizontally and dy pixels vertically.
    # Required Parameters:
    # - dx - int
    # - dy - int
    def move(self, dx, dy):
        # type checking
        assert isinstance(dx, int) and isinstance(dy, int), \
            "Make sure dx and dy are both ints."
        self._center = (self._center[0] + dx, self._center[1] + dy)
        # text is special because it does not need to be recreated after each
        # modification
        self._window._canvas.coords(self._tag,
                                    (self._center[0], self._center[1]))

    ## Moves a graphical object to a point.
    # Required Parameters:
    # - point - tuple of (int * int)
    def move_to(self, point):
        assert isinstance(point, tuple) and len(point) == 2 and \
            isinstance(point[0], int) and isinstance(point[1], int), \
            "Make sure point is a tuple of (int * int)."
        self._center = point
        # text is special because it does not need to be recreated after each
        # modification
        self._window._canvas.coords(self._tag,
                                    self._center[0],
                                    self._center[1])

    ## Sets the point size of the text.
    # Required Parameters:
    # - size - int
    def set_size(self, size):
        assert isinstance(size, int), \
            "Make sure size is an int."
        self._size = size
        # text is special because it does not need to be recreated after each
        # modification
        self._window._canvas.itemconfigure(self._tag, font=("Helvetica",
                                                            self._size))

    ## Sets the text.
    # Required Parameters:
    # - text - string
    def set_text(self, text):
        assert isinstance(text, str), \
            "Make sure text is a string."
        self._text = text
        # text is special because it does not need to be recreated after each
        # modification
        self._window._canvas.itemconfigure(self._tag, text=self._text)


## A Polygon, which can be added to a Window object.
#
# Required Parameters:
# - window - Window - the window which the object will be added to.
# - points - list of tuples of int * int - each tuple corresponds to an xy
#point.
class Polygon(Fillable):
    def __init__(self, window, points):
        # type checking
        assert isinstance(window, Window) and isinstance(points, list), \
            "Make sure window is a Window and points is a list of tuples " + \
            "of (int * int)."
        # checking whether each point in the list of points is a tuple of
        # length 2
        for point in points:
            if len(point) is not 2 or type(point[0]) != int or \
               type(point[1]) != int:
                raise AssertionError("One of the points in your polygon " +
                                     "does not have a length of two." +
                                     "Make sure every tuple in your list " +
                                     "has a length of two.")
        # establishing inheritance
        Fillable.__init__(self)
        # setting all variables, creating object, and adding it to
        # window._graphics
        self._window = window
        self._points = points
        self._center = _list_average(self._points)
        self._pivot = self._center
        self._enabled = False
        self._tag = self._window._canvas.create_polygon(
            *self._points,
            width=self.get_border_width(),
            fill=self.get_fill_color(),
            outline=self.get_border_color(),
            state=HIDDEN
        )
        self._window._graphics.append([self._depth, self._tag, self])

    ## Adds a graphical object to the canvas.
    def _add_to(self):
        self._window._canvas.itemconfigure(self._tag, state=NORMAL)
        self._enabled = True


# Averages each x value and each y value in the list and returns it.
def _list_average(points):
    # this is used to gauge the center from all of the given points of the
    # polygon
    # the points are turned into a list of ints, then each even one is put into
    # its own list and each odd one is put into its own list and then both are
    # summed, divided, and put into a tuple and returned
    points = [i[j] for i in points for j in range(len(i))]
    pointsX = points[0:len(points):2]
    pointsY = points[1:len(points):2]
    return (int(sum(pointsX) / len(pointsX)),
            int(sum(pointsY) / len(pointsY)))


## A circle, which can be added to a Window object.
#
# Required Parameters:
# - window - Window - the window which the object will be added to.
#
# Optional Parameters:
# - radius - int - sets the radius of the Circle. (default: 40)
# - center - tuple - sets the center of the Circle. (default: (200, 200))
class Circle(Fillable):
    def __init__(self, window, radius=40, center=(200, 200)):
        # type checking
        assert isinstance(window, Window) and isinstance(radius, int) \
            and isinstance(center, tuple) and len(center) == 2 and \
            isinstance(center[0], int) and isinstance(center[1], int), \
            "Make sure window is a window, radius is an int, and center " + \
            "is a tuple of (int * int)."
        # setting inheritance
        Fillable.__init__(self)
        # setting variables
        self._window = window
        self._width = radius
        self._height = radius
        self._center = center
        # these are necessary for _circle_gen
        self._top_left = (self._center[0] - self._width,
                          self._center[1] - self._height)
        self._bottom_right = (self._center[0] + self._width,
                              self._center[1] + self._height)

        # creating the circle, adding it to the window and then adding it to
        # window._graphics
        self._points = []
        self._circle_gen()
        self._enabled = False
        self._tag = self._window._canvas.create_polygon(
            *self._points,
            width=self.get_border_width(),
            fill=self.get_fill_color(),
            outline=self.get_border_color(),
            state=HIDDEN
        )
        self._window._graphics.append([self._depth, self._tag, self])

    ## Adds a graphical object to the canvas.
    def _add_to(self):
        self._window._canvas.itemconfigure(self._tag, state=NORMAL)
        self._enabled = True

    ## Generates a circle.
    def _circle_gen(self):
        # generates the x axis and y axis of the object
        xAxis = round(self._bottom_right[0] - self._top_left[0]) / 2
        yAxis = round(self._bottom_right[1] - self._top_left[1]) / 2

        # 200 can be anything but I thought it was a good mix between precise
        # and efficient
        for i in range(200):
            # generates angle, calculates x and y using some trig i don't know.
            # this is probably the only time i'm going to say this, but if you
            # want to understand how this works, email pmagnus@hamilton.edu
            theta = (math.pi * 2) * float(i) / 200
            x1 = xAxis * math.cos(theta)
            y1 = yAxis * math.sin(theta)
            x = round((x1 * math.cos(0)) + (y1 * math.sin(0)))
            y = round((y1 * math.cos(0)) - (x1 * math.sin(0)))
            self._points.append((x + self._center[0], y + self._center[1]))

    ## Sets the radius of the Circle.
    # Required Parameters:
    # - radius - int
    def set_radius(self, radius):
        # type checking
        assert isinstance(radius, int), \
            "Make sure radius is an int."
        self._width = radius
        self._height = radius
        self._top_left = (self._center[0] - self._width,
                          self._center[1] - self._height)
        self._bottom_right = (self._center[0] + self._width,
                              self._center[1] + self._height)
        # redraws circle
        self._points = []
        self._circle_gen()
        self._refresh()


## An oval, which can be added to a Window object.
#
# Required Parameters:
# - window - Window - the window which the object will be added to.
#
# Optional Parameters:
# - radiusX - int - sets the radius of the Oval. (default: 40)
# - radiusY - int - sets the radius of the Oval. (default: 60)
# - center - tuple - sets the center of the Oval. (default: (200, 200))
class Oval(Fillable):
    def __init__(self, window, radiusX=40, radiusY=60, center=(200, 200)):
        # type checking
        assert isinstance(window, Window) and isinstance(radiusX, int) \
            and isinstance(radiusY, int) and isinstance(center, tuple) \
            and len(center) == 2 and isinstance(center[0], int) and \
            isinstance(center[1], int), \
            "Make sure window is a window, radiusX and radiusY are both " + \
            "ints, and center is a tuple of (int * int)."
        # setting inheritance
        Fillable.__init__(self)
        # setting variables
        self._window = window
        self._width = radiusX
        self._height = radiusY
        self._center = center
        # this is necessary for _circle_gen
        self._top_left = (self._center[0] - self._width,
                          self._center[1] - self._height)
        self._bottom_right = (self._center[0] + self._width,
                              self._center[1] + self._height)
        # creating points, then adding it to canvas and window._graphics
        self._points = []
        self._circle_gen()
        self._enabled = False
        self._tag = self._window._canvas.create_polygon(
            *self._points,
            width=self.get_border_width(),
            fill=self.get_fill_color(),
            outline=self.get_border_color(),
            state=HIDDEN
        )
        self._window._graphics.append([self._depth, self._tag, self])

    ## Adds a graphical object to the canvas.
    def _add_to(self):
        self._window._canvas.itemconfigure(self._tag, state=NORMAL)
        self._enabled = True

    ## Generates a circle.
    def _circle_gen(self):
        # generates the x axis and y axis of the object
        xAxis = round(self._bottom_right[0] - self._top_left[0]) / 2
        yAxis = round(self._bottom_right[1] - self._top_left[1]) / 2

        # 200 can be anything but I thought it was a good mix between precise
        # and efficient
        for i in range(200):
            # generates angle, calculates x and y using some trig i don't know.
            # this is probably the only time i'm going to say this, but if you
            # want to understand how this works, email pmagnus@hamilton.edu
            theta = (math.pi * 2) * float(i) / 200
            x1 = xAxis * math.cos(theta)
            y1 = yAxis * math.sin(theta)
            x = round((x1 * math.cos(0)) + (y1 * math.sin(0)))
            y = round((y1 * math.cos(0)) - (x1 * math.sin(0)))
            self._points.append((x + self._center[0], y + self._center[1]))

    ## Sets the horizontal and vertical radii of the Oval.
    # Required Parameters:
    # - radiusX - int
    # - radiusY - int
    def set_radii(self, radiusX, radiusY):
        # type checking
        assert isinstance(radiusX, int) and isinstance(radiusY, int), \
            "Make sure radiusX and radiusY are both ints."
        self._width = radiusX
        self._height = radiusY
        self._top_left = (self._center[0] - self._width,
                          self._center[1] - self._height)
        self._bottom_right = (self._center[0] + self._width,
                              self._center[1] + self._height)

        self._points = []
        self._circle_gen()
        self._refresh()


## A square, which can be added to a Window object.
#
# Required Parameters:
# - window - Window - the window which the object will be added to.
#
# Optional Parameters:
# - side_length - int - sets the side length of the Square. (default: 40)
# - center - tuple - sets the center of the Square. (default: (200, 200))
class Square(Fillable):
    def __init__(self, window, side_length=80, center=(200, 200)):
        # type checking
        assert isinstance(window, Window) and isinstance(side_length, int) \
            and isinstance(center, tuple) and len(center) == 2 and \
            isinstance(center[0], int) and isinstance(center[1], int), \
            "Make sure window is a window, the side length is an int, " + \
            "and the center is a tuple of (int * int)."
        # setting inheritance
        Fillable.__init__(self)
        # setting variables
        self._window = window
        self._width = side_length
        self._height = side_length
        self._center = center
        # creating points and then adding object to the canvas and
        # window._graphics
        self._points = [(self._center[0] - self._width // 2,
                         self._center[1] - self._height // 2),
                        (self._center[0] + self._width // 2,
                         self._center[1] - self._height // 2),
                        (self._center[0] + self._width // 2,
                         self._center[1] + self._height // 2),
                        (self._center[0] - self._width // 2,
                         self._center[1] + self._height // 2)]
        self._enabled = False
        self._tag = self._window._canvas.create_polygon(
            *self._points,
            width=self.get_border_width(),
            fill=self.get_fill_color(),
            outline=self.get_border_color(),
            state=HIDDEN
        )
        self._window._graphics.append([self._depth, self._tag, self])

    ## Adds a graphical object to the canvas.
    def _add_to(self):
        self._window._canvas.itemconfigure(self._tag, state=NORMAL)
        self._enabled = True

    ## Sets the side length of the Square.
    def set_side_length(self, side_length):
        # type checking
        assert isinstance(side_length, int)
        self._width = side_length
        self._height = side_length
        # re-rendering each point
        self._points = [(self._center[0] - self._width // 2,
                         self._center[1] - self._height // 2),
                        (self._center[0] + self._width // 2,
                         self._center[1] - self._height // 2),
                        (self._center[0] + self._width // 2,
                         self._center[1] + self._height // 2),
                        (self._center[0] - self._width // 2,
                         self._center[1] + self._height // 2)]
        self._refresh()


## A rectangle, which can be added to a Window object.
#
# Required Parameters:
# - window - Window - the window which the object will be added to.
#
# Optional Parameters:
# - width - int - sets the width of the Square. (default: 40)
# - height - int - sets the height of the Square. (default: 40)
# - center - tuple - sets the center of the Square. (default: (200, 200))
class Rectangle(Fillable):
    def __init__(self, window, width=80, height=120, center=(200, 200)):
        # type checking
        assert isinstance(window, Window) and isinstance(width, int) \
            and isinstance(height, int) and isinstance(center, tuple) \
            and len(center) == 2 and isinstance(center[0], int) and \
            isinstance(center[1], int), \
            "Make sure window is a Window, width and height are both ints, " + \
            "and center is a tuple of (int * int)."
        # enabling inheritance
        Fillable.__init__(self)
        # setting variables
        self._window = window
        self._width = width
        self._height = height
        self._center = center
        # rendering each corner point
        self._points = [(self._center[0] - self._width // 2,
                         self._center[1] - self._height // 2),
                        (self._center[0] + self._width // 2,
                         self._center[1] - self._height // 2),
                        (self._center[0] + self._width // 2,
                         self._center[1] + self._height // 2),
                        (self._center[0] - self._width // 2,
                         self._center[1] + self._height // 2)]
        # adding object to canvas and then to window._graphics
        self._enabled = False
        self._tag = self._window._canvas.create_polygon(
            *self._points,
            width=self.get_border_width(),
            fill=self.get_fill_color(),
            outline=self.get_border_color(),
            state=HIDDEN
        )
        self._window._graphics.append([self._depth, self._tag, self])

    ## Adds a graphical object to the canvas.
    def _add_to(self):
        self._window._canvas.itemconfigure(self._tag, state=NORMAL)
        self._enabled = True

    ## Sets the width and height of the Rectangle.
    def set_side_lengths(self, width, height):
        # type checking
        assert isinstance(width, int) and isinstance(height, int), \
            "Make sure width and height are both ints."
        self._width = width
        self._height = height
        # re-rendering each corner point and refreshing
        self._points = [(self._center[0] - self._width / 2,
                         self._center[1] - self._height / 2),
                        (self._center[0] + self._width / 2,
                         self._center[1] - self._height / 2),
                        (self._center[0] + self._width / 2,
                         self._center[1] + self._height / 2),
                        (self._center[0] - self._width / 2,
                         self._center[1] + self._height / 2)]
        self._refresh()


## A class which continually runs a function after a delay.
#
# Required Parameters:
# - window - Window - the window which the timer will use to start and stop the
# animation.
# - interval - int - the time (in milliseconds) that the function will refresh.
# - func - function - the function which will be run.
class Timer:
    def __init__(self, window, interval, func):
        # type checking
        # i haven't found a good way of checking whether a func is a function
        assert isinstance(window, Window) and isinstance(interval, int), \
            "Make sure window is a Window, the interval is an int, and " + \
            "the function is a function or process."
        self._window = window
        self._func = func
        self._interval = interval

    ## Sets the function which is going to be run.
    # Required Parameters:
    # - func - function
    def set_function(self, func):
        # i haven't found a good way of checking whether a func is a function
        self._func = func

    ## Sets the interval between executions of the function.
    # Required Parameters:
    # - interval - int
    def set_interval(self, interval):
        assert isinstance(interval, int), \
            "Make sure the interval is an int."
        self._interval = interval

    ## Starts the timer.
    def start(self):
        self._func()
        self._tag = self._window._root.after(self._interval, self.start)

    ## Stops the timer.
    def stop(self):
        self._window._root.after_cancel(self._tag)


## A wrapper for the _RunWithYieldDelay class. THIS SHOULD BE USED INSTEAD OF 
# CREATING AN _RunWithYieldDelay INSTANCE.
#
# Required Parameters:
# - window - Window
# - func - function which returns a generator of int
def RunWithYieldDelay(window, func):
    # type checking
    # i haven't found a good way of checking whether a func is a function
    assert isinstance(window, Window), \
        "Make sure the window is a Window and the function is a func() -> " + \
        "generator of int."
    _RunWithYieldDelay(window, func)


## A class which uses a function which returns a generator to rerun until the
# generator stops generating numbers.
#
# NOTE: DO NOT INITALIZE THIS CLASS ANYWHERE IN YOUR PROGRAM. THE WRAPPER
# FUNCTION RunWithYieldDelay SHOULD BE USED INSTEAD.
#
# Required Parameters:
# - window - Window - the window which the object with yield delay is on.
# - func - function which returns a generator of int - a function with a few
# necessary parameters which allow it to run with yield delay. A function needs
# to return a generator of int, needs a yield statement with an int which 
# represents the delay (in milliseconds), and it needs a raise StopIteration
# statement at the end of the function.
class _RunWithYieldDelay:
    def __init__(self, window, func):
        assert isinstance(window, Window), "Make sure the window is a " + \
            "Window and the function is a function that returns a " + \
            "generator of int."
        self._func = func
        self._window = window
        self._run()

    # Starts the run with yield delay.
    def _run(self):
        # this will keep running with yield delay until a StopIteration is
        # raised, at which point it will stop
        try:
            delay = next(self._func)
            if delay is None:
                delay = 1000
        except StopIteration:
            delay = 0

        if delay > 0:
            self._tag = self._window._root.after(delay, self._run)
        else:
            self._window._root.after_cancel(self._tag)
