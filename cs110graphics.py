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

# Verifies that param has the same type as target_type
# If not, then a TypeError is raised
def _check_type(param, param_name, target_type):
    if not isinstance(param, target_type):
        raise TypeError("\nThe parameter '" + param_name + "' should be a " +
                        str(target_type.__name__) +
                        " but instead was a " +
                        str(type(param).__name__) + "\n" +
                        param_name + " = " + str(param))

# Returns true if point is a tuple of (int * int)
def _is_point(point):
    return (isinstance(point, tuple) and
            len(point) == 2 and
            isinstance(point[0], int) and
            isinstance(point[1], int))

# Verifies that fn is a function
# If not, then a TypeError is raised
def _check_function(fn, fn_name):
    if not callable(fn):
        raise TypeError("\nThe parameter '" + fn_name + "' should be a " +
                        "function\n" +
                        fn_name + " = " + str(fn))

# Verifies that gen is a generator
# If not, then a TypeError is raised
def _check_generator(gen, gen_name):
    if not (inspect.isgenerator(gen) or
            inspect.isgeneratorfunction(gen)):
        raise TypeError("\nThe parameter '" + gen_name + "' should be a " +
                        "generator function\n" +
                        gen_name + " = " + str(gen))

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

        # set up key event handling
        self._bind_handlers()

        self._start_depth = None
        self._needs_refresh = False

        if first_function is not None:
            # running first function
            self._first_function(self)
            # display graphics when done
            self._refresh()

    # This controls the Tkinter integration of event handlers
    # Key events are handled at the Window/Canvas level
    def _bind_handlers(self):
        bindings = {
            "<Key>"                : self._key_press,
            "<KeyRelease>"         : self._key_release,
        }

        for binding in bindings:
            # binding is the Tkinter binding string
            # bindings[binding] is the function to be bound
            self._canvas.bind(binding, bindings[binding])

    # Key press is bound at the canvas level
    # This then calls each graphic's _key_press method
    def _key_press(self, event):
        for graphic in self._graphics:
            graphic[2]._key_press(event)
        self._refresh()

    # Key release is bound at the canvas level
    # This then calls each graphic's _key_release method
    def _key_release(self, event):
        for graphic in self._graphics:
            graphic[2]._key_release(event)
        self._refresh()

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

    ## Refreshes all objects in the window.
    # All objects are redrawn in depth order.
    # @param start - GraphicalObject - <b>(default: None)</b> only objects with
    # the same or equal depth to this object are refreshed.
    def refresh(self, start = None):
        # print("We need a refresh")
        self._needs_refresh = True

        # done if no start object was given
        if start == None:
            return

        _check_type(start, "start", GraphicalObject)
        
        # update start depth
        if (self._start_depth is None or
            start.get_depth() > self._start_depth):
            self._start_depth = start.get_depth()

    # This is called when the system pauses for a moment and is ready to
    # refresh the window. This will only refresh objects that need to be
    # refreshed based on the last call to the function refresh above and
    # the depth of the objects in the window.
    def _refresh(self):
        if self._needs_refresh:
            self._graphics.sort(key=lambda g : g[0])

            for graphic in reversed(self._graphics):
                # graphic[0] is the object's depth
                if (self._start_depth is None or
                    graphic[0] <= self._start_depth):
                    # refresh the graphic
                    graphic[2]._refresh()
                # graphic[2]._refresh()
            
            self._needs_refresh = False
            self._start_depth = None


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

    def __str__(self):
        return "Event: " + self.get_description()

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
    # @bug Overrides of this method is likely to be called more often than
    # expected and many GraphicalObject methods will not work correctly with
    # when called within the method, avoid using this if possible.
    #
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
    # @bug GraphicalObjects may not update correctly if moved or modified
    # within this method. You can use this for setting variables, though.
    #
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

        if depth is not None:
            _check_type(depth, "depth", int)

        if pivot is not None:
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

        self._handlers = []

    ## Adds a handler to the graphical object.
    # @param handler_object - EventHandler - the object that handles
    # the events for this GraphicalObject
    def add_handler(self, handler_object):
        _check_type(handler_object, "handler_object", EventHandler)
        
        if handler_object not in self._handlers:
            self._handlers.append(handler_object)

        self._has_handlers = True

    # This controls the Tkinter integration of event handlers
    # When a graphic is added to the window, this binds the events
    def _bind_handlers(self):
        bindings = {
            "<Enter>"              : self._mouse_enter,
            "<Leave>"              : self._mouse_leave,
            "<Motion>"             : self._mouse_move,
            "<Button-1>"           : self._mouse_press,
            "<Button-2>"           : self._mouse_press,
            "<Button-3>"           : self._mouse_press,
            "<ButtonRelease-1>"    : self._mouse_release,
            "<ButtonRelease-2>"    : self._mouse_release,
            "<ButtonRelease-3>"    : self._mouse_release,
        }

        for binding in bindings:
            # binding is the Tkinter binding string
            # bindings[binding] is the function to be bound
            self._window._canvas.tag_bind(self._tag,
                                          binding,
                                          bindings[binding])

    def _key_press(self, event):
        if self._enabled:
            tkEvent = Event(event)
            for handler_object in self._handlers:
                _call_handler(handler_object.handle_key_press, tkEvent)

    def _key_release(self, event):
        if self._enabled:
            tkEvent = Event(event)
            for handler_object in self._handlers:
                _call_handler(handler_object.handle_key_release, tkEvent)

    def _mouse_enter(self, event):
        if self._enabled:
            tkEvent = Event(event)
            for handler_object in self._handlers:
                _call_handler(handler_object.handle_mouse_enter, tkEvent)
            # This creates infinite recursion since when an object is added
            # under the mouse pointer, mouse enter is called
            # self._window._refresh()

    def _mouse_leave(self, event):
        if self._enabled:
            tkEvent = Event(event)
            for handler_object in self._handlers:
                _call_handler(handler_object.handle_mouse_leave, tkEvent)
            self._window._refresh()

    def _mouse_move(self, event):
        if self._enabled:
            tkEvent = Event(event)
            for handler_object in self._handlers:
                _call_handler(handler_object.handle_mouse_move, tkEvent)
            self._window._refresh()

    def _mouse_press(self, event):
        if self._enabled:
            tkEvent = Event(event)
            for handler_object in self._handlers:
                _call_handler(handler_object.handle_mouse_press, tkEvent)
            # for some reason, this breaks the mouse release handler
            # self._window._refresh()

    def _mouse_release(self, event):
        if self._enabled:
            tkEvent = Event(event)
            for handler_object in self._handlers:
                _call_handler(handler_object.handle_mouse_release, tkEvent)
            self._window._refresh()

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

        if self._pivot is not None:
            self._pivot = (self._pivot[0] + dx,
                           self._pivot[1] + dy)

        # refresh all objects to keep depth correct
        self._window.refresh(start=self)

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

        if self._pivot is not None:
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
            self._bind_handlers()
        
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

        radians = (math.pi / 180) * degrees
        for i in range(len(self._points)):
            self._points[i] = _rotate_helper(self._points[i],
                                             radians,
                                             self._pivot)

        self._window.refresh(start=self)

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

    # moves all of the points in the graphic
    def _move_graphic(self, dx, dy):
        for i in range(len(self._points)):
            self._points[i] = (self._points[i][0] + dx,
                               self._points[i][1] + dy)

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

        _check_type(image_loc, "image_loc", str)
        _check_type(width, "width", int)
        _check_type(height, "height", int)

        GraphicalObject.__init__(self,
                                 window = window,
                                 center = center,
                                 pivot = center)

        self._image_loc = image_loc
        self._image = image.open(self._image_loc).convert('RGBA')
        self._width = width
        self._height = height
        self._degrees = 0

    # Adds a graphical object to the canvas.
    def _add(self):
        if not self._enabled:
            # resize and rotate the image
            img = self._image.rotate(self._degrees,
                                     expand=True).resize((self._width,
                                                          self._height),
                                                         image.BICUBIC)

            # convert to correct format
            self._photo_image = itk.PhotoImage(img)

            # add to window
            self._tag = self._window._canvas.create_image(self._center[0],
                                                          self._center[1],
                                                          image =
                                                          self._photo_image)
            
            self._update_graphic_list()
            self._enabled = True

    def _move_graphic(self, dx, dy):
        pass

    ## Resizes the Image.
    # @param width - int
    # @param height - int
    def resize(self, width, height):
        _check_type(width, "width", int)
        _check_type(height, "height", int)

        self._width = width
        self._height = height
        self._window.refresh(start=self)

    ## Rotates an object.
    # @param degrees - int
    def rotate(self, degrees):
        _check_type(degrees, "degrees", int)
        
        self._degrees = (self._degrees + degrees) % 360
        self._window.refresh(start=self)

    ## Scales the image according to the factor.
    # @param factor - float
    def scale(self, factor):
        _check_type(factor, "factor", float)
        
        self._width = int(self._width * factor)
        self._height = int(self._height * factor)
        self._window.refresh(start=self)

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
        _check_type(text, "text", str)
        _check_type(size, "size", int)

        GraphicalObject.__init__(self,
                                 window = window,
                                 center = center)

        self._text = text
        self._size = size
        
    # Adds a graphical object to the canvas.
    def _add(self):
        if not self._enabled:
            self._tag = self._window._canvas.create_text(self._center[0],
                                                         self._center[1],
                                                         text=str(self._text),
                                                         font=("Helvetica",
                                                               self._size))

            self._update_graphic_list()
            self._enabled = True

    def _move_graphic(self, dx, dy):
        pass

    ## Sets the font size of the text.
    # @param size - int
    def set_size(self, size):
        _check_type(size, "size", int)
        
        self._size = size
        self._window.refresh(start=self)

    ## Sets the text.
    # @param text - str
    def set_text(self, text):
        _check_type(text, "text", str)
        
        self._text = text
        self._window.refresh(start=self)


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
        

# Averages each x value and each y value in the list and returns it.
def _list_average(points):
    x_sum = 0
    y_sum = 0
    for i in range(len(points)):
        x_sum += points[i][0]
        y_sum += points[i][1]

    return (round(x_sum / len(points)),
            round(y_sum / len(points)))


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
        # Note that this does not use Fillable constructor since
        # it does not use points to generate the object
        GraphicalObject.__init__(self,
                                 window = window,
                                 center = center,
                                 pivot = center)

        # These are to simulate the attributes set up in Fillable
        self._border_color = "black"
        self._border_width = 2
        self._fill_color = "white"

        self._radius = radius

    # Rotates the circle around the pivot by the given number of degrees
    def rotate(self, degrees):
        _check_type(degrees, "degrees", int)

        # If the pivot is the center there is no change
        if self._pivot == self._center:
            return

        self._center = _rotate_helper(self._center,
                                      degrees * math.pi / 180,
                                      self._pivot)
        self._window.refresh(start=self)

    # Scales the circle by the given factor around the center
    def scale(self, factor):
        # type checking
        _check_type(factor, "factor", float)

        self._radius = self._radius * factor
        self._window.refresh(start=self)

    def _move_graphic(self, dx, dy):
        # GraphicalObject already moves center and pivot
        pass

    # This adds the circle to the window. The circle is implemented as
    # an oval in Tkinter.
    def _add(self):
        if not self._enabled:
            self._tag = self._window._canvas.create_oval(
                self._center[0] - self._radius,
                self._center[1] - self._radius,
                self._center[0] + self._radius,
                self._center[1] + self._radius,
                width = self.get_border_width(),
                fill = self.get_fill_color(),
                outline = self.get_border_color())

            self._update_graphic_list()

            self._enabled = True

    ## Sets the radius of the Circle.
    # @param radius - int
    def set_radius(self, radius):
        # type checking
        _check_type(radius, "radius", int)
        self._radius = radius
        self._window.refresh(start=self)
        
        
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
        Fillable.__init__(self,
                          window = window,
                          center = center,
                          points = _oval_gen(center, radiusX, radiusY),
                          pivot = center)

        self._radiusX = radiusX
        self._radiusY = radiusY
        self._degrees = 0

    ## Sets the horizontal and vertical radii of the oval.
    # @param radiusX - int
    # @param radiusY - int
    def set_radii(self, radiusX, radiusY):
        _check_type(radiusX, "radiusX", int)
        _check_type(radiusY, "radiusY", int)

        self._radiusX = radiusX
        self._radiusY = radiusY
        self._window.refresh(start=self)

    # overwrite
    # rotating an oval efficiently works differently
    def rotate(self, degrees):
        _check_type(degrees, "degrees", int)

        self._degrees += degrees
        self._center = _rotate_helper(self._center,
                                      degrees * math.pi / 180.0,
                                      self._pivot)
        self._window.refresh(start=self)

    # overwrite
    # scaling an oval works differently
    def scale(self, factor):
        _check_type(factor, "factor", float)

        self._radiusX = round(self._radiusX * factor)
        self._radiusY = round(self._radiusY * factor)
        self._window.refresh(start=self)

    def _move_graphic(self, dx, dy):
        pass

    def _add(self):
        if not self._enabled:
            self._tag = self._window._canvas.create_polygon(
                *_oval_gen(self._center,
                           self._radiusX,
                           self._radiusY,
                           degrees = self._degrees),
                width=self.get_border_width(),
                fill=self.get_fill_color(),
                outline=self.get_border_color())

            self._update_graphic_list()

            self._enabled = True

def _oval_gen(center, radiusX, radiusY, degrees=0, divisions=40):
    angle = degrees * math.pi / 180.0
    
    points = []
    for i in range(divisions):
        theta = 2.0 * math.pi * float(i) / divisions

        x1 = radiusX * math.cos(theta)
        y1 = radiusY * math.sin(theta)

        # rotate
        x = x1 * math.cos(angle) + y1 * math.sin(angle)
        y = y1 * math.cos(angle) - x1 * math.sin(angle)

        points.append((round(x + center[0]),
                       round(y + center[1])))

    return points

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

    ## Sets the side length of the Square.
    # @param side_length - int
    def set_side_length(self, side_length):
        # type checking
        _check_type(side_length, "side_length", int)

        # equivalent to scale
        self.scale(side_length / self._side_length)

        self._side_length = side_length
        self._window.refresh(start=self)

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
        _check_type(width, "width", int)
        _check_type(height, "height", int)

        self._width = width
        self._height = height

        points = [(center[0] - width // 2,
                   center[1] - height // 2),
                  (center[0] + width // 2,
                   center[1] - height // 2),
                  (center[0] + width // 2,
                   center[1] + height // 2),
                  (center[0] - width // 2,
                   center[1] + height // 2)]

        Fillable.__init__(self,
                          window = window,
                          center = center,
                          points = points,
                          pivot = center)

    ## Sets the width and height of the Rectangle.
    # @param width - int
    # @param height - int
    def set_side_lengths(self, width, height):
        # type checking
        _check_type(width, "width", int)
        _check_type(height, "height", int)

        self._width = width
        self._height = height
        # re-rendering each corner point and refreshing
        self._points = [(self._center[0] - self._width // 2,
                         self._center[1] - self._height // 2),
                        (self._center[0] + self._width // 2,
                         self._center[1] - self._height // 2),
                        (self._center[0] + self._width // 2,
                         self._center[1] + self._height // 2),
                        (self._center[0] - self._width // 2,
                         self._center[1] + self._height // 2)]
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
        _check_type(window, "window", Window)
        _check_type(interval, "interval", int)
        _check_function(func, "func")

        
        
        self._window = window
        self._func = func
        self._interval = interval

    ## Sets the function which is going to be run.
    # @param func - function
    def set_function(self, func):
        _check_function(func, "func")
        
        self._func = func

    ## Sets the interval between executions of the function.
    # @param interval - int
    def set_interval(self, interval):
        _check_type(interval, "interval", int)

        self._interval = interval

    ## Starts the timer.
    def start(self):
        self._func()
        self._window._refresh()
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
    _check_type(window, "window", Window)
    _check_generator(func, "func")

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
        _check_type(window, "window", Window)
        _check_generator(func, "func")
    
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
            delay = -1

        # update the window
        self._window._refresh()

        if delay >= 0:
            self._tag = self._window._root.after(delay, self._run)
        else:
            self._window._root.after_cancel(self._tag)
