## @package cs110graphics
# @mainpage CS 110 Graphics
# A Tkinter based graphics library for introductory computer science.
#
# <h2>Usage</h2>
# <hr>
# All files that use the CS 110 Graphics package must have the following line
# at the top of the file.
# @code
# from cs110graphics import *
# @endcode
# A simple implementation using the CS 110 Graphics package is shown below.
# The shown code will create a window and add a rectangle. StartGraphicsSystem
# must be used in all files to create the window and begin the main function.
# @code
# from cs110graphics import *
#
# def main(window):
#     rectangle = Rectangle(window)
#     window.add(rectangle)
#
# if __name__ == "__main__":
#     StartGraphicsSystem(main)
# @endcode
# @authors Paul Magnus '18
# @authors Ines Ayara '20
# @authors Matthew R. Jenkins '20
# @version 1.2
# @date Summer 2017

from tkinter import *  # for pretty much everything graphics related
import math  # for rotate
import inspect
from PIL import Image as image  # for Image class
from PIL import ImageTk as itk  # for Image class


#-------------------------------------------------------------------------------
#
#  Error Handling
#
#-------------------------------------------------------------------------------

# If this exception is thrown, something is wrong with the graphics
# package.
class CS110Exception(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return "Error: " + repr(self.parameter) + "\n" + \
            "This is a bug in the cs110graphics system."

def _check_type(param, param_name, target_type):
    if not isinstance(param, target_type):
        raise TypeError("\nThe parameter '" + param_name + "' should be a " +
                        str(target_type.__name__) +
                        " but instead was a " +
                        str(type(param).__name__) + "\n" +
                        param_name + " = " + str(param))

def _is_point(point):
    return (isinstance(point, tuple) and
            len(point) == 2 and
            isinstance(point[0], int) and
            isinstance(point[1], int))

## @file cs110graphics.py
# The main cs110graphics file


#-------------------------------------------------------------------------------
#
#  Window
#
#-------------------------------------------------------------------------------

## Window acts as a canvas which other objects can be put onto.
#
# The standard size of window created by StartGraphicsSystem is
# width = 400, height = 400.
class Window:
    ## @param width - int - The width of the canvas
    # @param height - int - The height of the canvas
    # @param background - str - Background color of canvas. Can be either the
    # name of a color ("yellow"), or a hex code ("#FFFF00")
    # @param name - str - The title of the window
    # @param first_function - proc(Window) - <b>(default: None)</b> When the
    # window is created, it runs this function.
    # @param master - unkown type - <b>(default: None)</b> The parent widget.
    # @warning Unless you understand how Tkinter works do not change master
    def __init__(self, width, height, background, name, first_function=None,
                 master=None):
        # type checking
        _check_type(width, "width", int)
        _check_type(height, "height", int)
        _check_type(background, "background", str)
        _check_type(name, "name", str)
        if not ((first_function is None) or callable(first_function)):
            raise TypeError("The parameter 'first_function' should be a " +
                            "function but instead was a " +
                            str(type(first_function).__name__))
        
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

        if not first_function is None:
            # running first function
            self._first_function(self)

    ## Adds an object to the Window.
    # @param graphic - GraphicalObject
    def add(self, graphic):
        # type checking
        _check_type(graphic, "graphic", GraphicalObject)

        # deferring to each object since each object requires a different
        # method of construction
        graphic._enabled = True
        self.refresh(start=graphic)

    ## Removes an object from the Window.
    # @param graphic - GraphicalObject
    def remove(self, graphic):
        # type checking
        _check_type(graphic, "graphic", GraphicalObject)

        graphic._remove()

    ## Returns the height of the window as an integer.
    # @return height - int
    def get_height(self):
        return self._height

    ## Returns the width of the window as an integer.
    # @return width - int
    def get_width(self):
        return self._width

    ## Sets the background color of the canvas.
    # @param background - string - Background color of canvas. Can be either the
    # name of a color ("yellow"), or a hex code ("#FFFF00")
    def set_background(self, background):
        # type checking
        _check_type(background, "background", str)
        
        self._background = background
        self._canvas.configure(bg=background)

    ## Sets the height of the canvas.
    # @param height - int
    def set_height(self, height):
        # type checking
        _check_type(height, "height", int)

        self._height = height
        self._canvas.configure(height=height)

    ## Sets the title of the window holding the canvas.
    # @param name - string
    def set_title(self, name):
        # type checking
        _check_type(name, "name", str)

        self._name = name
        self._root.title(name)

    ## Sets the width of the canvas.
    # @param width - height
    def set_width(self, width):
        # type checking
        _check_type(width, "width", int)

        self._width = width
        self._canvas.configure(width=width)

    # I think this is deprecated
    # Whenever an object is updated through external functions, its tag is
    # overwritten. This function goes into self._graphics and replaces the old
    # tag with a newer one, as well as replacing its depth with a newer one.
    def _update_tag(self, graphic):
        try:
            _check_type(graphic, "graphic", GraphicalObject)
        except TypeError as instance:
            raise CS110Exception(str(instance))

        # goes through every item in self._graphics, then saves the object's
        # tag and depth if it's found
        for item in self._graphics:
            if item[2] == graphic:
                item[1] = graphic._tag
                item[0] = graphic._depth

    ## Refreshes all objects in the window.
    # All objects are redrawn in depth order.
    # @param start - GraphicalObject - <b>(default: None)</b> only objects with
    # the same or equal depth to this object are refreshed.
    def refresh(self, start = None):
        if not start is None:
            _check_type(start, "start", GraphicalObject)
            start_depth = start.get_depth()
        
        self._graphics.sort()
        
        for graphic in self._graphics:
            # graphic[0] is the object's depth
            if graphic[0] >= start_depth:
                # refresh the graphic
                graphic[2]._refresh()


#-------------------------------------------------------------------------------
#
#  StartGraphicsSystem
#
#-------------------------------------------------------------------------------
                
## This initalizes the graphics system.
# @param first_function - func
# @param width - int - <b>(default: 400)</b>
# @param height - int - <b>(default: 400)</b>
# @param background - string - <b>(default: "white")</b>
# Background color of canvas. Can be either the
# name of a color ("yellow"), or a hex code ("#FFFF00")
# @param name - string - <b>(default: "Graphics Window")</b>
# The title of the window
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


#-------------------------------------------------------------------------------
#
#  Event
#
#-------------------------------------------------------------------------------
    
## An object representing an action from the user. Used by EventHandler objects.
# User actions that create Event objects include:
# - Pressing/Releasing a key on the keyboard
# - Pressing/Releasing a button on the mouse while on a GraphicalObject with an
# event handler
# - Moving the mouse while on a GraphicalObject with an event handler
#
# Each of these actions will call their corresponding methods in EventHandler
# automatically and give an instance of Event to the method called.
class Event:
    
    def __init__(self, event):
        # converting each necessary tkinter event parameter to something easier
        # to get access to and easier to understand
        self._type = event.type
        self._location = (event.x, event.y)
        self._rootLocation = (event.x_root, event.y_root)
        self._keysym = event.keysym
        self._num = event.num

    ## Returns the mouse button that is attached to the event. Returns
    # <tt>None</tt> if
    # the button fails to exist (like if the Event handles a key press).
    # @return button - str
    #
    # Possible returns are:
    # - "Left Mouse Button"
    # - "Right Mouse Button"
    # - "Middle Mouse Button"
    # - None
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
    # @return description - str
    #
    # Possible returns are:
    # - "Key Press"
    # - "Key Release"
    # - "Mouse Press"
    # - "Mouse Release"
    # - "Mouse Move"
    # - "Mouse Enter"
    # - "Mouse Leave"
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
    # @return key - str
    #
    # Most keys will evaluate to a single character (eg. pressing the a-key will
    # result in "a" while pressing shift-a will result in "A").
    def get_key(self):
        # this is mostly to handle user stupidity - why would you put
        # get_key in a handle_mouse function if get_button exists?
        if self._keysym == "??":
            return None
        return self._keysym

    ## Returns a tuple of the x and y coordinates of the mouse
    # location in the canvas.
    # @return location - tuple of (int * int) - (e.g. (200, 200))
    def get_mouse_location(self):
        return self._location

    ## Returns a tuple of the x and y coordinates of the mouse location in the
    # window. Typically using get_mouse_location is more applicable.
    # @return location - tuple of (int * int) - (e.g. (200, 200))
    def get_root_mouse_location(self):
        return self._rootLocation


#-------------------------------------------------------------------------------
#
#   EventHandler
#
#-------------------------------------------------------------------------------

## The EventHandler class should be extended by any class that reacts to user
# input in the form of some action with the computer mouse or the keyboard.
# Each method inherited from the EventHandler class takes an Event object as
# a parameter. The methods available to Event can be useful for interpreting
# how a call to each method should be handled. For example usage of
# event.get_key() can be used to destinguish between the keys used in navigating
# a character in a game.
#
# A sample program using the EventHandler is shown below.
# @code
# from cs110graphics import *
#
# class Bot(EventHandler):
#     """ A bot made up of a square that detects interaction from the user. """
#
#     def __init__(self, window):
#         """ Creates the bot which is comprised of one square and adds the Bot
#         as the event handler for the square body. """
#         self._window = window
#
#         # create the body of the Bot and add this class
#         # as the handler
#         self._body = Square(window)
#         self._body.add_handler(self)
#
#     def add_to_window(self):
#         """ This method adds the graphical representation of the bot
#         to the window. """
#         self._window.add(self._body)
#
#     ##########################################################################
#     # Event handling methods                                                  
#     ##########################################################################
#
#     def handle_key_press(self, event):
#         """ Prints what key was pressed. This is called whenever a key is
#         pressed regardless of the mouse position. """
#         print(event.get_key(), "was pressed")
#
#     def handle_key_release(self, event):
#         """ Prints what key was released. This is called whenever a key is
#         pressed regardless of the mouse position. """
#         print(event.get_key(), "was released")
#
#     def handle_mouse_enter(self, event):
#         """ Prints where the mouse entered the Bot. """
#         print("The mouse entered the bot at", event.get_mouse_location())
#
#     def handle_mouse_leave(self, event):
#         """ Prints where the mouse left the Bot. """
#         print("The mouse left the bot at", event.get_mouse_location())
#
#     def handle_mouse_move(self, event):
#         """ Prints when the mouse moves while on the Bot. """
#         print("The mouse moved to", event.get_mouse_location())
#
#     def handle_mouse_press(self, event):
#         """ Prints where the mouse was pressed while on the Bot. """
#         print("The mouse was pressed at", event.get_mouse_location())
#
#     def handle_mouse_release(self, event):
#         """ Prints where the mouse was released while on the Bot. """
#         print("The mouse was released at", event.get_mouse_location())
#
# def main(window):
#     bot = Bot(window)
#     bot.add_to_window()
#
# if __name__ == "__main__":
#     StartGraphicsSystem(main)
# @endcode
class EventHandler:
    def __init__(self):
        pass
    
    ## Handles a key press.
    # This function will be called whenever a key is pressed while the window is
    # active. The event parameter can be used to determine which key was
    # pressed. For example:
    # @code
    # class Handler(EventHandler):
    #     def handle_key_press(self, event):
    #         if "a" == event.get_key():
    #             # do something when a is pressed...
    #         else:
    #             # do something else...
    # @endcode
    # @param event - Event - the event that occurred
    def handle_key_press(self, event):
        pass

    ## Handles a key release.
    # This method will be called whenever a key is released while the window is
    # active. The event parameter can be used to determine which key was
    # pressed. For example:
    # @code
    # class Handler(EventHandler):
    #     def handle_key_release(self, event):
    #         if "a" == event.get_key():
    #             # do something when a is released...
    #         else:
    #             # do something else...
    # @endcode
    # @param event - Event - the event that occurred
    def handle_key_release(self, event):
        pass

    ## Handles when a mouse enters an object.
    # This is called by the system when the mouse enters the GraphicalObject
    # that this handler is an event handler for. The event parameter can be used
    # to determine the location at which the mouse entered the object.
    # @code
    # class Handler(EventHandler):
    #     def handle_mouse_enter(self, event):
    #         mouse_location = event.get_mouse_location()
    # @endcode
    # @param event - Event - the event that occurred
    def handle_mouse_enter(self, event):
        pass

    ## Handles when a mouse leaves an object.
    # This is called by the system when the mouse leaves the GraphicalObject
    # that this handler is an event handler for. The event parameter can be used
    # to determine the location at which the mouse left the object.
    # @code
    # class Handler(EventHandler):
    #     def handle_mouse_leave(self, event):
    #         mouse_location = event.get_mouse_location()
    # @endcode
    # @param event - Event - the event that occurred
    def handle_mouse_leave(self, event):
        pass

    ## Handles a mouse move.
    # This is called by the system when the mouse moves within the
    # GraphicalObject that this handler is an event handler for. The event
    # parameter can be used to determine the location that the mouse moved to.
    # @code
    # class Handler(EventHandler):
    #     def handle_mouse_move(self, event):
    #         mouse_location = event.get_mouse_location()
    # @endcode
    # @param event - Event - the event that occurred
    def handle_mouse_move(self, event):
        pass

    ## Handles a mouse press.
    # This is called by the system when a mouse button is pressed while the
    # mouse is on the GraphicalObject that this handler is an event handler for.
    # The event parameter can be used to determine the location at which the
    # mouse button was pressed and which mouse button was pressed.
    # @code
    # class Handler(EventHandler):
    #     def handle_mouse_press(self, event):
    #         mouse_location = event.get_mouse_location()
    #         mouse_button = event.get_button()
    # @endcode
    # @param event - Event - the event that occurred
    def handle_mouse_press(self, event):
        pass

    ## Handles a mouse release.
    # This is called by the system when a mouse button is released while the
    # mouse is on the GraphicalObject that this handler is an event handler for.
    # The event parameter can be used to determine the location at which the
    # mouse button was released and which mouse button was released.
    # @code
    # class Handler(EventHandler):
    #     def handle_mouse_release(self, event):
    #         mouse_location = event.get_mouse_location()
    #         mouse_button = event.get_button()
    # @endcode
    # @param event - Event - the event that occurred
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


#-------------------------------------------------------------------------------
#
#  GraphicalObject
#
#-------------------------------------------------------------------------------

## This is a parent class of any object which can be put into Window. No
# constructor exists in this class, but its methods are used by other objects
# that extend/inherit this class.
#
# Default values:
# - depth = 50
# - center = (200, 200)
class GraphicalObject:
    def __init__(self,
                 window = None,
                 center = (200, 200),
                 depth = 50,
                 pivot = None):

        _check_type(window, "window", Window)
        if not _is_point(center):
            raise TypeError("\nThe parameter 'center' should be a " +
                            "tuple of (int * int) but instead was a " +
                            str(type(center).__name__) + "\n" +
                            "center = " + str(center))

        if not depth is None:
            _check_type(depth, "depth", int)

        if not pivot is None:
            if not _is_point(pivot):
                raise TypeError("\nThe parameter 'pivot' should be a " +
                                "tuple of (int * int) but instead was a " +
                                str(type(pivot).__name__) + "\n" +
                                "pivot = " + str(pivot))
        
        self._depth = depth
        self._center = center
        self._window = window
        self._has_handlers = False
        self._enabled = False
        self._tag = -1
        self._pivot = pivot

        self._graphic_list = [self._depth,
                              self._tag,
                              self]
        self._window._graphics.append(self._graphic_list)

    ## Adds a handler to the graphical object.
    # @param handler_object - EventHandler - the object that handles
    # the events for this GraphicalObject
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

    ## Returns the center of the object.
    # @return center - tuple
    def get_center(self):
        return self._center

    ## Returns the depth of the object.
    # @return depth - int
    def get_depth(self):
        return self._depth

    ## Moves the object dx pixels horizontally and dy pixels vertically.
    # @param dx - int
    # @param dy - int
    def move(self, dx, dy):
        _check_type(dx, "dx", int)
        _check_type(dy, "dy", int)

        self._center = (self._center[0] + dx, self._center[1] + dy)
        self._move_graphic(dx, dy)

        if not self._pivot is None:
            self._pivot = (self._pivot[0] + dx,
                           self._pivot[1] + dy)

        # refresh all objects to keep depth correct
        self._window.refresh(start=self)
    
    # def move(self, dx, dy):
    #     # type checking
    #     _check_type(dx, "dx", int)
    #     _check_type(dy, "dy", int)

    #     self._center = (self._center[0] + dx, self._center[1] + dy)
    #     # goes through each point and increments it by dx or dy depending if
    #     # its index is even or odd
    #     for i in range(len(self._points)):
    #             self._points[i] = (self._points[i][0] + dx,
    #                                self._points[i][1] + dy)
    #     self._refresh()

    ## Moves a graphical object to a point.
    # @param point - tuple of (int * int)
    def move_to(self, point):
        # type checking
        if not _is_point(point):
            raise TypeError("\nThe parameter 'point' should be a " +
                            "tuple of (int * int) but instead was a " +
                            str(type(point).__name__) + "\n" +
                            "point = " + str(point))

        dx = point[0] - self._center[0]
        dy = point[1] - self._center[1]
        
        self._move_graphic(dx, dy)

        self._center = point

        if not self._pivot is None:
            self._pivot = (self._pivot[0] + dx,
                           self._pivot[1] + dy)
        
        # refresh all objects to keep depth correct
        self._window.refresh(start=self)

    def _move_graphic(self, dx, dy):
        raise NotImplementedError

    # Removes and adds an object after it's been changed.
    def _refresh(self):
        if self._enabled:
            self._remove()
            self._add()
            # deal with handlers
        
        # # since this is run for every object we need a special case if the
        # # object is a graphical object and not a fillable
        #     # in that case, we remove it and readd it without using any canvas
        #     # operators, add handlers if they exist, and return
        # if isinstance(self, Text) or isinstance(self, Image):
        #     self._remove_from(self._window)
        #     self._add_to()
        #     self._window._update_tag(self)
        #     if self._has_handlers:
        #         self.add_handler(self._parent_object)
        # else:
        #     # from here on out we're assuming fillables only.
        #     # we remove the object from the window, and then if the object is
        #     # disabled we readd it with the HIDDEN state, otherwise just readd
        #     # it
        #     self._remove_from(self._window)
        #     if self._enabled is False:
        #         self._tag = self._window._canvas.create_polygon(
        #             *self._points,
        #             width=self.get_border_width(),
        #             fill=self.get_fill_color(),
        #             outline=self.get_border_color(),
        #             state=HIDDEN
        #         )
        #     else:
        #         self._tag = self._window._canvas.create_polygon(
        #             *self._points,
        #             width=self.get_border_width(),
        #             fill=self.get_fill_color(),
        #             outline=self.get_border_color()
        #         )
        #     # we then update the tag, and then readd handlers if they exist
        #     # if we don't then the event will only run once and then not again
        #     self._window._update_tag(self)
        #     if self._has_handlers:
        #         self.add_handler(self._parent_object)

    ## Removes a graphical object from the canvas.
    def _remove(self):
        if self._enabled:
            if self._tag != -1:
                self._window._canvas.delete(self._tag)
                # self._window._graphics.remove([self._depth, self._tag, self])
                self._tag = -1
                self._update_graphic_list()
            self._enabled = False

    def _add(self):
        raise NotImplementedError

    ## Sets the depth of the GraphicalObject.
    # @param depth - int
    def set_depth(self, depth):
        # type checking
        _check_type(depth, "depth", int)
    
        self._depth = depth
        # self._window._update_tag(self)
        self._update_graphic_list()
        # self._window._graphics.sort()

        # get rid of all objects and readd them in depth order
        self._window.refresh(start=self)

    # Hopefully with list aliasing, this updates the list in window
    def _update_graphic_list(self):
        self._graphic_list[0] = self._depth
        self._graphic_list[1] = self._tag
        

#-------------------------------------------------------------------------------
#
#  Fillable
#
#-------------------------------------------------------------------------------

## This is a parent class of any object which can have its colors
# modified. No constructor exists in this class, but its methods are used by
# other objects that extend/inherit this class.
#
# Default values:
# - border color = "black"
# - border width = 2
# - fill color = "white"
# - pivot = center
class Fillable(GraphicalObject):
    def __init__(self,
                 window = None,
                 center = (200, 200),
                 points = [],
                 pivot = (200, 200),
                 depth = 50):
        
        GraphicalObject.__init__(self,
                                 window = window,
                                 center = center,
                                 depth = depth,
                                 pivot = pivot)
        # default values - otherwise when an object is changed later it reverts
        # any changes that were made

        _check_type(points, "points", list)
        
        for point in points:
            if not _is_point(point):
                raise TypeError("\nThe parameter 'points' should be a " +
                                "list of tuples of (int * int)\n" +
                                "points = " + str(points))
        
        self._border_color = "black"
        self._border_width = 2
        self._fill_color = "white"
        self._points = points

    ## Returns the border color.
    # @return border_color - str - Can be either the
    # name of a color ("yellow"), or a hex code ("#FFFF00")
    def get_border_color(self):
        return self._border_color

    ## Returns the border width.
    # @return border_width - int
    def get_border_width(self):
        return self._border_width

    ## Returns fill color.
    # @return color - int - Can be either the
    # name of a color ("yellow"), or a hex code ("#FFFF00")
    def get_fill_color(self):
        return self._fill_color

    ## Returns the pivot point.
    # @return pivot - tuple (int * int)
    def get_pivot(self):
        return self._pivot

    ## Rotates the object.
    # @param degrees - int
    def rotate(self, degrees):
        # type checking
        _check_type(degrees, "degrees", int)
        
        # calculates radians, runs _rotate_helper, moves back to its center and
        # refreshes
        radians = (math.pi / 180) * degrees
        for i in range(len(self._points)):
            self._points[i] = _rotate_helper(self._points[i],
                                             radians,
                                             self._pivot)

        self.move_to(self._center)

    ## Scales the object up or down depending on the factor.
    # @param factor - float
    def scale(self, factor):
        # type checking
        _check_type(factor, "factor", float)

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
        self._window.refresh(start=self)

    def _move_graphic(self, dx, dy):
        for i in range(len(self._points)):
            self._points[i] = (self._points[i][0] + dx,
                               self._points[i][1] + dy)

        if self._enabled:
            self._window.refresh(start=self)

    # def move(self, dx, dy):
    #     GraphicalObject.move(self, dx, dy)

    #     # update pivot
    #     self._pivot = (self._pivot[0] + dx, self._pivot[1] + dy)

    # def move_to(self, point):
    #     difference = (self._pivot[0] - self._center[0],
    #                   self._pivot[1] - self._center[1])
        
    #     GraphicalObject.move_to(self, point)

    #     self._pivot = (self._center[0] + difference[0],
    #                    self._center[1] + difference[1])

    ## Sets the border color.
    # @param color - string - Can be either the
    # name of a color ("yellow"), or a hex code ("#FFFF00")
    def set_border_color(self, color):
        # type checking
        _check_type(color, "color", str)
        
        self._border_color = color

        if self._enabled:
            self._window._canvas.itemconfigure(self._tag, outline=color)

    ## Sets the border width.
    # @param width - int
    def set_border_width(self, width):
        # type checking
        _check_type(width, "width", int)

        self._border_width = width

        if self._enabled:
            self._window._canvas.itemconfigure(self._tag, width=width)

    ## Sets the fill color.
    # @param color - string - Can be either the
    # name of a color ("yellow"), or a hex code ("#FFFF00")
    def set_fill_color(self, color):
        # type checking
        _check_type(color, "color", str)
        
        self._fill_color = color

        if self._enabled:
            self._window._canvas.itemconfigure(self._tag, fill=color)
        
    ## Sets the pivot point.
    # @param pivot - tuple of (int * int)
    def set_pivot(self, pivot):
        # type checking
        if not _is_point(pivot):
            raise TypeError("\nThe parameter 'pivot' should be a " +
                            "tuple of (int * int) but instead was a " +
                            str(type(pivot).__name__) + "\n" +
                            "pivot = " + str(pivot))

        self._pivot = pivot

    def _add(self):
        if not self._enabled:
            self._tag = self._window._canvas.create_polygon(
                *self._points,
                width=self.get_border_width(),
                fill=self.get_fill_color(),
                outline=self.get_border_color())

            self._update_graphic_list()
            # self._window._graphics.append([self._depth, self._tag, self])
            
            self._enabled = True


# Aids in rotation.
def _rotate_helper(point, angle, pivot):
    point = (point[0] - pivot[0], point[1] - pivot[1])
    newX = round(point[0] * math.cos(angle) + point[1] * math.sin(angle))
    newY = round(point[1] * math.cos(angle) - point[0] * math.sin(angle))
    return (newX + pivot[0], newY + pivot[1])


#-------------------------------------------------------------------------------
#
#  Image
#
#-------------------------------------------------------------------------------

## An image, which can be added to a Window object.
class Image(GraphicalObject):
    ## @param window - Window - the window which the object will be added to
    # @param image_loc - str- The file location for an image, see below for
    # instructions regarding file locations
    # @param width - int - <b>(default: 100)</b> the width of the image
    # @param height - int - <b>(default: 100)</b> the height of the image
    # @param center - tuple of (int * int) - <b>(default: (200, 200))</b> the
    # center location for the image
    #
    # File locations:
    # - If a file is in the same folder/directory as the program, just use the
    # name of the file
    # - Otherwise use a file path: eg. "~/110/bots/images/bot.jpg" or
    # "./images/bot.jpg"
    #
    # Note that "." represents the current directory and ".." represents the
    # parent directory.
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

    # Adds a graphical object to the canvas.
    def _add_to(self):
        self._tag = self._window._canvas.create_image(self._center[0],
                                                      self._center[1],
                                                      image=self._img)
        self._enabled = True

        self._window._update_tag(self)

    def move(self, dx, dy):
        # type checking
        assert isinstance(dx, int) and isinstance(dy, int), \
            "Make sure dx and dy are both ints."
        self._center = (self._center[0] + dx, self._center[1] + dy)
        self._remove_from(self._window)
        self._img = _image_gen(self._image_loc, self._width, self._height)
        self._refresh()

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
    # @param width - int
    # @param height - int
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

    ## Rotates an object.
    # @param degrees - int
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
    # @param factor - float
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
    # @return size - tuple of (int * int)
    def size(self):
        return (self._width, self._height)


# Creates a resized image and returns an image of type itk.PhotoImage.
def _image_gen(image_loc, width, height):
    # opens and resizes an object based on the width and height
    img_temp = image.open(image_loc)
    img_temp = img_temp.resize((width, height), image.ANTIALIAS)
    return itk.PhotoImage(img_temp)


#-------------------------------------------------------------------------------
#
#  Text
#
#-------------------------------------------------------------------------------

## Text which can be added to a Window object.
class Text(GraphicalObject):
    ## @param window - Window - the window which the object will be added to
    # @param text - str - The text which is displayed
    # @param size - int - <b>(default: 12)</b> sets the size of the text
    # @param center - tuple of int * int - <b>(default: (200, 200))</b>
    # sets the center of the Image
    def __init__(self, window, text, size=12, center=(200, 200)):
        # type checking
        assert isinstance(window, Window) and isinstance(size, int) \
            and isinstance(center, tuple) and len(center) == 2 and \
            isinstance(center[0], int) and isinstance(center[1], int), \
            "Make sure the window is a Window, the size is an int, and " + \
            "the center is a tuple of (int * int)."
        # for inheritance
        GraphicalObject.__init__(self, window = window, center = center)
        # setting variables, creating object and adding it to window._graphics
        # self._window = window
        self._text = text
        # self._center = center
        self._size = size
        self._enabled = False
        self._tag = self._window._canvas.create_text(self._center[0],
                                                     self._center[1],
                                                     text=str(self._text),
                                                     font=("Helvetica",
                                                           self._size),
                                                     state=HIDDEN)
        self._window._graphics.append([self._depth, self._tag, self])

    # Adds a graphical object to the canvas.
    def _add_to(self):
        self._tag = self._window._canvas.create_text(self._center[0],
                                                     self._center[1],
                                                     text=str(self._text),
                                                     font=("Helvetica",
                                                           self._size))
        self._enabled = True

        self._window._update_tag(self)

    def move(self, dx, dy):
        # type checking
        assert isinstance(dx, int) and isinstance(dy, int), \
            "Make sure dx and dy are both ints."
        self._center = (self._center[0] + dx, self._center[1] + dy)
        # text is special because it does not need to be recreated after each
        # modification
        self._window._canvas.coords(self._tag,
                                    (self._center[0], self._center[1]))

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
    # @param size - int
    def set_size(self, size):
        assert isinstance(size, int), \
            "Make sure size is an int."
        self._size = size
        # text is special because it does not need to be recreated after each
        # modification
        self._window._canvas.itemconfigure(self._tag, font=("Helvetica",
                                                            self._size))

    ## Sets the text.
    # @param text - str
    def set_text(self, text):
        assert isinstance(text, str), \
            "Make sure text is a string."
        self._text = text
        # text is special because it does not need to be recreated after each
        # modification
        self._window._canvas.itemconfigure(self._tag, text=self._text)

        
#-------------------------------------------------------------------------------
#
#  Polygon
#
#-------------------------------------------------------------------------------

## A Polygon, which can be added to a Window object.
class Polygon(Fillable):
    ## @param window - Window - the window which the object will be added to
    # @param points - list of tuples of (int * int) - each tuple corresponds
    # to an x-y point
    def __init__(self, window, points):
        center = _list_average(points)
        
        # establishing inheritance
        Fillable.__init__(self,
                          window = window,
                          center = center,
                          points = points,
                          pivot = center)
        
        # setting all variables, creating object, and adding it to
        # window._graphics
        # self._tag = self._window._canvas.create_polygon(
        #     *self._points,
        #     width=self.get_border_width(),
        #     fill=self.get_fill_color(),
        #     outline=self.get_border_color(),
        #     state=HIDDEN
        # )
        # self._window._graphics.append([self._depth, self._tag, self])

    # Adds a graphical object to the canvas.
    # def _add_to(self):
    #     self._window._canvas.itemconfigure(self._tag, state=NORMAL)
    #     self._enabled = True


# Averages each x value and each y value in the list and returns it.
def _list_average(points):
    # this is used to gauge the center from all of the given points of the
    # polygon
    # the points are turned into a list of ints, then each even one is put into
    # its own list and each odd one is put into its own list and then both are
    # summed, divided, and put into a tuple and returned
    # points = [i[j] for i in points for j in range(len(i))]
    # pointsX = points[0:len(points):2]
    # pointsY = points[1:len(points):2]

    x_sum = 0
    y_sum = 0
    for i in range(len(points)):
        x_sum += points[i][0]
        y_sum += points[i][1]

    return (round(x_sum / len(points)),
            round(y_sum / len(points)))
    # return (int(sum(pointsX) / len(pointsX)),
            # int(sum(pointsY) / len(pointsY)))


#-------------------------------------------------------------------------------
#
#  Circle
#
#-------------------------------------------------------------------------------

## A circle, which can be added to a Window object.
class Circle(Fillable):
    ## @param window - Window - the window which the object will be added to
    # @param radius - int - <b>(default: 40)</b> the radius of the circle
    # @param center - tuple of (int * int) - <b>(default: (200, 200))</b>
    # sets the center of the circle
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

    # Adds a graphical object to the canvas.
    def _add_to(self):
        self._window._canvas.itemconfigure(self._tag, state=NORMAL)
        self._enabled = True

    # Generates a circle.
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
    # @param radius - int
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

        
#-------------------------------------------------------------------------------
#
#  Oval
#
#-------------------------------------------------------------------------------

## An oval, which can be added to a Window object.
class Oval(Fillable):
    ## @param window - Window - the window which the object will be added to
    # @param radiusX - int - <b>(default: 40)</b> the radius in the x-direction
    # @param radiusY - int - <b>(default: 60)</b> the radius in the y-direction
    # @param center - tuple of (int * int) - <b>(default: (200, 200))</b>
    # the center of the oval
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

    # Adds a graphical object to the canvas.
    def _add_to(self):
        self._window._canvas.itemconfigure(self._tag, state=NORMAL)
        self._enabled = True

    # Generates a circle.
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

    ## Sets the horizontal and vertical radii of the oval.
    # @param radiusX - int
    # @param radiusY - int
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


#-------------------------------------------------------------------------------
#
#  Square
#
#-------------------------------------------------------------------------------
        
## A square, which can be added to a Window object.
class Square(Fillable):
    ## @param window - Window - the window which the object will be added to
    # @param side_length - int - <b>(default: 40)</b> the side length
    # @param center - tuple of (int * int) - <b>(default: (200, 200))</b>
    # the center of the square
    def __init__(self, window, side_length=80, center=(200, 200)):
        # type checking

        _check_type(side_length, "side_length", int)
        
        self._side_length = side_length
        points = [(center[0] - side_length // 2,
                   center[1] - side_length // 2),
                  (center[0] + side_length // 2,
                   center[1] - side_length // 2),
                  (center[0] + side_length // 2,
                   center[1] + side_length // 2),
                  (center[0] - side_length // 2,
                   center[1] + side_length // 2)]
        
        # setting inheritance
        Fillable.__init__(self,
                          window = window,
                          center = center,
                          points = points,
                          pivot = center)
        # setting variables
        # self._window = window
        # self._width = side_length
        # self._height = side_length
        # self._center = center
        # # creating points and then adding object to the canvas and
        # # window._graphics
        # self._points = [(self._center[0] - self._width // 2,
        #                  self._center[1] - self._height // 2),
        #                 (self._center[0] + self._width // 2,
        #                  self._center[1] - self._height // 2),
        #                 (self._center[0] + self._width // 2,
        #                  self._center[1] + self._height // 2),
        #                 (self._center[0] - self._width // 2,
        #                  self._center[1] + self._height // 2)]
        # self._enabled = False
        # self._tag = self._window._canvas.create_polygon(
        #     *self._points,
        #     width=self.get_border_width(),
        #     fill=self.get_fill_color(),
        #     outline=self.get_border_color(),
        #     state=HIDDEN
        # )
        # self._window._graphics.append([self._depth, self._tag, self])

    # Adds a graphical object to the canvas.
    # def _add_to(self):
    #     self._window._canvas.itemconfigure(self._tag, state=NORMAL)
    #     self._enabled = True

    ## Sets the side length of the Square.
    # @param side_length - int
    def set_side_length(self, side_length):
        # type checking
        _check_type(side_length, "side_length", int)

        # equivalent to scale
        self.scale(side_length / self._side_length)

        self._side_length = side_length

#-------------------------------------------------------------------------------
#
#  Rectangle
#
#-------------------------------------------------------------------------------
        
## A rectangle, which can be added to a Window object.
class Rectangle(Fillable):
    ## @param window - Window - the window which the object will be added to
    # @param width - int - <b>(default: 80)</b> the width of the rectangle
    # @param height - int - <b>(default: 120)</b> the height of the rectangle
    # @param center - tuple of (int * int) - <b>(default: (200, 200))</b>
    # the center of the rectangle
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

    # Adds a graphical object to the canvas.
    def _add_to(self):
        self._window._canvas.itemconfigure(self._tag, state=NORMAL)
        self._enabled = True

    ## Sets the width and height of the Rectangle.
    # @param width - int
    # @param height - int
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
        self._window.refresh(start=self)

#-------------------------------------------------------------------------------
#
#  Timer
#
#-------------------------------------------------------------------------------
        
## A class which continually runs a function after a delay.
class Timer:
    ## @param window - Window - the window which the timer will use to start
    # and stop the animation
    # @param interval - int - the time (in milliseconds) that that the timer
    # will wait
    # @param func - function - the function which will be run
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
    # @param func - function
    def set_function(self, func):
        # i haven't found a good way of checking whether a func is a function
        self._func = func

    ## Sets the interval between executions of the function.
    # @param interval - int
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


#-------------------------------------------------------------------------------
#
#  RunWithYieldDelay
#
#-------------------------------------------------------------------------------

## Begins an animation loop.
# @param window - Window
# @param func - function which returns a generator of int
#
# The function given must use yield statements to indicate moments in the code
# when the system should stop and refresh the window. The system will pause for
# the number of milliseconds given to yield. This allows for the creation of
# animation systems by refreshing the window between movements.
def RunWithYieldDelay(window, func):
    # type checking
    # i haven't found a good way of checking whether a func is a function
    assert isinstance(window, Window), \
        "Make sure the window is a Window and the function is a func() -> " + \
        "generator of int."
    _RunWithYieldDelay(window, func)


# A class which uses a function which returns a generator to rerun until the
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
