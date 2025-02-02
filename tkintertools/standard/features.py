"""All standard `Feature` classes"""

from __future__ import annotations

__all__ = [
    "BaseFeature",
    "LabelFeature",
    "ButtonFeature",
    "Underline",
    "Highlight",
    "SwitchFeature",
    "ToggleButtonFeature",
    "CheckButtonFeature",
    "RadioButtonFeature",
    "ProgressBarFeature",
    "InputBoxFeature",
    "SliderFeature",
    "SpinBoxFeature",
]

import collections.abc
import tkinter
import typing

from ..animation import animations, controllers
from ..core import virtual
from ..standard import shapes


class BaseFeature(virtual.Feature):
    """Base Feature"""

    def _motion(self, event: tkinter.Event) -> bool:
        return self.widget.shapes[0].detect(event.x, event.y)


class LabelFeature(virtual.Feature):
    """Feature of Label"""

    def _motion(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            self.widget.master.trigger_config.update(cursor="arrow")
            if self.widget.state != "hover":
                self.widget.update("hover")
        else:
            if self.widget.state != "normal":
                self.widget.update("normal")
        return flag


class ButtonFeature(virtual.Feature):
    """Feature of Button"""

    def __init__(
        self,
        widget: virtual.Widget,
        *,
        command: collections.abc.Callable | None = None,
        args: tuple = (),
    ) -> None:
        """
        * `widget`: parent widget
        * `command`: callback function
        * `args`: arguments of callback function
        """
        virtual.Feature.__init__(self, widget)
        self.command: collections.abc.Callable = command
        self._args: tuple = args

    def _motion(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            self.widget.master.trigger_config.update(cursor="hand2")
            if self.widget.state == "normal":
                self.widget.update("hover")
        else:
            if self.widget.state != "normal":
                self.widget.update("normal")
        return flag

    def _b_1_motion(self, event: tkinter.Event) -> bool:
        return self._motion(event)

    def _b_2_motion(self, event: tkinter.Event) -> bool:
        return self._motion(event)

    def _b_3_motion(self, event: tkinter.Event) -> bool:
        return self._motion(event)

    def _button_1(self, _: tkinter.Event) -> bool:
        if flag := self.widget.state == "hover":
            self.widget.update("active")
        return flag

    def _button_release_1(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            if self.widget.state == "active":
                self.widget.update("hover")
                if self.command is not None:
                    self.command(*self._args)
        return flag


class Underline(ButtonFeature):
    """Feature of underline"""

    def _motion(self, event: tkinter.Event) -> bool:
        if flag := self.widget.texts[0].detect(event.x, event.y):
            self.widget.master.trigger_config.update(cursor="hand2")
            if self.widget.state == "normal":
                self.widget.update("hover")
                self.widget.texts[0].font.config(underline=True)
        else:
            if self.widget.state != "normal":
                self.widget.update("normal")
                self.widget.texts[0].font.config(underline=False)
        return flag

    def _button_1(self, _: tkinter.Event) -> bool:
        if flag := self.widget.state == "hover":
            self.widget.update("active")
        return flag

    def _button_release_1(self, event: tkinter.Event) -> bool:
        if flag := self.widget.texts[0].detect(event.x, event.y):
            if self.widget.state == "active":
                self.widget.update("hover")
                self.widget.texts[0].font.config(underline=True)
                if self.command is not None:
                    self.command(*self._args)
        return flag


class Highlight(ButtonFeature):
    """Feature of highlight"""

    def _motion(self, event: tkinter.Event) -> bool:
        if flag := self.widget.texts[0].detect(event.x, event.y):
            self.widget.master.trigger_config.update(cursor="hand2")
            if self.widget.state == "normal":
                self.widget.update("hover")
                animations.ScaleFontSize(self.widget.texts[0], 150, sizes=28).start()
        else:
            if self.widget.state != "normal":
                self.widget.update("normal")
                animations.ScaleFontSize(self.widget.texts[0], 150, sizes=24).start()
        return flag

    def _button_1(self, _: tkinter.Event) -> bool:
        if flag := self.widget.state == "hover":
            self.widget.update("active")
            animations.ScaleFontSize(self.widget.texts[0], 150, sizes=26).start()
        return flag

    def _button_release_1(self, event: tkinter.Event) -> bool:
        if flag := self.widget.texts[0].detect(event.x, event.y):
            if self.widget.state == "active":
                self.widget.update("hover")
                animations.ScaleFontSize(self.widget.texts[0], 150, sizes=28).start()
                if self.command is not None:
                    self.command(*self._args)
        return flag


class SwitchFeature(ButtonFeature):
    """Feature of Switch"""

    def _motion(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            self.widget.master.trigger_config.update(cursor="hand2")
            if self.widget.state.startswith("normal"):
                if self.widget.state != "disabled":
                    self.widget.shapes[-1].coords(
                        (self.widget.size[0]/3, self.widget.size[0]/3),
                        (self.widget.shapes[-1].position[0] - self.widget.size[0]/60,
                         self.widget.shapes[-1].position[1] - self.widget.size[0]/60))
                self.widget.update(f"hover-{'on' if self.widget.get() else 'off'}")
        else:
            if not self.widget.state.startswith("normal"):
                if self.widget.state != "disabled":
                    self.widget.shapes[-1].coords(
                        (self.widget.size[0]*3/10, self.widget.size[0]*3/10),
                        (self.widget.shapes[-1].position[0] + self.widget.size[0]/60,
                         self.widget.shapes[-1].position[1] + self.widget.size[0]/60))
                self.widget.update(f"normal-{'on' if self.widget.get() else 'off'}")
        return flag

    def _button_1(self, _: tkinter.Event) -> bool:
        if flag := self.widget.state.startswith("hover"):
            self.widget.update(f"active-{'on' if self.widget.get() else 'off'}", no_delay=True)
        return flag

    def _button_release_1(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            if self.widget.state.startswith("active"):
                boolean = not self.widget.get()
                self.widget.set(boolean)
                self.widget.update(f"hover-{'on' if boolean else 'off'}", no_delay=True)
                if self.command is not None:
                    self.command(boolean)
        return flag


class CheckButtonFeature(ButtonFeature):
    """Feature of CheckButton"""

    def _button_1(self, _: tkinter.Event) -> bool:
        if flag := self.widget.state == "hover":
            self.widget.update("active", no_delay=True)
        return flag

    def _button_release_1(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            if self.widget.state == "active":
                self.widget.set(boolean := not self.widget.get())
                self.widget.update("hover", no_delay=True)
                if self.command is not None:
                    self.command(boolean)
        return flag


class ToggleButtonFeature(ButtonFeature):
    """Feature of ToggleButton"""

    def _motion(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            self.widget.master.trigger_config.update(cursor="hand2")
            if self.widget.state.startswith("normal"):
                self.widget.update(f"hover-{'on' if self.widget.get() else 'off'}")
        else:
            if not self.widget.state.startswith("normal"):
                self.widget.update(f"normal-{'on' if self.widget.get() else 'off'}")
        return flag

    def _button_1(self, _: tkinter.Event) -> bool:
        if flag := self.widget.state.startswith("hover"):
            self.widget.update(f"active-{'on' if self.widget.get() else 'off'}")
        return flag

    def _button_release_1(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            if self.widget.state.startswith("active"):
                boolean = not self.widget.get()
                self.widget.set(boolean)
                self.widget.update(f"hover-{'on' if boolean else 'off'}")
                if self.command is not None:
                    self.command(boolean)
        return flag


class RadioButtonFeature(CheckButtonFeature):
    """Feature of RadioButton"""


class ProgressBarFeature(LabelFeature):
    """Feature of ProgressBar"""


class InputBoxFeature(ButtonFeature):
    """Feature of input box"""

    def __init__(
        self,
        widget: virtual.Widget,
        *,
        command: collections.abc.Callable[..., typing.Any] | None = None,
        args: tuple = (),
    ) -> None:
        super().__init__(widget, command=command, args=args)
        self._start_index: int | None = None
        self._end_index: int | None = None

    def _motion(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            self.widget.master.trigger_config.update(cursor="xterm")
            if self.widget.state == "normal":
                self.widget.update("hover")
        else:
            if self.widget.state == "hover":
                self.widget.update("normal")
        return flag

    def _button_1(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[0].detect(event.x, event.y):
            self.widget.update("active")
            if self.widget.state == "active":  # Maybe widget is disabled
                self.widget.master.trigger_focus.update(True, self.widget.texts[0].items[0])
                self._start_index = self.widget.texts[0].text_proxy.cursor_find(event.x)
                self.widget.texts[0].text_proxy.cursor_set(self._start_index)
                self.widget.master.itemconfigure(self.widget.texts[0].items[1], fill="")
        else:
            if self.widget.state != "normal":
                self.widget.update("normal")
                if not self.widget.texts[0].get():
                    self.widget.master.itemconfigure(
                        self.widget.texts[0].items[1], fill="#787878")
        self.widget.texts[0].text_proxy.select_clear()
        return flag

    def _b_1_motion(self, event: tkinter.Event) -> bool:
        if self.widget.state == "active":
            self.widget.master.trigger_config.update(cursor="xterm")
            self._end_index = self.widget.texts[0].text_proxy.cursor_find(event.x)
            self.widget.texts[0].text_proxy.cursor_set(self._end_index)
            if self._start_index < self._end_index:
                self.widget.texts[0].text_proxy.select_set(self._start_index, self._end_index)
            elif self._start_index > self._end_index:
                self.widget.texts[0].text_proxy.select_set(self._end_index, self._start_index)
            else:
                self.widget.texts[0].text_proxy.select_clear()
            return True
        return False

    def _button_release_1(self, _: tkinter.Event) -> bool:
        return False

    def _key_press(self, event: tkinter.Event) -> bool:
        if self.widget.state == "active":
            select = self.widget.texts[0].text_proxy.select_get()
            match event.keysym:
                case "Right":
                    if select is None:
                        self.widget.texts[0].cursor_move(1)
                    else:
                        self.widget.texts[0].text_proxy.select_clear()
                        self.widget.texts[0].cursor_move_to(select[1])
                case "Left":
                    if select is None:
                        self.widget.texts[0].cursor_move(-1)
                    else:
                        self.widget.texts[0].text_proxy.select_clear()
                        self.widget.texts[0].cursor_move_to(select[0])
                case "BackSpace" | "Delete":
                    if select is not None:
                        self.widget.texts[0].text_proxy.select_clear()
                        self.widget.texts[0].remove(*select)
                    else:
                        index = self.widget.texts[0].text_proxy.cursor_get()
                        if event.keysym == "BackSpace":
                            if index > 0:
                                self.widget.texts[0].remove(index - 1)
                        else:
                            if index < self.widget.texts[0].text_proxy.length():
                                self.widget.texts[0].remove(index)
                case _:
                    if len(event.char) and event.char.isprintable():
                        if select is not None:
                            self.widget.texts[0].text_proxy.select_clear()
                            self.widget.texts[0].remove(*select)
                        self.widget.texts[0].insert(
                            self.widget.texts[0].text_proxy.cursor_get(), event.char)
        return False

    def _copy(self, _: tkinter.Event) -> bool:
        if flag := self.widget.state == "active":
            select = self.widget.texts[0].text_proxy.select_get()
            if select is not None:
                self.widget.master.clipboard_clear()
                self.widget.master.clipboard_append(
                    self.widget.texts[0].text_proxy.get()[select[0]: select[1]])
        return flag

    def _paste(self, _: tkinter.Event) -> bool:
        if flag := self.widget.state == "active":
            select = self.widget.texts[0].text_proxy.select_get()
            if select is not None:
                self.widget.texts[0].text_proxy.select_clear()
                self.widget.texts[0].remove(*select)
            if value := self.widget.master.clipboard_get():
                self.widget.texts[0].append(value)
        return flag

    def _cut(self, event: tkinter.Event) -> bool:
        if flag := self._copy(event):
            select = self.widget.texts[0].text_proxy.select_get()
            if select is not None:
                self.widget.texts[0].remove(*select)
                self.widget.texts[0].text_proxy.select_clear()
        return flag

    def _select_all(self, _: tkinter.Event) -> bool:
        if flag := self.widget.state == "active":
            self.widget.texts[0].text_proxy.select_all()
        return flag


class SliderFeature(virtual.Feature):
    """Feature of Slider"""

    def __init__(self, widget: virtual.Widget) -> None:
        super().__init__(widget)
        self._temp_position: tuple[float, float] | None = None

    def _motion(self, event: tkinter.Event) -> bool:
        if flag := self.widget.shapes[2].detect(event.x, event.y):
            if self.widget.state == "normal":
                self.widget.update("hover")
                if isinstance(self.widget.shapes[-1], shapes.Oval):
                    self.widget.shapes[-1].coords(
                        (self.widget.size[1]*2/3, self.widget.size[1]*2/3),
                        (self.widget.shapes[-2].position[0] + self.widget.size[1]/6,
                         self.widget.shapes[-2].position[1] + self.widget.size[1]/6))
        else:
            if self.widget.state == "hover":
                self.widget.update("normal")
                if isinstance(self.widget.shapes[-1], shapes.Oval):
                    self.widget.shapes[-1].coords(
                        (self.widget.size[1]/2, self.widget.size[1]/2),
                        (self.widget.shapes[-2].position[0] + self.widget.size[1]/4,
                         self.widget.shapes[-2].position[1] + self.widget.size[1]/4))
        return flag

    def _button_1(self, event: tkinter.Event) -> bool:
        if self.widget.state == "hover":
            self._temp_position = event.x, event.y
            self.widget.update("active")
        elif self.widget.state != "disabled" and self.widget.shapes[0].detect(event.x, event.y):
            self._temp_position = event.x, event.y
            self.widget.update("active")
            temp_value = self.widget.value
            if isinstance(self.widget.shapes[-1], shapes.Oval):
                self.widget.shapes[-1].coords(
                    (self.widget.size[1]*2/3, self.widget.size[1]*2/3),
                    (self.widget.shapes[-2].position[0] + self.widget.size[1]/6,
                     self.widget.shapes[-2].position[1] + self.widget.size[1]/6))
                next_value = (
                    (event.x-self.widget.position[0]-self.widget.size[1]/2)
                    / (self.widget.size[0]-self.widget.size[1]))
            else:
                next_value = (
                    (event.x-self.widget.position[0]-self.widget.size[1]/5)
                    / (self.widget.size[0]-self.widget.size[1]*2/5))
            delta = next_value - temp_value
            animations.Animation(
                150, controllers.smooth,
                callback=lambda k: self.widget.set(
                    temp_value + delta*k, callback=True), fps=60).start()

    def _b_1_motion(self, event: tkinter.Event) -> bool:
        if self._temp_position is not None:
            if isinstance(self.widget.shapes[-1], shapes.Oval):
                delta = (event.x-self._temp_position[0]) / (self.widget.size[0]-self.widget.size[1])
            else:
                delta = ((event.x-self._temp_position[0])
                         / (self.widget.size[0]-self.widget.size[1]*2/5))
            self._temp_position = event.x, event.y
            self.widget.set(self.widget.value + delta, callback=True)

    def _button_release_1(self, _: tkinter.Event) -> bool:
        if self.widget.state == "active":
            self._temp_position = None
            self.widget.update("hover")


class SpinBoxFeature(virtual.Feature):
    """Feature of SpinBox"""

    def __init__(
        self,
        widget: virtual.Widget,
        *,
        command: collections.abc.Callable[[bool], typing.Any] | None = None,
    ) -> None:
        """
        * `widget`: parent widget
        * `command`: callback function
        """
        virtual.Feature.__init__(self, widget)
        self.command: collections.abc.Callable = command
        if self.command is None:
            self.command = self.widget.change

    def _mouse_wheel(self, event: tkinter.Event) -> bool:
        if flag := self.widget.widgets[0].state == "active":
            self.command(event.delta > 0)
        return flag
