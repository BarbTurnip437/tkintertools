Change Log/更新日志
==================

[2.5.4] - 2022-12-08
--------------------

### Features/新增

* A new widget has been added: progress bar(ProcessBar)  
增加了一个新的控件：进度条（ProcessBar）

### Fixed/修复

* Fixed the bug that the screen size would be abnormal when creating Canvas of different sizes  
修复了新建不同大小的 Canvas 时，画面大小会异常的 bug

* Solved the bug that there is no change when the font size is scaled under certain conditions  
解决了字体大小进行缩放时，在某种条件下缩小没有变化的 bug

* Solved the bug that function move_widget cannot move tkinter._CanvasItemId  
解决了函数 move_widget 无法移动 tkinter._CanvasItemId 的 bug

### Changed/变更

* The binding mechanism of associated events has been modified so that Canvas classes can be created at any time  
修改了关联事件的绑定机制，使得 Canvas 类可以被随时创建

### Refactored/优化

* Some colors are beautified  
美化了部分颜色

* Optimized some codes in function move_widget
优化了函数 move_widget 中的部分代码

[2.5.3] - 2022-11-27
--------------------

### Features/新增

* Added singleton pattern class for inheritance  
增加了单例模式类供继承

* Add some methods (attributes) of Tk, Toplevel and Canvas to access some attributes that should not be directly accessed  
增加 Tk、Toplevel、Canvas 的一些方法(属性)来访问一些不应该被直接访问的属性

### Fixed/修复

* Solved the bug that the destroy method of the control can only delete half of the controls when traversing  
解决了控件的 destroy 方法在遍历使用时只能删除一半控件的 bug

    > Thanks/特别感谢  
    Thanks [-ShuiGuang-](https://blog.csdn.net/atlantis618) for finding a bug (point 3)  
    感谢 [-ShuiGuang-](https://blog.csdn.net/atlantis618) 发现一个bug（第3点）

### Refactored/优化

* Canvas class overrides destroy method to be compatible with the original destroy method  
Canvas 类重写 destroy 方法以兼容原 destroy 方法

* Toplevel class overrides destroy method to be compatible with the original destroy method  
Toplevel 类重写 destroy 方法以兼容原 destroy 方法

* Some codes of Tk and Toplevel are optimized, and the code amount of Toplevel controls is greatly reduced  
优化了 Tk、Toplevel 的部分代码，Toplevel 控件的代码量大大缩减

### Removed/删除

* The proportion_lock parameter and its function of Tk and Toplevel are deleted  
删除了 Tk、Toplevel 的 proportion_lock 参数及其功能

[2.5.2] - 2022-11-25
--------------------

### Features/新增

* Added mouse style for text type virtual control  
添加了对文本类虚拟控件的鼠标样式

### Fixed/修复

* Solved the bug that the set and append methods of text virtual controls may fail in some cases  
解决了文本类虚拟控件 set、append 方法某些时候会失效的 bug

* Solved the bug that the mouse style flickers when the mouse cursor moves over the button  
解决了鼠标光标移动到按钮上时的鼠标样式会闪烁的 bug

* Fixed the bug that the read parameter of the text box control failed  
修复了文本框控件 read 参数失效的 bug

### Refactored/优化

* Change the mouse position detection order to further improve the running speed  
改变鼠标位置检测顺序，进一步提升运行速度

[2.5.1] - 2022-11-23
--------------------

### Features/新增

* Added mouse style for button virtual controls  
添加了对按钮虚拟控件的鼠标样式

### Fixed/修复

* Solved the bug that the input prompt position was not aligned after the input box was enlarged  
解决了输入框放大后输入提示符位置没对齐的 bug

* Solved the bug that text virtual controls will lose focus after being pasted once  
解决了文本类虚拟控件粘贴一次后会失去焦点的 bug

* Fix a few errors in the module documentation  
修复模块文档中的少许错误

### Changed/变更

* Modified the mouse position determination mechanism and improved the running speed  
修改了鼠标位置判定机制，同时提升运行速度

### Refactored/优化

* Some redundant codes are deleted to improve the overall running speed  
删除了部分冗余代码，提升总体运行速度

[2.5.0] - 2022-11-21
--------------------

No more logging