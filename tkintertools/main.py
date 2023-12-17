"""Main File"""

import fractions
import math
import tkinter
import typing

from .constants import *
from .exceptions import *

if SYSTEM == "Windows":
    from ctypes import windll
    windll.shcore.SetProcessDpiAwareness(1)

try:
    from PIL import Image, ImageTk
except ImportError:
    Image = None


class Tk(tkinter.Tk):
    """根窗口容器控件"""

    def __init__(
        self,
        title=None,  # type: str | None
        width=None,  # type: int | None
        height=None,  # type: int | None
        x=None,  # type: int | None
        y=None,  # type: int | None
        *,
        shutdown=None,  # type: typing.Callable | None
        alpha=None,  # type: float | None
        toolwindow=None,  # type: bool | None
        topmost=None,  # type: bool | None
        transparentcolor=None,  # type: str | None
        **kw
    ):  # type: (...) -> None
        """
        * `title`: 窗口标题
        * `width`: 窗口宽度
        * `height`: 窗口高度
        * `x`: 窗口左上角横坐标
        * `y`: 窗口左上角纵坐标
        * `shutdown`: 关闭窗口之前执行的函数，但会覆盖原关闭操作
        * `alpha`: 窗口的透明度，取值在 0 ~ 1 之间，且 1 为不透明
        * `toolwindow`: 窗口是否为工具窗口
        * `topmost`: 窗口是否置顶，为布尔值
        * `transparentcolor`: 过滤掉该颜色
        * `**kw`: 与 `tkinter.Tk` 类的其他参数相同
        """
        if type(self) == Tk:  # NOTE: 方便后面的 Toplevel 类继承，只继承一部分功能
            tkinter.Tk.__init__(self, **kw)

        self.width = [100, 1]  # type: list[int]  # [初始宽度, 当前宽度]
        self.height = [100, 1]  # type: list[int]  # [初始高度, 当前高度]
        self._canvas = []  # type: list[Canvas]  # 子画布列表

        if width is not None and height is not None:
            if x is not None and y is not None:
                self.geometry(f"{width}x{height}+{x}+{y}")
            else:
                self.geometry(f"{width}x{height}")

        if title is not None:
            self.title(title)
        if alpha is not None:
            self.attributes("-alpha", alpha)
        if toolwindow is not None:
            self.attributes("-toolwindow", toolwindow)
        if topmost is not None:
            self.attributes("-topmost", topmost)
        if transparentcolor is not None:
            self.attributes("-transparentcolor", transparentcolor)

        self.minsize(200, 200)
        self.protocol("WM_DELETE_WINDOW", shutdown if shutdown else None)
        self.bind("<Configure>", lambda _: self._zoom())  # 开启窗口缩放检测

    def canvas(self):  # type: () -> tuple[Canvas]
        """返回 `Tk` 类全部的 `Canvas` 对象"""
        return tuple(self._canvas)

    def _zoom(self):  # type: () -> None
        """缩放检测"""
        width, height = map(int, self.geometry().split("+")[0].split("x"))

        if width == self.width[1] and height == self.height[1]:  # 没有大小的改变
            return

        for canvas in self._canvas:
            if canvas.expand and canvas._lock:
                canvas._zoom(width / self.width[1], height / self.height[1])

        self.width[1], self.height[1] = width, height  # 更新窗口当前的宽高值

    def wm_geometry(self, newGeometry=None):  # type: (str | None) -> str | None
        # override: 添加修改初始宽高值的功能并兼容不同的 DPI 缩放
        if newGeometry:
            width, height, _width, _height, *_ = \
                (newGeometry + "+0+0").replace("+", "x").split("x")
            if width != "":
                width = int(width)
                height = int(height)
            if _width != "":
                _width = int(_width)
                _height = int(_height)

            self.width, self.height = [width, width], [height, height]
            if width != "":
                geometry = f"{width}x{height}+{_width}+{_height}"
            else:
                geometry = f"+{_width}+{_height}"
            if not _:
                geometry = geometry.split("+")[0]
            return tkinter.Tk.wm_geometry(self, geometry)
        geometry = tkinter.Tk.wm_geometry(self, newGeometry)
        width, height, _width, _height, *_ = \
            map(int, (geometry + "+0+0").replace("+", "x").split("x"))
        return f"{width}x{height}+{_width}+{_height}"

    geometry = wm_geometry


class Toplevel(tkinter.Toplevel, Tk):
    """子窗口容器控件"""

    def __init__(
        self,
        master=None,  # type: Tk | None
        title=None,  # type: str | None
        width=None,  # type: int | None
        height=None,  # type: int | None
        x=None,  # type: int | None
        y=None,  # type: int | None
        *,
        shutdown=None,  # type: typing.Callable | None
        alpha=None,  # type: float | None
        toolwindow=None,  # type: bool | None
        topmost=None,  # type: bool | None
        transparentcolor=None,  # type: str | None
        **kw
    ):  # type: (...) -> None
        """
        * `master`: 父窗口
        * `title`: 窗口标题
        * `width`: 窗口宽度
        * `height`: 窗口高度
        * `x`: 窗口左上角横坐标
        * `y`: 窗口左上角纵坐标
        * `shutdown`: 关闭窗口之前执行的函数，但会覆盖关闭操作
        * `alpha`: 窗口的透明度，取值在 0 ~ 1 之间，且 1 为不透明
        * `toolwindow`: 窗口是否为工具窗口
        * `topmost`: 窗口是否置顶，为布尔值
        * `transparentcolor`: 过滤掉该颜色
        * `**kw`: 与 `tkinter.Toplevel` 类的参数相同
        """
        tkinter.Toplevel.__init__(self, master, **kw)
        Tk.__init__(self, title, width, height, x, y, shutdown=shutdown, alpha=alpha,
                    toolwindow=toolwindow, topmost=topmost, transparentcolor=transparentcolor, **kw)
        self.focus_set()  # 把焦点转移到该子窗口上来


class Canvas(tkinter.Canvas):
    """画布容器控件"""

    def __init__(
        self,
        master,  # type: Tk | Toplevel
        width,  # type: int
        height,  # type: int
        x=None,  # type: int | None
        y=None,  # type: int | None
        *,
        lock=True,  # type: bool
        expand=True,  # type: bool
        keep=False,  # type: bool
        **kw
    ):  # type: (...) -> None
        """
        * `master`: 父控件
        * `width`: 画布宽度
        * `height`: 画布高度
        * `x`: 画布左上角的横坐标
        * `y`: 画布左上角的纵坐标
        * `lock`: 画布内控件的功能锁，为 `False` 时功能暂时失效
        * `expand`: 画布内控件是否能缩放
        * `keep`: 画布比例是否保持不变
        * `**kw`: 与 `tkinter.Canvas` 类的参数相同
        """
        self.width = [width, width]  # [初始宽度, 当前宽度]
        self.height = [height, height]  # [初始高度, 当前高度]
        self._lock = lock
        self.expand = expand
        self.keep = keep

        self.master = master  # type: Tk | Toplevel  # NOTE: 此语句虽冗余，实则为类型提示

        self.rx = 1.  # 横向放缩比率
        self.ry = 1.  # 纵向放缩比率
        self._widget = []  # type: list[BaseWidget]  # 子控件列表（与事件绑定有关）
        self._font = {}  # type: dict[int, float]
        self._image = {}  # type: dict[int, list]

        tkinter.Canvas.__init__(self, master, width=width,
                                height=height, highlightthickness=0, **kw)

        master._canvas.append(self)  # 将实例添加到 Tk 的画布列表中
        if x is not None and y is not None:
            self.place(x=x, y=y)

        self.bind("<Motion>", self._touch)  # 绑定鼠标触碰控件
        self.bind("<Any-Key>", self._input)  # 绑定键盘输入字符（和 Ctrl+v 的代码顺序不可错）
        self.bind("<Button-1>", self._click)  # 绑定鼠标左键按下
        self.bind("<B1-Motion>", self._click)  # 绑定鼠标左键按下移动
        self.bind("<ButtonRelease-1>", self._release)  # 绑定鼠标左键松开
        self.bind("<<Paste>>", lambda _: self._paste())  # 绑定粘贴快捷键

    def widget(self):  # type: () -> tuple[BaseWidget]
        """返回 `Canvas` 类全部的 `BaseWidget` 对象"""
        return tuple(self._widget)

    @typing.overload
    def lock(self, value):  # type: (bool) -> None
        ...

    @typing.overload
    def lock(self):  # type: () -> None
        ...

    def lock(self, value=None):  # type: (bool | None) -> bool | None
        """设置或查询画布锁的状态

        * `value`: 为 `True` 则可操作，为 `False` 则反之，无参数或参数为 `None` 则返回当前值
        """
        if value is None:
            return self._lock
        self._lock = value
        if value and self.expand:
            self._zoom()

    def _zoom(self, rate_x=None, rate_y=None):  # type: (float | None, float | None) -> None
        """缩放画布及其内部的所有元素

        * `rate_x`: 横向缩放比率，默认值表示自动更新缩放（根据窗口缩放程度）
        * `rate_y`: 纵向缩放比率，默认值同上
        """
        if not rate_x:
            rate_x = self.master.width[1] / self.master.width[0] / self.rx
        if not rate_y:
            rate_y = self.master.height[1] / self.master.height[0] / self.ry

        rate_x_pos, rate_y_pos = rate_x, rate_y  # 避免受 keep 影响

        if self.keep:  # 维持比例
            rx = rate_x * self.master.width[1] / self.master.width[0] / self.rx
            ry = rate_y * self.master.height[1] / \
                self.master.height[0] / self.ry
            rate_x = rate_y = min(rx, ry)

        # 更新画布的位置及大小的数据
        self.width[1] *= rate_x
        self.height[1] *= rate_y
        temp_x, self.rx = self.rx, self.width[1] / self.width[0]
        temp_y, self.ry = self.ry, self.height[1] / self.height[0]

        place_info = self.place_info()
        tkinter.Canvas.place(  # 更新画布的位置及大小
            self,
            width=self.width[1],
            height=self.height[1],
            x=float(place_info["x"]) * rate_x_pos,
            y=float(place_info["y"]) * rate_y_pos)

        for widget in self._widget:  # 更新子画布控件的子虚拟画布控件位置数据
            widget.x1 *= rate_x
            widget.x2 *= rate_x
            widget.y1 *= rate_y
            widget.y2 *= rate_y

        for item in self.find_all():  # item 位置缩放
            self.coords(item, *[c * (rate_x, rate_y)[i & 1]
                        for i, c in enumerate(self.coords(item))])

        for item in self._font:  # 字体大小缩放
            self._font[item][1] *= math.sqrt(rate_x*rate_y)
            font = self._font[item][:]
            font[1] = round(font[1])
            self.itemconfigure(item, font=font)

        for item in self._image:  # 图像大小缩放（采用相对的绝对缩放）
            if self._image[item][0] and self._image[item][0].extension != "gif":
                self._image[item][1] = self._image[item][0].zoom(
                    temp_x * rate_x, temp_y * rate_y, precision=1.2)
                self.itemconfigure(item, image=self._image[item][1])

    def _touch(self, event, flag=True):  # type: (tkinter.Event, bool) -> None
        """鼠标触碰控件事件"""
        if self._lock:
            for widget in self._widget[::-1]:
                if widget.live and widget._touch(event) and flag:
                    if isinstance(widget, TextWidget):
                        self.configure(cursor="xterm")
                    elif isinstance(widget, Button):
                        self.configure(cursor="hand2")
                    else:
                        self.configure(cursor="arrow")
                    flag = False
                    event.x = math.inf  # NOTE: 让其他控件失去“焦点”，就算鼠标在其范围内

            if flag:
                self.configure(cursor="arrow")

    def _click(self, event):  # type: (tkinter.Event) -> bool
        """鼠标左键按下事件"""
        if self._lock:
            self.focus_set()
            flag = False
            for widget in self._widget[::-1]:
                if widget.live and isinstance(widget, (Button, TextWidget)):
                    if widget._click(event) and not flag:  # NOTE: not flag 和 and 不可互换位置
                        flag = True
                        # 此处无需直接 return，按下空白区域也有作用
            if flag:
                return True
        return False

    def _release(self, event):  # type: (tkinter.Event) -> bool
        """鼠标左键松开事件"""
        if self._lock:
            for widget in self._widget[::-1]:
                if widget.live and isinstance(widget, Button):
                    # _state 先导判断，必须是点击后才可触发调用
                    if widget._state == "click" and widget._touch(event):
                        widget._execute(event)
                        return True
                    else:
                        widget._touch(event)
        return False

    def _input(self, event):  # type: (tkinter.Event) -> None
        """键盘输入字符事件"""
        if self._lock:
            for widget in self._widget[::-1]:
                if widget.live and isinstance(widget, TextWidget):
                    if widget._input(event):
                        return

    def _paste(self):  # type: () -> None
        """快捷键粘贴事件"""
        if self._lock:
            for widget in self._widget[::-1]:
                if widget.live and isinstance(widget, TextWidget):
                    if widget._paste():
                        return

    def create_text(self, *args, **kw):  # type: (...) -> int
        # override: 添加对 text 类型的 _CanvasItemId 的字体大小的控制
        font = kw.get("font")
        if not font:
            kw["font"] = FONT, SIZE
        elif isinstance(font, str):
            kw["font"] = font, SIZE
        elif kw["font"][1] > 0:
            kw["font"] = list(kw["font"])
            kw["font"][1] = -kw["font"][1]
        item = tkinter.Canvas.create_text(self, *args, **kw)
        self._font[item] = list(kw["font"])
        return item

    def create_image(self, *args, **kw):  # type: (...) -> int
        # override: 添加对 image 类型的 _CanvasItemId 的图像大小的控制
        item = tkinter.Canvas.create_image(self, *args, **kw)
        self._image[item] = [kw.get("image"), None]
        return item

    def itemconfigure(self, tagOrId, **kw):
        # type: (str | int, ...) -> dict[str, tuple[str, str, str, str, str]] | None
        # override: 创建空 image 的 _CanvasItemId 时漏去对图像大小的控制
        if type(kw.get("image")) == PhotoImage:
            self._image[tagOrId] = [kw.get("image"), None]
        return tkinter.Canvas.itemconfigure(self, tagOrId, **kw)

    def place(self, *args, **kw):  # type: (...) -> None  # BUG: 缩放就会恢复原样
        # override: 增加一些特定功能
        self.width[0] = kw.get("width", self.width[0])
        self.height[0] = kw.get("height", self.height[0])
        return tkinter.Canvas.place(self, *args, **kw)

    def destroy(self):  # type: () -> None
        # override: 兼容 tkinter
        self.master._canvas.remove(self)
        for widget in self.widget():
            widget.destroy()
        return tkinter.Canvas.destroy(self)


class BaseWidget:
    """虚拟画布控件基类"""

    def __init__(
        self,
        canvas,  # type:  Canvas
        x,  # type: float
        y,  # type: float
        width,  # type: float
        height,  # type: float
        radius,  # type: float
        text,  # type: str
        justify,  # type: str
        borderwidth,  # type: float
        font,  # type: tuple[str, int, str]
        image,  # type: PhotoImage | None
        tooltip,  # type: ToolTip | None
        color_text,  # type: tuple[str, str, str]
        color_fill,  # type: tuple[str, str, str]
        color_outline  # type: tuple[str, str, str]
    ):  # type: (...) -> None
        """
        标准参数：标准参数是所有控件都有的 

        * `canvas`: 父画布容器控件
        * `x`: 控件左上角的横坐标
        * `y`: 控件左上角的纵坐标
        * `width`: 控件的宽度
        * `height`: 控件的高度
        * `radius`: 控件圆角化半径
        * `text`: 控件显示的文本，对于文本控件而言，可以为一个元组：(默认文本, 鼠标触碰文本)
        * `justify`: 文本的对齐方式
        * `borderwidth`: 外框的宽度
        * `font`: 控件的字体设定 (字体, 大小, 样式)
        * `image`: 控件的背景（支持 png 类型，大小必须小于控件，否则会溢出控件边框）
        * `tooltip`: 提示框
        * `color_text`: 控件文本的颜色
        * `color_fill`: 控件内部的颜色
        * `color_outline`: 控件外框的颜色

        特定参数：特定参数只有某些控件类才有 

        * `command`: 按钮控件的关联函数
        * `show`: 文本控件的显示文本
        * `limit`: 文本控件的输入字数限制，为负数时表示没有字数限制
        * `read`: 文本控件的只读模式
        * `cursor`: 文本控件输入提示符的字符，默认为一竖线
        * `mode`: 进度条控件的模式，`determinate` 为确定模式，`indeterminate` 为不定模式，默认为前者
        * `tick`: 复选框控件的标记符号，默认为一个“对号”

        详细说明

        1. 字体的值为一个包含两个或三个值的元组或者单个的字符串，共三种形式:
             * 形式一: `字体名称`
             * 形式二: `(字体名称, 字体大小)`
             * 形式三: `(字体名称, 字体大小, 字体样式)`
        2. 颜色为一个包含三个或四个 RGB 颜色字符串的元组，共两种形式:
             * 不使用禁用功能时: `(正常颜色, 触碰颜色, 交互颜色)`
             * 需使用禁用功能时: `(正常颜色, 触碰颜色, 交互颜色, 禁用颜色)`
             * 特别地，进度条控件的参数 `color_bar` 为: `(底色, 进度条颜色)`
        """
        self.master = canvas
        self.value = text
        self.justify = justify
        self.font = font
        self.photoimage = image
        self.tooltip = tooltip
        self.color_text = list(color_text)
        self.color_fill = list(color_fill)
        self.color_outline = list(color_outline)

        x *= canvas.rx
        y *= canvas.ry
        width *= canvas.rx
        height *= canvas.ry

        self.x1, self.y1 = x, y  # 控件左上角坐标
        self.x2, self.y2 = x + width, y + height  # 控件左下角坐标
        self.width, self.height = width, height  # 控件的宽高值
        self.radius = radius  # 边角圆弧半径
        self.live = True  # 控件活跃标志
        self._state = "normal"  # 控件的状态
        self.pre_state = None  # 记录之前的状态

        self.command_ex = {
            "normal": None, "touch": None,
            "click": None, "disabled": None
        }  # type: dict[str, typing.Callable | None]

        canvas._widget.append(self)  # 将实例添加到父画布控件

        if radius:
            if 2*radius > width:
                radius = width // 2
                self.radius = radius
            if 2*radius > height:
                radius = height // 2
                self.radius = radius

            d = 2*radius  # 圆角直径
            _x, _y = x + radius*canvas.rx, y + radius*canvas.ry
            _w, _h = width - d*canvas.rx, height - d*canvas.ry

            kw = {"outline": "", "fill": color_fill[0]}
            self.inside = [  # 虚拟控件内部填充颜色
                canvas.create_rectangle(
                    x, _y, x + width, y + height - radius * canvas.ry, **kw),
                canvas.create_rectangle(
                    _x, y, x + width - radius * canvas.rx, y + height, **kw),
                canvas.create_arc(x, y, x + d * canvas.rx,
                                  y + d * canvas.ry, start=90, **kw),
                canvas.create_arc(x + _w, y, x + width, y + \
                                  d * canvas.ry, start=0, **kw),
                canvas.create_arc(x, y + _h, x + d * canvas.rx,
                                  y + height, start=180, **kw),
                canvas.create_arc(x + _w, y + _h, x + width, y + height, start=270, **kw)]

            kw = {"extent": 100, "style": tkinter.ARC,
                  "outline": color_outline[0]}
            self.outside = [  # 虚拟控件外框
                canvas.create_line(_x, y, x + width - radius * canvas.rx,
                                   y, fill=color_outline[0], width=borderwidth),
                canvas.create_line(_x, y + height, x + width - radius * canvas.rx,
                                   y + height, fill=color_outline[0], width=borderwidth),
                canvas.create_line(x, _y, x, y + height - radius * \
                                   canvas.ry, fill=color_outline[0], width=borderwidth),
                canvas.create_line(x + width, _y, x + width, y + height - \
                                   radius * canvas.ry, fill=color_outline[0], width=borderwidth),
                canvas.create_arc(x, y, x + d * canvas.rx, y + \
                                  d * canvas.ry, start=90, width=borderwidth, **kw),
                canvas.create_arc(x + _w, y, x + width, y + d * \
                                  canvas.ry, start=0, width=borderwidth, **kw),
                canvas.create_arc(x, y + _h, x + d * canvas.rx,
                                  y + height, start=180, width=borderwidth, **kw),
                canvas.create_arc(x + _w, y + _h, x + width, y + height, start=270, width=borderwidth, **kw)]
        else:
            self.rect = canvas.create_rectangle(
                # 虚拟控件的外框
                x, y, x+width, y+height, width=borderwidth, outline=color_outline[0], fill=color_fill[0])

        self.image = canvas.create_image(
            x+width/2, y+height/2, image=image)  # 背景图片

        self.text = canvas.create_text(  # 虚拟控件显示的文字
            x + (radius+2 if justify == "left" else
                 width-radius-3 if justify == "right" else width/2),
            y+height/2,
            text=text,
            font=font,
            justify=justify,
            anchor="w" if justify == "left" else "e" if justify == "right" else "center",
            fill=color_text[0])

        if type(font) != str:
            font = list(font)
            font[1] = int(font[1] * math.sqrt(canvas.rx * canvas.ry))
            canvas._font[self.text][1] = font[1]
            canvas.itemconfigure(self.text, font=font)

    @typing.overload
    def state(self, mode):
        # type: (typing.Literal["normal", "touch", "click", "disabled"]) -> None
        ...

    @typing.overload
    def state(self):  # type: () -> None
        ...

    def state(self, mode=None):
        # type: (typing.Literal["normal", "touch", "click", "disabled"] | None) -> str | None
        """设置或查询控件的状态，参数 `mode` 为 `None` 或者无参数时仅更新控件，否则改变虚拟控件的外观 

        * `mode`: 可以为下列值之一 `normal`（正常状态）、`touch`（鼠标触碰时的状态）、`click`（鼠标按下时的状态）、`disabled`（禁用状态） 和 `None`（查询控件状态）
        """
        if mode:
            self._state, self.pre_state = mode, self._state
            if self._state == self.pre_state:  # 保持状态时直接跳过
                return

        if self._state == "normal":
            mode = 0
        elif self._state == "touch":
            mode = 1
        elif self._state == "click":
            mode = 2
        elif self._state == "disabled":
            mode = 3
        else:
            raise WidgetStateModeError(self._state)

        if self.tooltip is not None:
            if self._state == "normal":
                self.tooltip._cancel(self.master)
                self.tooltip._destroy()
            if self._state == "touch":
                self.tooltip._countdown(self.master)

        self.master.itemconfigure(self.text, fill=self.color_text[mode])
        if isinstance(self, (Text, CheckButton)):
            self.master.itemconfigure(self._text, fill=self.color_text[mode])

        if self.radius:
            for item in self.inside:  # 修改色块
                self.master.itemconfigure(item, fill=self.color_fill[mode])

            # 修改线条
            for item in self.outside[:4]:
                self.master.itemconfigure(item, fill=self.color_outline[mode])
            for item in self.outside[4:]:
                self.master.itemconfigure(
                    item, outline=self.color_outline[mode])
        else:
            self.master.itemconfigure(
                self.rect, outline=self.color_outline[mode])
            if isinstance(self, ProgressBar):
                self.master.itemconfigure(self.bottom, fill=self.color_fill[0])
                self.master.itemconfigure(self.bar, fill=self.color_fill[1])
            else:
                self.master.itemconfigure(
                    self.rect, fill=self.color_fill[mode])

        if self.command_ex[self._state]:
            self.command_ex[self._state]()

    def move(self, dx, dy):  # type: (float, float) -> None
        """移动控件的位置

        * `dx`: 横向移动长度
        * `dy`: 纵向移动长度
        """
        self.x1 += dx
        self.x2 += dx
        self.y1 += dy
        self.y2 += dy

        if self.radius:
            for item in self.inside + self.outside:
                self.master.move(item, dx, dy)
        else:
            self.master.move(self.rect, dx, dy)

        self.master.move(self.image, dx, dy)
        self.master.move(self.text, dx, dy)

        if isinstance(self, TextWidget):
            self.master.move(self._cursor, dx, dy)
        if isinstance(self, (Text, CheckButton)):
            self.master.move(self._text, dx, dy)
        if isinstance(self, ProgressBar):
            self.master.move(self.bar, dx, dy)

    def moveto(self, x, y):  # type: (float, float) -> None
        """改变控件的位置（以控件左上角为基准）

        * `x`: 改变到的横坐标
        * `y`: 改变到的纵坐标
        """
        self.move(x-self.x1, y-self.y1)

    @typing.overload
    def configure(self, **kw):  # type: (...) -> None
        ...

    @typing.overload
    def configure(self, *args):  # type: (...) -> str | tuple
        ...

    def configure(self, *args, **kw):  # type: (...) -> str | tuple | None
        """修改或查询参数的值

        可供修改或查询的参数有: 
        1. 所有控件: `color_text`、`color_fill`、`color_outline`
        2. 非文本控件: `text`

        注意：颜色修改不会立即生效，可通过鼠标经过生效，或者调用 `state` 方法立即刷新状态！
        """
        if args:
            if args[0] == "text":
                if isinstance(self, CheckButton):
                    return self.master.itemcget(self._text, "text")
                return self.value
            else:
                return getattr(self, args[0])

        value = kw.get("text", None)
        text = kw.get("color_text", None)
        fill = kw.get("color_fill", None)
        outline = kw.get("color_outline", None)

        if value is not None:
            if isinstance(self, CheckButton):
                self.master.itemconfigure(self._text, text=value)
            else:
                self.value = value
        if text:
            self.color_text = list(text)
        if fill:
            self.color_fill = list(fill)
        if outline:
            self.color_outline = list(outline)

        if isinstance(self, (Label, Button, ProgressBar)) and value is not None and not isinstance(self, CheckButton):
            self.master.itemconfigure(self.text, text=value)

    def destroy(self):  # type: () -> None
        """摧毁控件释放内存"""
        self.live = False
        self.master._widget.remove(self)

        if self.radius:
            for item in self.inside + self.outside:
                self.master.delete(item)
        else:
            self.master.delete(self.rect)

        if isinstance(self, TextWidget):
            self.master.delete(self._cursor)
        if isinstance(self, (Text, CheckButton)):
            self.master.delete(self._text)
        if isinstance(self, ProgressBar):
            self.master.delete(self.bar)

        self.master.delete(self.image)
        self.master.delete(self.text)

    @typing.overload
    def set_live(self, value):  # type: (bool) -> None
        ...

    @typing.overload
    def set_live(self):  # type: () -> bool
        ...

    def set_live(self, value=None):  # type: (bool | None) -> bool | None
        """设置或查询控件的活跃状态

        * `value`: 可以为 `bool` 类型（设置当前值）或者 `None`（返回当前值）
        """
        if value is None:
            return self.live
        else:
            self.live = value
            if value:
                self.state("normal")
            else:
                self.state("disabled")


class TextWidget(BaseWidget):
    """虚拟文本类控件基类 """

    def __init__(
        self,
        canvas,  # type: Canvas
        x,  # type: int
        y,  # type: int
        width,  # type: int
        height,  # type: int
        radius,  # type: float
        text,  # type: tuple[str] | str
        limit,  # type: int
        justify,  # type: str
        icursor,  # type: str
        borderwidth,  # type: int
        font,  # type: tuple[str, int, str]
        image,  # type: PhotoImage | None
        tooltip,  # type: ToolTip | None
        color_text,  # type: tuple[str, str, str]
        color_fill,  # type: tuple[str, str, str]
        color_outline  # type: tuple[str, str, str]
    ):  # type: (...) -> None

        self.canvas = canvas
        self.limit = limit
        self.icursor = icursor

        self.interval = 300  # 光标闪烁间
        self.flag = False  # 光标闪烁标志
        self._value = ["", text, ""] if type(text) == str else [
            "", *text]  # 隐式值

        BaseWidget.__init__(
            self, canvas, x, y, width, height, radius, "", justify, borderwidth,
            font, image, tooltip, color_text, color_fill, color_outline)

        # NOTE: 提示光标代码的位置顺序不可乱动，font 不可乱改
        self._cursor = canvas.create_text(0, 0, fill=color_text[2], font=font)
        canvas._font[self._cursor][1] = canvas._font[self.text][1]
        font = canvas.itemcget(self.text, "font")
        canvas.itemconfigure(self._cursor, font=font)

    def _touch_on(self):  # type: () -> None
        """鼠标悬停状态"""
        if self._state != "click":
            self.state("touch")

            if self.master.itemcget(self.text, "text") == self._value[1]:
                self.master.itemconfigure(self.text, text=self._value[2])

    def _touch_off(self):  # type: () -> None
        """鼠标离开状态"""
        if self._state != "click":
            self.state("normal")

            if self.master.itemcget(self.text, "text") == self._value[2]:
                self.master.itemconfigure(self.text, text=self._value[1])

    def _click(self, event):  # type: (Entry | Text, tkinter.Event) -> bool
        """交互状态检测"""
        if self.x1 <= event.x <= self.x2 and self.y1 <= event.y <= self.y2 and self._state in ("touch", "click"):
            if self._state != "click":
                self._click_on()
                return True
        else:
            self._click_off()
        return False

    def _touch(self, event):  # type: (Entry | Text, tkinter.Event) -> bool
        """触碰状态检测"""
        condition = self.x1 <= event.x <= self.x2 and self.y1 <= event.y <= self.y2
        self._touch_on() if condition else self._touch_off()
        return condition

    def _cursor_flash(self):  # type: () -> None
        """鼠标光标闪烁"""
        if self.interval >= 300:
            self.interval, self.flag = 0, not self.flag
            if self.flag:
                self.master.itemconfigure(self._cursor, text=self.icursor)
            else:
                self.master.itemconfigure(self._cursor, text="")

        if self._state == "click":
            self.interval += 10
            self.master.after(10, self._cursor_flash)
        else:
            self.interval, self.flag = 300, False  # 恢复默认值
            self.master.itemconfigure(self._cursor, text="")

    def _cursor_update(self, text=" "):  # type: (str) -> None
        """鼠标光标更新"""
        self.interval, self.flag = 300, False  # 恢复默认值
        if isinstance(self, Entry):
            self.master.coords(self._cursor, self.master.bbox(self.text)[2],
                               self.y1+self.height*self.master.ry/2)  # BUG: 缩放后光标位置会略微显示错误
        elif isinstance(self, Text):
            _pos = self.master.bbox(self._text)
            self.master.coords(self._cursor, _pos[2], _pos[1])
        self.master.itemconfigure(
            self._cursor, text="" if not text else self.icursor)

    def _paste(self):  # type: () -> bool
        """快捷键粘贴"""
        condition = self._state == "click" and not getattr(self, "show", None)
        if condition:
            self.append(self.master.clipboard_get())
        return condition

    def clear(self):  # type: () -> None
        """清空文本类控件的内容"""
        if isinstance(self, Text):
            event = tkinter.Event()
            event.keysym = "BackSpace"
            self._click_on()
            for _ in range(len(self.value)):
                self._input(event, True)
            self._click_off()
        else:
            self.value = self._value[0] = ""
            self.master.itemconfigure(self.text, text="")

    def get(self):  # type: () -> str
        """获取输入框的值"""
        return self.value

    def set(self, value):  # type: (str) -> None
        """设置输入框的值"""
        self.value = self._value[0] = value
        self.master.itemconfigure(self.text, text=self._value[0])

    def append(self, value):  # type: (Entry | Text, str) -> None
        """添加输入框的值"""
        event = tkinter.Event()
        event.keysym = None
        self._click_on()
        for s in value:
            event.char = s
            self._input(event, True)
        self._click_off()


class Label(BaseWidget):
    """标签控件"""

    def __init__(
        self,
        canvas,  # type: Canvas
        x,  # type: int
        y,  # type: int
        width,  # type: int
        height,  # type: int
        *,
        radius=RADIUS,  # type: float
        text="",  # type: str
        borderwidth=BORDERWIDTH,  # type: int
        justify="center",  # type: typing.Literal["left", "center", "right"]
        font=(FONT, SIZE),  # type: tuple[str, int, str]
        image=None,  # type: PhotoImage | None
        tooltip=None,  # type: ToolTip | None
        color_text=COLOR_TEXT,  # type: tuple[str, str, str]
        color_fill=COLOR_FILL_LABEL,  # type: tuple[str, str, str]
        color_outline=COLOR_OUTLINE_LABEL  # type: tuple[str, str, str]
    ):  # type: (...) -> None
        BaseWidget.__init__(
            self, canvas, x, y, width, height, radius, text, justify, borderwidth,
            font, image, tooltip, color_text, color_fill, color_outline)

    def _touch(self, event):  # type: (tkinter.Event) -> bool
        """触碰状态检测"""
        condition = self.x1 <= event.x <= self.x2 and self.y1 <= event.y <= self.y2
        self.state("touch" if condition else "normal")
        return condition


class Button(BaseWidget):
    """按钮控件"""

    def __init__(
        self,
        canvas,  # type: Canvas
        x,  # type: int
        y,  # type: int
        width,  # type: int
        height,  # type: int
        *,
        radius=RADIUS,  # type: float
        text="",  # type: str
        borderwidth: int = BORDERWIDTH,  # type: int
        justify="center",  # type: typing.Literal["left", "center", "right"]
        font=(FONT, SIZE),  # type: tuple[str, int, str]
        command=None,  # type: typing.Callable | None
        image=None,  # type: PhotoImage | None
        tooltip=None,  # type: ToolTip | None
        color_text=COLOR_TEXT,  # type: tuple[str, str, str]
        color_fill=COLOR_FILL_BUTTON,  # type: tuple[str, str, str]
        color_outline=COLOR_OUTLINE_BUTTON,  # type: tuple[str, str, str]
    ):  # type: (...) -> None
        BaseWidget.__init__(
            self, canvas, x, y, width, height, radius, text, justify, borderwidth,
            font, image, tooltip, color_text, color_fill, color_outline)
        self.command = command

    def _execute(self, event):  # type: (tkinter.Event) -> None
        """执行关联函数"""
        condition = self.x1 <= event.x <= self.x2 and self.y1 <= event.y <= self.y2
        if condition and self.command:
            self.command()

    def _click(self, event):  # type: (tkinter.Event) -> bool
        """交互状态检测"""
        if self.x1 <= event.x <= self.x2 and self.y1 <= event.y <= self.y2 and self._state in ("touch", "click"):
            self.state("click")
            return True
        else:
            self.state("normal")
        return False

    def _touch(self, event):  # type: (tkinter.Event) -> bool
        """触碰状态检测"""
        condition = self.x1 <= event.x <= self.x2 and self.y1 <= event.y <= self.y2
        self.state("touch" if condition else "normal")
        return condition


class CheckButton(Button):
    """复选框控件"""

    def __init__(
        self,
        canvas,  # type: Canvas
        x,  # type: int
        y,  # type: int
        height,  # type: int
        *,
        radius=RADIUS,  # type: float
        text="",  # type: str
        value=False,  # type: bool
        tick=TICK,  # type: str
        borderwidth=BORDERWIDTH,  # type: int
        justify="right",  # type: typing.Literal["right", "left"]
        font=(FONT, SIZE),  # type: tuple[str, int, str]
        image=None,  # type: PhotoImage | None
        tooltip=None,  # type: ToolTip | None
        color_text=COLOR_TEXT,  # type: tuple[str, str, str]
        color_fill=COLOR_FILL_CHECKBUTTON,  # type: tuple[str, str, str]
        color_outline=COLOR_OUTLINE_CHECKBUTTON  # type: tuple[str, str, str]
    ):  # type: (...) -> None
        Button.__init__(
            self, canvas, x, y, height, height, radius=radius, borderwidth=borderwidth, image=image, font=font,
            tooltip=tooltip, color_text=color_text, color_fill=color_fill, color_outline=color_outline)
        self.tick = tick
        if justify == "right":
            self._text = canvas.create_text(
                x + 1.25*height, y + height/2, text=text, anchor="w", fill=color_text[0], font=font)
        else:
            self._text = canvas.create_text(
                x - 0.25*height, y + height/2, text=text, anchor="e", fill=color_text[0], font=font)
        self.command = lambda: self.set(not bool(self.value))
        if value:
            self.command()

    def get(self):  # type: () -> bool
        """获取复选框状态"""
        return bool(self.value)

    def set(self, value):  # type: (bool) -> None
        """设置复选框状态"""
        self.value = self.tick if value else ""
        self.master.itemconfigure(self.text, text=self.value)


class Entry(TextWidget):
    """输入框控件"""

    def __init__(
        self,
        canvas,  # type: Canvas
        x,  # type: int
        y,  # type: int
        width,  # type: int
        height,  # type: int
        *,
        radius=RADIUS,  # type: float
        text="",  # type: tuple[str, str] | str
        show=None,  # type: str | None
        limit=LIMIT,  # type: int
        cursor=CURSOR,  # type: str
        borderwidth=BORDERWIDTH,  # type: int
        justify="left",  # type: typing.Literal["left", "center", "right"]
        font=(FONT, SIZE),  # type: tuple[str, int, str]
        image=None,  # type: PhotoImage | None
        tooltip=None,  # type: ToolTip | None
        color_text=COLOR_TEXT,  # type: tuple[str, str, str]
        color_fill=COLOR_FILL_ENTRY,  # type: tuple[str, str, str]
        color_outline=COLOR_OUTLINE_ENTRY  # type: tuple[str, str, str]
    ):  # type: (...) -> None
        TextWidget.__init__(
            self, canvas, x, y, width, height, radius, text, limit, justify, cursor,
            borderwidth, font, image, tooltip, color_text, color_fill, color_outline)
        self.master.itemconfigure(self.text, text=self._value[1])
        self.show = show

    def _click_on(self):  # type: () -> None
        """控件获得焦点"""
        self.state("click")
        self.master.itemconfigure(self.text, text=self._value[0])
        self._cursor_update("")
        self._cursor_flash()

    def _click_off(self):  # type: () -> None
        """控件失去焦点"""
        self.state("normal")

        if self.value == "":
            self.master.itemconfigure(self.text, text=self._value[1])
        else:
            self.master.itemconfigure(self.text, text=self._value[0])

    def _input(self, event, flag=False):  # type: (tkinter.Event, bool) -> None
        """文本输入"""
        if self._state == "click" or flag:
            if event.keysym == "BackSpace":  # 按下退格键
                self.value = self.value[:-1]
            elif len(self.value) == self.limit:  # 达到字数限制
                return True
            elif len(event.char):
                if not event.char.isprintable() or (event.char == " "):
                    return True
                else:  # 按下普通按键
                    self.value += event.char
            else:
                return True

            # 更新显示
            self._update_text()
            self._cursor_update()
            return True

    def _update_text(self):  # type: () -> None
        """更新控件"""
        self._value[0] = len(self.value) * \
            self.show if self.show else self.value  # 更新表面显示值
        self.master.itemconfigure(self.text, text=self._value[0])
        while True:
            pos = self.master.bbox(self.text)
            if self.justify == "left" and pos[2] > self.x2-self.radius-2:
                self._value[0] = self._value[0][1:]
                self.master.itemconfigure(self.text, text=self._value[0])
            elif self.justify == "right" and pos[0] < self.x1+self.radius+1:
                self._value[0] = self._value[0][:-1]
                self.master.itemconfigure(self.text, text=self._value[0])
            else:
                break

    def set(self, value):  # type: (str) ->None
        # overload: 防止 show 参数失效
        TextWidget.set(self, value)
        self._update_text()


class Text(TextWidget):
    """文本框控件"""

    def __init__(
        self,
        canvas,  # type: Canvas
        x,  # type: int
        y,  # type: int
        width,  # type: int
        height,  # type: int
        *,
        radius=RADIUS,  # type: float
        text="",  # type: tuple[str, str] | str
        limit=LIMIT,  # type: int
        read=False,  # type: bool
        cursor=CURSOR,  # type: str
        borderwidth=BORDERWIDTH,  # type: int
        justify="left",  # type: typing.Literal["left", "center", "right"]
        font=(FONT, SIZE),  # type: tuple[str, int, str]
        image=None,  # type: PhotoImage | None
        tooltip=None,  # type: ToolTip | None
        color_text=COLOR_TEXT,  # type: tuple[str, str, str]
        color_fill=COLOR_FILL_TEXT,  # type: tuple[str, str, str]
        color_outline=COLOR_OUTLINE_TEXT  # type: tuple[str, str, str]
    ):  # type: (...) -> None
        TextWidget.__init__(
            self, canvas, x, y, width, height, radius, text, limit, justify, cursor,
            borderwidth, font, image, tooltip, color_text, color_fill, color_outline)

        _x = x + (width-radius-3 if justify == "right" else width /
                  2 if justify == "center" else radius+2)
        _anchor = "n" if justify == "center" else "ne" if justify == "right" else "nw"

        self._text = canvas.create_text(  # NOTE: 位置确定文本，位置不要乱动
            _x, y+radius+2,
            justify=justify,
            anchor=_anchor,
            font=font,
            fill=color_text[0])

        self.read = read  # 只读模式

        # 修改多行文本靠左显示
        self.master.coords(self.text, _x, y + radius + 2)
        self.master.itemconfigure(
            self.text, text=self._value[1], anchor=_anchor)
        self.master.itemconfigure(self._cursor, anchor="n")

    def _click_on(self):  # type: () -> None
        """控件获得焦点"""
        if not self.read:
            self.state("click")
            *__, _ = [""] + self._value[0].rsplit("\n", 1)
            self.master.itemconfigure(self.text, text="".join(__))
            self.master.itemconfigure(self._text, text=_)
            self._cursor_update("")
            self._cursor_flash()

    def _click_off(self):  # type: () -> None
        """控件失去焦点"""
        self.state("normal")

        if self.value == "":
            self.master.itemconfigure(self.text, text=self._value[1])
        else:
            *__, _ = [""] + self._value[0].rsplit("\n", 1)
            self.master.itemconfigure(self.text, text="".join(__))
            self.master.itemconfigure(self._text, text=_)

    def _input(self, event, flag=False):  # type: (tkinter.Event, bool) -> bool
        """文本输入"""
        if self._state == "click" or flag:
            if event.keysym == "BackSpace":  # 按下退格键
                self._input_backspace()
            elif len(self.value) == self.limit:  # 达到字数限制
                return True
            elif event.keysym == "Tab":  # 按下Tab键
                self.append(" "*4)
            elif event.keysym == "Return" or event.char == "\n":  # 按下回车键
                self._input_return()
            elif event.char.isprintable() and event.char:  # 按下其他普通的键
                _text = self.master.itemcget(self._text, "text")
                self.master.itemconfigure(self._text, text=_text + event.char)
                _pos = self.master.bbox(self._text)

                if _pos[2] > self.x2-self.radius-2 or _pos[0] < self.x1+self.radius+1:  # 文本溢出啦
                    self.master.itemconfigure(self._text, text=_text)
                    self._input_return()
                    self.master.itemconfigure(self._text, text=event.char)

                self.value += event.char
            else:
                return True

            self._cursor_update()

            # 更新表面显示值
            text = self.master.itemcget(self.text, "text")
            _text = self.master.itemcget(self._text, "text")
            self._value[0] = text + "\n" + _text

            return True

    def _input_return(self):  # type: () -> None
        """回车键功能"""
        self.value += "\n"

        # 相关数据获取
        text = self.master.itemcget(self.text, "text")
        _text = self.master.itemcget(self._text, "text")
        _pos = self.master.bbox(self._text)

        self.master.itemconfigure(self._text, text="")

        if _pos[3]+_pos[3]-_pos[1] < self.y2-self.radius-2:  # 还没填满文本框
            self.master.move(self._text, 0, _pos[3] - _pos[1])
            self.master.itemconfigure(
                self.text, text=text + bool(text) * "\n" + _text)
        else:  # 文本框已经被填满了
            text = text.split("\n", 1)[-1]
            self.master.itemconfigure(self.text, text=text + "\n" + _text)

    def _input_backspace(self):  # type: () -> None
        """退格键功能"""
        if not self.value:  # 没有内容，删个毛啊
            return

        _text = self.master.itemcget(self._text, "text")
        self.value = self.value[:-1]

        if _text:  # 正常地删除字符
            self.master.itemconfigure(self._text, text=_text[:-1])
        else:  # 遇到换行符
            _ = self.value.rsplit("\n", 1)[-1]
            self.master.itemconfigure(self._text, text=_)

            # 内容未超出框的大小
            if self.value == self.master.itemcget(self.text, "text"):
                _pos = self.master.bbox(self._text)
                self.master.move(self._text, 0, _pos[1] - _pos[3])
                # NOTE: 为了兼容 Python3.8，放弃使用 str.removesuffix 方法，以 temp 取而代之
                temp = self.value[:-
                                  len(_)] if self.value.endswith(_) else self.value
                __ = temp[:-("\n" in self.value)]
            else:  # 内容已经超出框框的大小啦
                text = self.master.itemcget(self.text, "text")
                temp = self.value[:-len(text)
                                  ] if self.value.endswith(text) else self.value
                temp2 = text[:len(_)] if text.endswith(_) else text
                __ = temp[:-1].rsplit("\n", 1)[-1] + "\n" + temp2[:-1]

            self.master.itemconfigure(self.text, text=__)


class ProgressBar(BaseWidget):
    """进度条控件"""

    def __init__(
        self,
        canvas,  # type: Canvas
        x,  # type: int
        y,  # type: int
        width,  # type: int
        height,  # type: int
        *,
        borderwidth=BORDERWIDTH,  # type: int
        justify="center",  # type: typing.Literal["left", "center", "right"]
        font=(FONT, SIZE),  # type: tuple[str, int, str]
        image=None,  # type: PhotoImage | None
        tooltip=None,  # type: ToolTip | None
        color_text=COLOR_TEXT,  # type: tuple[str, str, str]
        color_outline=COLOR_OUTLINE_PROGRESSBAR,  # type: tuple[str, str, str]
        color_fill=COLOR_FILL_PROGRESSBAR,  # type: tuple[str, str]
        # type: typing.Literal["determinate", "indeterminate"]
        mode="determinate",
    ):  # type: (...) -> None
        self.bottom = canvas.create_rectangle(
            x, y, x + width, y + height, width=borderwidth, fill=color_fill[0])
        self.bar = canvas.create_rectangle(
            x, y, x, y + height, width=borderwidth, outline="", fill=color_fill[1])
        # XXX: 圆角功能的添加，建议重构 BaseWidget 来解决
        self.mode = mode
        if mode == "indeterminate":
            color_text = COLOR_NONE
        BaseWidget.__init__(
            self, canvas, x, y, width, height, 0, "0.00%", justify, borderwidth,
            font, image, tooltip, color_text, COLOR_NONE, color_outline)

        self.color_fill = list(color_fill)

    def _touch(self, event):  # type: (tkinter.Event) -> bool
        """触碰状态检测"""
        condition = self.x1 <= event.x <= self.x2 and self.y1 <= event.y <= self.y2
        self.state("touch" if condition else "normal")
        return condition

    def load(self, percentage):  # type: (float) -> None
        """加载进度条的值（调整值）

        * `percentage`: 进度条的值，范围 0~1，大于 1 的值将被视为 1
        """
        percentage = 0 if percentage < 0 else 1 if percentage > 1 else percentage
        if self.mode == "determinate":
            self.configure(text=f"{percentage*100:.2f}%")
            x1, x2 = 0, self.width*percentage
        elif self.mode == "indeterminate":
            length = percentage*self.width*4/3
            x1 = length - self.width/3 if length > self.width/3 else 0
            x2 = length if length < self.width else self.width
        self.master.coords(self.bar, self.x1 + x1*self.master.rx,
                           self.y1, self.x1 + x2*self.master.rx, self.y2)


class Switch(Button):
    """开关控件"""

    def __init__(
        self,
        canvas,  # type: Canvas
        x,  # type: int
        y,  # type: int
        height=SWITCH_HEIGHT,  # type: int
        *,
        width=SWITCH_WIDTH,  # type: int
        radius=SWITCH_RADIUS,  # type: float
        borderwidth=BORDERWIDTH,  # type: int
        tooltip=None,  # type: ToolTip | None
        color_fill_on=COLOR_FILL_ON,  # type: tuple[str, str, str]
        color_fill_off=COLOR_FILL_OFF,  # type: tuple[str, str, str]
        color_outline_on=COLOR_OUTLINE_ON,  # type: tuple[str, str, str]
        color_outline_off=COLOR_OUTLINE_OFF,  # type: tuple[str, str, str]
        color_fill_slider=COLOR_FILL_SLIDER,  # type: tuple[str, str, str]
        # type: tuple[str, str, str]
        color_outline_slider=COLOR_OUTLINE_SLIDER,
        default=False,  # type: bool
        on=None,  # type: typing.Callable | None
        off=None,  # type: typing.Callable | None
    ):  # type: (...) -> None
        """
        * `canvas`: 父画布控件
        * `x`: 横坐标
        * `y`: 纵坐标
        * `height`: 高度，默认为 30 像素
        * `width`: 宽度，默认为高度的两倍
        * `radius`: 圆角半径，默认为完全圆弧
        * `borderwidth`: 边框宽度
        * `tooltip`: 提示框
        * `color_fill_on`: 内部颜色（状态：开）
        * `color_fill_off`: 内部颜色（状态：关）
        * `color_outline_on`: 边框颜色（状态：开）
        * `color_outline_off`: 边框颜色（状态：关）
        * `color_fill_slider`: 滑块内部颜色
        * `color_outline_slider`: 滑块边框颜色
        * `default`: 默认值，默认为 `False`
        * `on`: 转换到开时触发的回调函数
        * `off`: 转换到关时触发的回调函数
        """
        self.on = on
        self.off = off
        self.color_fill_on = color_fill_on
        self.color_fill_off = color_fill_off
        self.color_outline_on = color_outline_on
        self.color_outline_off = color_outline_off
        Button.__init__(
            self, canvas, x, y, height*2 if width < height*2 else width, height, radius=radius,
            borderwidth=borderwidth, tooltip=tooltip, color_fill=color_fill_off, color_outline=color_outline_off,
            command=lambda: self.set(not self.value))
        self.value = default  # NOTE: 位置不可乱动
        spcaing = height / 7
        self._slider = Button(  # XXX: 滑块状态无法保证和本体同步，建议重构 BaseWidget 解决问题
            canvas, x+spcaing, y+spcaing, height - spcaing*2, height - spcaing*2, radius=radius,
            borderwidth=borderwidth, color_outline=color_outline_slider, color_fill=color_fill_slider,
            command=lambda: self.set(not self.value))
        if self.value:
            self._animate(0)

    def _animate(self, ms=SWITCH_ANIMATION_MS):  # type: (int) -> None
        """移动动画"""
        if self.value:
            key = 1
            self.configure(color_fill=self.color_fill_on,
                           color_outline=self.color_outline_on)
        else:
            key = -1
            self.configure(color_fill=self.color_fill_off,
                           color_outline=self.color_outline_off)
        self.state()
        Animation(self._slider, ms, fps=90, control=(math.sin, 0, math.pi), translation=(
            key * (self.width-self.height) * self._slider.master.rx, 0)).run()

    def get(self):  # type: () -> bool
        """返回状态"""
        return self.value

    def set(self, value):  # type: (bool) -> None
        """设定状态"""
        self.value = value
        if self.value and self.on is not None:
            self.on()
        if not self.value and self.off is not None:
            self.off()
        self._animate()

    def state(self, mode=None):
        # type: (typing.Literal["normal", "touch", "click", "disabled"] | None) -> str | None
        # overload: 重载以兼容
        if mode is None:
            return Button.state(self)
        self._slider.state(mode)
        Button.state(self, mode)

    def move(self, dx, dy):  # type: (float, float) -> None
        # overload: 重载以兼容
        self._slider.move(dx, dy)
        Button.move(self, dx, dy)

    def set_live(self, value=None):  # type: (bool | None) -> bool | None
        # overload: 重载以兼容
        if value is None:
            return Button.set_live(self)
        self._slider.set_live(value)
        Button.set_live(self, value)

    def configure(self, *args, **kw):  # type: (...) -> str | tuple | None
        """修改或查询参数的值

        可供修改或查询的参数有: `color_fill`、`color_outline`、`color_fill_slider` 和 `color_outline_slider`

        注意：颜色修改不会立即生效，可通过鼠标经过生效，或者调用 `state` 方法立即刷新状态！
        """
        if args:
            res = getattr(self, args[0], None)
            if res is None:
                return getattr(self._slider, args[0][:-7])
            return res
        fill = kw.get("color_fill", None)
        outline = kw.get("color_outline", None)
        fill_slider = kw.get("color_fill_slider", None)
        outline_slider = kw.get("color_outline_slider", None)
        self._slider.configure(color_fill=fill_slider,
                               color_outline=outline_slider)
        Button.configure(self, color_fill=fill, color_outline=outline)

    # NOTE: destory 无需重载，因为 self.slider 实际是独立的控件


class ToolTip:
    """提示框容器控件"""

    def __init__(
        self,
        text,  # type: str
        *,
        font=(FONT,),
        # type: tuple[str, int, str] | tuple[str, int] | str
        fg=TOOLTIP_FG,  # type: str
        bg=TOOLTIP_BG,  # type: str
        justify="left",  # type: typing.Literal["left", "center", "right"]
        highlightthickness=TOOLTIP_HIGHLIGHT_THICKNESS,  # type: int
        highlightbackground=TOOLTIP_HIGHLIGHT_BACKGROUND,  # type: str
        delay=DELAY,  # type: int
        duration=DURATION,  # type: int | None
    ):  # type: (...) -> None
        """
        * `text`: 要显示的文本
        * `font`: 文本字体
        * `fg`: 前景色，默认为黑色
        * `bg`: 背景色，默认为淡黄色
        * `justify`: 文本对齐方式
        * `highlightthickness`: 边框厚度，默认为 1 像素
        * `highlightbackground`: 边框颜色，默认为黑色
        * `delay`: 延迟时间，超过这个时间后，提示框才会出现，默认为 500 毫秒（必须大于等于零）
        * `duration`: 持续时间，达到这个值后，提示框会消失，默认为 5000 毫秒（值为 `None` 表示不会自己消失，需要触发才会消失，但有时候会触发失败……）
        """
        self.text = text
        self.font = font
        self.fg = fg
        self.bg = bg
        self.justify = justify
        self.highlightthickness = highlightthickness
        self.highlightbackground = highlightbackground
        self.delay = delay
        self.duration = duration

        self.toplevel = None  # type: Toplevel | None
        self.cd = None  # type: str | None

    def _countdown(self, master):  # type: (tkinter.Widget) -> None
        """倒计时"""
        if self.cd is None:
            self.cd = master.after(self.delay, self._place)

    def _cancel(self, master):  # type: (tkinter.Widget) -> None
        """取消倒计时"""
        if self.cd is not None:
            master.after_cancel(self.cd)
            self.cd = None

    def _place(self):  # type: () -> None
        """显示"""
        self.toplevel = tkinter.Toplevel(
            highlightthickness=self.highlightthickness, highlightbackground=self.highlightbackground)
        px, py = self.toplevel.winfo_pointerxy()
        x = self.toplevel.master.winfo_x()
        y = self.toplevel.master.winfo_y()
        width = self.toplevel.master.winfo_width()
        height = self.toplevel.master.winfo_height()
        if not x <= px <= x + width or not y <= py <= y + height:
            return self._destroy()
        self.toplevel.overrideredirect(True)
        self.toplevel.geometry(f"+{px+1}+{py+1}")
        tkinter.Label(self.toplevel, text=self.text, font=self.font,
                      fg=self.fg, bg=self.bg, justify=self.justify).pack()
        if self.duration is not None:
            self.toplevel.after(self.duration, self._destroy)

    def _destroy(self):
        """消失"""
        if self.toplevel is not None:
            self.toplevel.destroy()
            self.toplevel = None


class PhotoImage(tkinter.PhotoImage):
    """图片类"""

    def __init__(
        self,
        file,  # type: str | bytes
        **kw
    ):  # type: (...) -> None
        """
        * `file`: 图片文件的路径
        * `**kw`: 与 `tkinter.PhotoImage` 的参数相同
        """
        self.file = file  # 图片文件的路径
        self.extension = file.rsplit(".", 1)[-1]  # 文件扩展名
        self._item = {}  # type: dict[int, Canvas | None]

        if self.extension == "gif":  # 动态图片
            self.image = []  # type: list[tkinter.PhotoImage]
            self.parse_done = False
        else:  # 静态图片
            self.image = tkinter.PhotoImage.__init__(self, file=file, **kw)

    def parse(self, start=0):
        # type: (int) -> typing.Generator[int, None, None] | None
        """解析动图，并得到动图的每一帧动画，该方法返回一个生成器 

        * `start`: 动图解析的起始索引（帧数-1）
        """
        try:
            if self.parse_done:
                return
            while True:
                self.image.append(tkinter.PhotoImage(
                    file=self.file, format=f"gif -index {start}"))
                value = yield start  # 抛出索引
                start += value if value else 1
        except:
            self.parse_done = True
            return

    def play(self, canvas, item, interval, **kw):  # type: (Canvas, int, int, ...) -> None
        """播放动图，设置 `canvas.lock` 为 `False` 会暂停 

        * `canvas`: 播放动画的画布
        * `item`: 播放动画的 `_CanvasItemId`（`create_image` 方法的返回值）
        * `interval`: 每帧动画的间隔时间
        """
        if kw.get("_ind", None) is None:  # 初始化的判定
            self._item[item], kw["_ind"] = canvas, -1
        if not self._item[item]:  # 终止播放的判定
            return
        if canvas._lock:  # 暂停播放的判定
            if not self.parse_done:
                if getattr(self, 'parser', None) is None:
                    self.parser = self.parse()
                next(self.parser, None)
            canvas.itemconfigure(item, image=self.image[kw["_ind"]])
        _ind = kw["_ind"] + 1
        # 迭代执行函数
        canvas.after(interval if self.parse_done else 1, lambda: self.play(
            canvas, item, interval, _ind=0 if _ind == len(self.image) else _ind))

    def stop(self, item, clear=False):  # type: (int, bool) -> None
        """终止对应动图的播放，且无法重新播放 

        * `item`: 播放动画的 `_CanvasItemId`（`create_text` 方法的返回值）
        * `clear`: 清除图片的标识，为 `True` 就清除图片
        """
        self._item[item] = None
        if clear:  # 清除背景
            self._item[item].itemconfigure(item, image=None)

    def zoom(self, rate_x, rate_y, *, precision=None):
        # type: (float, float, ..., float | None) -> tkinter.PhotoImage
        """缩放图片，但不会缩放该图片对象本身，只是返回一个缩放后的图片对象 

        * `rate_x`: 横向缩放倍率
        * `rate_y`: 纵向缩放倍率
        * `precision`: 精度到小数点后的位数（推荐 1.2），越大运算就越慢（默认值代表绝对精确）

        注意：若有 PIL 包，请忽略参数 `precision`
        """
        if Image is not None:
            new_size = map(
                int, [self.width() * rate_x, self.height() * rate_y])
            image = Image.open(self.file).resize(new_size)
            return ImageTk.PhotoImage(image)
        if precision is not None:
            limit = round(10**precision)
            rate_x = fractions.Fraction(str(rate_x)).limit_denominator(
                limit)  # type: fractions.Fraction
            rate_y = fractions.Fraction(str(rate_y)).limit_denominator(
                limit)  # type: fractions.Fraction
            image = tkinter.PhotoImage.zoom(
                self, rate_x.numerator, rate_y.numerator)
            image = image.subsample(rate_x.denominator, rate_y.denominator)
        else:
            width, height = int(
                self.width() * rate_x), int(self.height() * rate_y)
            image = tkinter.PhotoImage(width=width, height=height)
            for x in range(width):
                for y in range(height):
                    r, g, b = self.get(int(x/rate_x), int(y/rate_y))
                    image.put(f"#{r:02X}{g:02X}{b:02X}", (x, y))

        return image


class Animation:
    """动画"""

    def __init__(
        self,
        widget,  # type: BaseWidget | tkinter.BaseWidget | int
        ms,  # type: int
        *,
        # type: tuple[typing.Callable[[float], float], float, float] | None
        control=CONTROL,
        translation=None,  # type: tuple[float, float] | None
        # type: tuple[typing.Callable[[str], None], str, str] | None
        color=None,
        fps=FPS,  # type: int
        start=None,  # type: typing.Callable | None
        step=None,  # type: typing.Callable | None
        stop=None,  # type: typing.Callable | None
        callback=None,  # type: typing.Callable[[float]] | None
        canvas=None,  # type: tkinter.Canvas | None
        loop=False,  # type: bool
    ):  # type: (...) -> None
        """
        * `widget`: 进行动画的控件
        * `ms`: 动画总时长（单位：毫秒）
        * `control`: 控制函数，为元组 (函数, 起始值, 终止值) 的形式
        * `translation`: 平移运动，x 方向位移，y 方向位移
        * `color`: 颜色变换
        * `fps`: 每秒帧数
        * `start`: 动画开始前执行的函数
        * `step`: 动画每一帧结束后执行的函数（包括开始和结束）
        * `stop`: 动画结束后执行的函数
        * `callback`: 回调函数，每一帧调用一次，传入参数为单帧占比
        * `canvas`: 当 `widget` 是画布中的绘制对象时，应指定 `canvas`
        * `loop`: 是否循环播放动画，默认不循环，循环时参数 `stop` 失效
        """
        self.widget = widget
        self.master = canvas if isinstance(widget, int) else widget if isinstance(
            widget, tkinter.Widget) else widget.master
        self.start = start
        self.step = step
        self.stop = stop
        self.loop = loop
        self.translation = translation
        self.color = color
        self.sec = 1000 // fps  # 单帧间隔时间
        self.count = ms * fps // 1000  # 总帧数
        if self.count == 0:
            self.count = 1  # 至少一帧
        self.callback = callback
        if control is None:
            control = (lambda _: 1), 0, 1
        self.parts = self._parts(*control)
        self.animation = ""  # 动画命令

    def _parts(self, control, up, down):
        # type: (typing.Callable[[float], float], float, float) -> list[float]
        """部分比率"""
        key = (down-up) / self.count
        parts = [control(key * value) for value in range(1, self.count+1)]
        total = sum(parts)
        return [elem/total for elem in parts]

    def _run(self, _ind=0):  # type: (int) -> None
        """执行动画"""
        if _ind == self.count:
            if self.loop:
                return self._run()  # 循环播放动画
            return None if self.stop is None else self.stop()
        self.animation = self.master.after(self.sec, self._run, _ind+1)

        if self.translation is not None:
            self._translate(*[value * self.parts[_ind]
                            for value in self.translation])
        if self.color is not None:
            self.color[0](color(self.color[1:], sum(self.parts[:_ind+1])))

        None if self.step is None else self.step()
        None if self.callback is None else self.callback(self.parts[_ind])

    def _translate(self, dx, dy):  # type: (int, int) -> None
        """平移"""
        if isinstance(self.widget, (tkinter.Tk, tkinter.Toplevel)):  # 窗口
            size, x, y = self.widget.geometry().split("+")
            self.widget.geometry(f"{size}+{int(x) + dx}+{int(y) + dy}")
        elif isinstance(self.widget, tkinter.Widget):  # tkinter 控件
            place_info = self.widget.place_info()
            origin_x, origin_y = float(place_info["x"]), float(place_info["y"])
            self.widget.place(x=origin_x + dx, y=origin_y + dy)
        elif isinstance(self.widget, BaseWidget):  # tkt 控件
            self.widget.move(dx, dy)
        elif isinstance(self.widget, int):  # int
            self.master.move(self.widget, dx, dy)

    def run(self):  # type: () -> None
        """运行动画"""
        None if self.start is None else self.start()
        self._run()

    def shutdown(self):  # type: () -> None
        """终止动画"""
        if self.animation != "":
            self.master.after_cancel(self.animation)


@typing.overload
def color(
    __color,  # type: typing.Iterable[str]
    /,
    proportion=PROPORTION,  # type: float
    *,
    seqlength=SEQLENGTH,  # type: int
    num=NUM,  # type: typing.Literal[1, 2, 3, 4]
):  # type: (...) -> str | list[str]
    ...


@typing.overload
def color(
    __color,  # type: str
    /,
    proportion=PROPORTION,  # type: float
    *,
    seqlength=SEQLENGTH,  # type: int
    num=NUM,  # type: typing.Literal[1, 2, 3, 4]
):  # type: (...) -> str | list[str]
    ...


def color(
    __color,  # type: typing.Iterable[str] | str
    /,
    proportion=PROPORTION,  # type: float
    *,
    seqlength=SEQLENGTH,  # type: int
    num=NUM,  # type: typing.Literal[1, 2, 3, 4]
):  # type: (...) -> str | list[str]
    """按一定比例给出已有 RGB 颜色字符串的渐变 RGB 颜色字符串，或者给出已有 RGB 颜色字符串的对比色

    * `color`: 颜色元组或列表 (初始颜色, 目标颜色)，或者一个颜色字符串（此时返回其对比色）
    * `proportion`: 改变比例（浮点数，范围为 0 ~ 1），默认值为 1
    * `seqlength`: 如果值为 1，则直接返回结果，其余情况返回长度为 `seqlength` 的渐变颜色列表，默认为 1
    * `num`: 每一通道的 16 进制位数，默认为 2 位，可选值为 1 ~ 4
    """
    if not 0 <= proportion <= 1:
        raise ColorArgsValueError(proportion)

    key = 16 - (num << 2)
    format_ = f"#%0{num}X%0{num}X%0{num}X"

    if tkinter._default_root is None:
        tkinter.Tk().withdraw()

    if isinstance(__color, str):  # 对比色的情况处理
        start = [c >> key for c in tkinter._default_root.winfo_rgb(__color)]
        end = [(1 << (num << 2)) - c - 1 for c in start]
    else:
        start = [c >> key for c in tkinter._default_root.winfo_rgb(__color[0])]
        end = [c >> key for c in tkinter._default_root.winfo_rgb(__color[1])]

    proportion_generator = (
        proportion*i/seqlength for i in range(1, seqlength+1))
    lst = [(format_ % tuple(c1 + round((c2-c1) * p)
            for c1, c2 in zip(start, end))) for p in proportion_generator]

    return lst[0] if seqlength == 1 else lst


def askfont(
    bind=None,  # type: typing.Callable[[str], typing.Any] | None
    initfont=""  # type: tuple[str, int, str] | tuple[str, int] | str
):  # type: (...) -> None
    """字体选择对话框，弹出选择字体的默认对话框窗口

    * `bind`: 关联的回调函数，有且仅有一个参数 `font`
    * `initfont`: 初始字体，格式为 `font` 参数默认格式

    注意: 由于 `tkinter` 模块无法直接打开该窗口，所以此处添加了这个函数
    """
    args = []

    if tkinter._default_root is None:
        tkinter.Tk().withdraw()

    if bind is not None:
        args += ["-command", tkinter._default_root.register(bind)]
    if initfont:
        if isinstance(initfont, tuple):
            initfont = " ".join(str(i) for i in initfont)
        args += ["-font", initfont]
    if args:
        tkinter._default_root.tk.call("tk", "fontchooser", "configure", *args)
    tkinter._default_root.tk.call("tk", "fontchooser", "show")


# __all__ = [
#     "Tk",
#     "Toplevel",
#     "Canvas",
#     "Label",
#     "Button",
#     "CheckButton",
#     "Entry",
#     "Text",
#     "ProgressBar",
#     "Switch",
#     "ToolTip",
#     "PhotoImage",
#     "Animation",
#     "color",
#     "askfont",
# ]
