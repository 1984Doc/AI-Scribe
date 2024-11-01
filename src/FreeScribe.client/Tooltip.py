# This module provides a Tooltip class to display tooltips for Tkinter widgets.
# The Tooltip class is adapted from a solution on Stack Overflow.
# https://stackoverflow.com/questions/3221956/how-do-i-display-tooltips-in-tkinter

import tkinter as tk

# Tooltip class
# This class creates a tooltip for a given widget.
# It handles the scheduling and display of the tooltip when the mouse enters the widget,
# and hides the tooltip when the mouse leaves the widget.
class Tooltip(object):
    """
    Create a tooltip for a given widget.

    This class creates a tooltip for a given widget. It handles the scheduling and display
    of the tooltip when the mouse enters the widget, and hides the tooltip when the mouse
    leaves the widget.

    :param widget: The widget to which the tooltip will be attached.
    :type widget: tkinter.Widget
    :param text: The text to display in the tooltip.
    :type text: str, optional
    """
    def __init__(self, widget, text='widget info'):
        """
        Initialize the Tooltip object.

        :param widget: The widget to which the tooltip will be attached.
        :type widget: tkinter.Widget
        :param text: The text to display in the tooltip.
        :type text: str, optional
    #     """
    #     self.waittime = 500     # milliseconds
    #     self.wraplength = 180   # pixels
    #     self.widget = widget
    #     self.text = text
    #     self.widget.bind("<Enter>", self.enter)
    #     self.widget.bind("<Leave>", self.leave)
    #     self.widget.bind("<ButtonPress>", self.leave)
    #     self.ttid = None
    #     self.tw = None

    # def enter(self, event=None):
    #     """
    #     Schedule the tooltip to be shown when the mouse enters the widget.

    #     :param event: The event object.
    #     :type event: tkinter.Event, optional
    #     """
    #     self.schedule()

    # def leave(self, event=None):
    #     """
    #     Unschedule the tooltip and hide it when the mouse leaves the widget.

    #     :param event: The event object.
    #     :type event: tkinter.Event, optional
    #     """
    #     self.unschedule()
    #     self.hidetip()

    # def schedule(self):
    #     """
    #     Schedule the tooltip to be shown after a delay.
    #     """
    #     self.unschedule()
    #     self.ttid = self.widget.after(self.waittime, self.showtip)

    # def unschedule(self):
    #     """
    #     Cancel the scheduled tooltip if it exists.
    #     """
    #     ttid = self.ttid
    #     self.ttid = None
    #     if ttid:
    #         self.widget.after_cancel(ttid)

    # def showtip(self, event=None):
    #     """
    #     Show the tooltip.

    #     :param event: The event object.
    #     :type event: tkinter.Event, optional
    #     """
    #     x = y = 0
    #     x, y, cx, cy = self.widget.bbox("insert")
    #     x += self.widget.winfo_rootx() + 25
    #     y += self.widget.winfo_rooty() + 20
    #     # creates a toplevel window
    #     self.tw = tk.Toplevel(self.widget)
    #     # Leaves only the label and removes the app window
    #     self.tw.wm_overrideredirect(True)
    #     self.tw.wm_geometry("+%d+%d" % (x, y))
    #     label = tk.Label(self.tw, text=self.text, justify='left',
    #                    background="#ffffff", relief='solid', borderwidth=1,
    #                    wraplength = self.wraplength)
    #     label.pack(ipadx=1)

    # def hidetip(self):
    #     """
    #     Hide the tooltip.
    #     """
    #     tw = self.tw
    #     self.tw= None
    #     if tw:
    #         tw.destroy()
