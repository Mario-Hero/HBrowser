# HBrowser

**HPicBrowser：**

支持文件夹穿透和随机播放的图片幻灯片播放Python脚本。

**HVidBrowser：**

支持文件夹穿透和随机播放的视频播放Python脚本，基于python-vlc.



两个脚本均为键盘控制。可以直接拖入文件夹到Python文件开始播放，也可以通过按下F1~F12和数字0~9来播放预先设置好的库，最多支持12*10=120个库。支持读取Windows下的快捷方式指向的文件夹、视频和图片。支持播放.url文件所指的网络图片和视频。支持以英文、拼音、拼音首字母搜索文件夹。



# 更新Log

2021.08.07：图片幻灯片播放器改成了新开一个线程载入图片。

2021.06.07：视频播放器在切换时不会卡死了。具体解决方法见文档最后《问题以及解决方法》。

2021.06.05：视频播放器新增手机模式，使触屏更方便操作：左侧按键切换视频，右侧按键快进30秒。【基本】修复了切换视频时会时常崩溃的bug，偶尔还是会崩。。



# 为什么做这个东西？

我的一位朋友存了很多套图片，分门别类地摆放整齐，分了好几级文件夹，还标注上了好看不好看。但是要看的时候就找不到合适的看图软件，因为大部分看图软件都只能在一个文件夹里随机播放幻灯片，其他的要么支持文件夹穿透但不能随机播放，要么能随机播放但只能穿透一层文件夹。实在是让人十分不快，所以他让我做一个专门随机看图的软件。

本来我想用Qt，但是没有那个必要。这个软件必须是能高度定制、随时调整的，用脚本应该更合适。

脚本写好了，他试用一段时间后，说非常满意。还问我能不能做个随机播放视频的软件。。。我就给他做了一个。



# 依赖

1. **Python 3**

2. **安装 pypiwin32 pillow pypinyin python-vlc** 

   可通过cmd中执行以下命令来安装：`pip install pypiwin32 pillow pypinyin python-vlc` 

3. **安装 VLC播放器** 

   可以到[官网](https://www.videolan.org/)下载安装。没有它就无法播放音乐和视频。



# **HPicBrowser**

## **用法**

直接把单个或多个文件夹拖入Python脚本上即可全屏播放幻灯片，如果直接打开该脚本，它就会打开默认库DEFAULT_LIB，你可以在打开脚本后按F1到F12和0到9选择MY_SELECT_LIB中的一个库进行播放，一个库可以是多个文件夹的集合。F1到F12为库的行数，1234567890为库的列数，按下F1到F12和0到9任意一个按键即可播放该库。



**左侧键盘操作**

本脚本为左侧键盘操作，如有需要可以在程序里自行修改键位。

按Esc退出。按S暂停或播放。

按左Shift增加幻灯片间隔时间，按左Ctrl减少。一次±0.5秒。

按F打开随机播放，或关闭随机播放进行顺序播放。

按空格或回车直接进入下一张图。

（以下“顺序”指文件名升序排序的顺序）

按D打开顺序下一张图，按A打开顺序上一张图。

按X打开顺序下一文件夹，按Z打开顺序上一文件夹。

按C打开该文件夹的顺序第一张图，按V打开该文件夹的顺序最后一张图。

当按下Q会使程序在当前图片所在的文件夹下进行随机播放，按下W会使程序在该文件夹的上一级文件夹下进行随机播放，按下E则会使程序在该文件夹的上两级文件夹下进行随机播放。按下R返回原来的随机模式。



**背景音乐控制：**

由于不太常用，背景音乐控制为键盘右侧控制

按Enter随机播放音乐库里的音乐，可重复按。

按右Shift暂停或继续播放。

按方向上下调整音量，一次±5

按方向左右快进快退，一次±10秒



**鼠标操作**

鼠标左键单击屏幕，相当于按下q键，使程序在该图片所在的文件夹下进行随机播放；再单击屏幕，相当于按下r键，取消在该文件夹随机播放，返回原来的随机方式。

单击操作是给手机设计的方式，在手机上安装RD Client远程控制该电脑后，触屏就相当于鼠标单击，可以使用这种方式简单地使用该程序。另外RD Client附带的键盘具有PC上的所有按键，所以用手机也是能完全控制该程序的，就是有点麻烦。



**搜索**

按下Tab后，直接用英文键盘输入英文、拼音、拼音首字母即可，再按下Tab开始搜索。如果搜索到某文件夹的名称符合要求，则会直接进入该文件夹开始播放。按R回到搜索前的状态。

比如你想搜索名为“风景”的文件夹，可以按 Tab键，输入 fj ，再按Tab 来进入该文件夹，或者按 Tab键，输入fengjing，再按Tab 也可。

在按下Tab后，原先的键盘左侧的按键都不会触发其原有的功能，除了按下Esc仍能直接退出程序。



**其他特色功能**

背景颜色可自定义。

若参数TWO_COLUMNS为真，则当屏幕的宽大于高（即正常电脑屏幕大小）时，当随机到照片为竖屏时，一页同时浏览两张竖屏照片。屏幕的宽小于于高（可能是手机）时，当随机到照片为横屏时，一页同时浏览两张横屏照片。

锐化和差值功能，使图片浏览时更清晰。

可以不全屏播放了。FULL_SCREEN = False时不全屏，同时窗口的初始大小为FACTOR_WIDTH*屏幕宽度 x FACTOR_HEIGHT *屏幕高度。出现位置由SCREEN_POSITION决定，详情见参数。



## 参数

```python
LOOP_TIME = 2000  # 幻灯片播放间隔（单位：毫秒）
SHUFFLE = True  # 是否开启图片随机播放
TWO_COLUMNS = True  # 若为真，则屏幕的宽大于高时，当随机到照片为竖屏时，一页浏览两张竖屏照片。屏幕的宽小于于高时，当随机到照片为横屏时，一页浏览两张横屏照片
WHEN_REACH_END_OF_FOLDER = FOLDER_CROSS  # 顺序播放时，到文件夹末尾后的行为，FOLDER_REPEAT为文件夹内循环，FOLDER_CROSS为进入下一文件夹
MUSIC_LIB = ['E:/MUSIC/']  # 音乐库路径
DEFAULT_LIB = './pic'  # 默认库
MY_SELECT_LIB = [['./pic', './pic/good', './pic/best', './pic/',
                  'E:/VirtualBox/zz', 'E:/VirtualBox/nmz',
                  'E:/VirtualBox/xww', 'E:/VirtualBox/saku',
                  'E:/VirtualBox/zyx']
             , ['E:/VirtualBox/wyc']

                 ]  # 你的图片库路径
SHOULD_NOT_GO_INTO_THESE_FOLDERS = ["一般", "不好看", "没法看", "视频"]  # 如果文件夹名称包含其中任意一个关键字，则不进入该文件夹
#      MY_SELECT_LIB的行列对应按键关系:
#                 1 2 3 4 5 6 7 8 9 0
#           F1
#           F2
#           F3
#           ...
#           F12
BACKGROUND_COLOR = 'black'  # 背景颜色,可选 black,white,pink,green,blue,red,orange等，或者直接设为'#FFDAB9'等值
SHARPEN_ON = True # 开启锐化。开启锐化后图片预览效果会变好一点。
FULL_SCREEN = False  # 全屏。只有不全屏，下面的FACTOR_WIDTH、FACTOR_HEIGHT、POSITION才会生效。
FACTOR_WIDTH = 0.5  # 打开时的窗口相对于屏幕的宽度比例
FACTOR_HEIGHT = FACTOR_WIDTH  # 打开时的窗口相对于屏幕的高度比例
SCREEN_POSITION = 1  # 如下图所示。数字代表了打开程序时，程序出现在屏幕中的位置

# POSITION 可选位置：
# 左上角 1 2 3 右上角
#       4 5 6
# 左下角 7 8 9 右下角
```



# **HVidBrowser**

## **用法**

直接把单个或多个文件夹拖入Python脚本上即可全屏播放视频，如果直接打开该脚本，它就会打开默认库DEFAULT_LIB，你可以在打开脚本后按F1到F12和0到9选择MY_SELECT_LIB中的一个库进行播放，一个库可以是多个文件夹的集合。F1到F12为库的行数，1234567890为库的列数，按下F1到F12和0到9任意一个按键即可播放该库。

视频默认单循环，需要按空格或回车来打开下一个视频。

有**手机模式**，会在屏幕两边出现两个灰黑色的条，按左边的条切换到下一个视频，按右边的条快进30秒。进度条变宽，点击进度条即可跳转到对应位置。把参数PHONE_SUPPORT设置为真，则为手机模式。适用于用RD Client 远程控制时使用，虽然帧率不高，画面也不算特别清晰，但我认为还算可以接受。



**视频播放器和图片播放器操作基本一致，先说一下不一样的按键：**

图片播放器中按左Shift和Ctrl增减幻灯片间隔时间。在视频播放器中改为左Shift快进10秒，左Ctrl后退10秒。

视频播放器中，按V提高播放速度0.1倍，按C降低播放速度0.1倍。



**一些视频播放的特色功能：**

删除功能：如果参数 CAN_DELETE_FILE 为真，则可按Del删除键来直接删除当前播放的视频。若为假，则按Del删除键只会给视频的文件名添加一个标记为‘不好看’的前缀。前缀的内容为参数ADD_THIS_TO_FILE_IF_NOT_DELETE 的内容。

【视频有进度条，可选打开或关闭，可自定义颜色。当鼠标移至进度条上，则会将视频跳转到鼠标所指的进度（之所以这样控制进度条，是因为vlc直接获取了tkinter的控件的hwnd进行输出，所以这个播放器控件就无法获取鼠标事件了，而进度条如果太宽会影响观看体验，所以就改为很细的一条进度条，只要鼠标一进入这个进度条就跳转，实际操作体验还可以）。】

收藏功能：按左Alt在参数COLLECTION_FOLDER所指的文件夹下创建一个到该文件的快捷方式。



**完整操作**



本脚本为左侧键盘操作，如有需要可以在程序里自行修改键位。

按Esc退出。按S或右Shift来暂停或播放。

按左Shift或方向右键快进10秒，左Ctrl或方向左键后退10秒。

按上下方向键调节音量。

按F关闭或打开随机播放。

按空格或回车直接进入下一个视频。

按V提高播放速度0.1倍，按C降低播放速度0.1倍。

按Tab进入搜索，输入要搜索的内容后，再按Tab进行搜索。

按Del删除或标注不好看，取决于参数CAN_DELETE_FILE.

按左Alt收藏，即在参数COLLECTION_FOLDER所指的文件夹下创建一个到该文件的快捷方式。

鼠标移动到进度条上，即可将视频定位到所指位置。



（以下“顺序”指文件名升序排序的顺序）

按D打开顺序下一个视频，按A打开顺序上一个视频。

按X打开顺序下一个文件夹，按Z打开顺序上一个文件夹。



## 参数

```python
SHUFFLE = True  # 是否开启视频随机播放
WHEN_REACH_END_OF_FOLDER = FOLDER_REPEAT  # 顺序播放时，到文件夹末尾后的行为，FOLDER_REPEAT为文件夹内循环，FOLDER_CROSS为进入下一文件夹
DEFAULT_LIB = './vid/'  # 默认库
MY_SELECT_LIB = [['E:/VirtualBox/vid/nyo', 'E:/VirtualBox/vid/nier', 'E:/VirtualBox/VirtualBox/vid/honoka'],
                 ['E:/VirtualBox/avi/']
                 ]  # 你的视频库路径
SHOULD_NOT_GO_INTO_THESE_FOLDERS = ["一般", "不好看", "没法看", "图"]  # 如果文件夹名称包含其中任意一个关键字，则不进入该文件夹
SHOULD_NOT_GO_INTO_THESE_FILES = ["一般", "不好看", "没法看"]  # 如果文件名包含其中任意一个关键字，则不打开该文件
COLLECTION_FOLDER = 'E:/VirtualBox/collection/'  # 你的收藏夹地址。收藏的视频的快捷方式会保存在该文件夹。
CAN_DELETE_FILE = True  # 如果为真，则按下Del删除键时，会直接删除正在播放的文件。
ADD_THIS_TO_FILE_IF_NOT_DELETE = '一般'  # 如果CAN_DELETE_FILE为假，则给该文件的文件名前面面添加一个 ADD_THIS_TO_FILE_IF_NOT_DELETE的内容
COLOR_PROGRESS_BAR = 'red'  # 进度条颜色

FULL_SCREEN = False  # 全屏。只有不全屏，下面的FACTOR_WIDTH、FACTOR_HEIGHT、POSITION才会生效。
FACTOR_WIDTH = 0.5  # 打开时的窗口相对于屏幕的宽度比例
FACTOR_HEIGHT = FACTOR_WIDTH  # 打开时的窗口相对于屏幕的高度比例
SCREEN_POSITION = 1  # 如下图所示。数字代表了打开程序时，程序出现在屏幕中的位置

# POSITION 可选位置：
# 左上角 1 2 3 右上角
#       4 5 6
# 左下角 7 8 9 右下角

PHONE_SUPPORT = False  # 触摸屏模式。进度条变宽。在屏幕左上角和右上角出现按键，按左边的键切换到下一个视频，按右边的键快进30秒。
TOUCH_BAR_COLOR = '#202020'  # 触摸条的颜色。
```



# 问题以及解决方法（不用看）

HPicBroswer：

1. 刚开始试半天都无法让tikinter的label显示新的图片，后来上网查发现除了要加label.configure(image=photo)，还要加label.image = photo才会使label更新图片。



HVidBrowser：

1. 最开始使用的是VLC的MediaPlayer，但是只要视频的播放一结束，这个MediaPlayer对象就怎么也操作不了了，这样我就没办法让一个视频循环播放了。我给它添加播放结束事件侦听器，但没有触发（所有事件列表见[此](https://www.olivieraubert.net/vlc/python-ctypes/doc/vlc.EventType-class.html)）。MediaPlayerPositionChanged事件并不准确，所以不能用来在播放快结束时使视频跳回最开始的地方。

   上网查发现得用VLC的MediaListPlayer，添加播放列表后set_playback_mode(vlc.PlaybackMode.loop) 设置播放模式为循环即可。

2. 视频切换时莫名其妙卡死。上网查到是因为视频渲染到了tkinter的窗体里，所以执行stop()结束播放命令时，偶尔会和tkinter的窗口消息（不知道具体叫啥）发生冲突，然后卡死。解决方法是，切换视频时，先把vlc输出到的canvas元件destroy()，然后根窗体实例更新top.update()，然后MediaListPlayer.stop()结束播放，再删除vlc实例，（不结束就删除的话，内存就不会释放，切换几个视频分分钟爆内存），新建一模一样大小的canvas在原位置，top.update()，等待canvas.winfo_ismapped()，然后获取这个canvas的hwnd，新建vlc实例，设置hwnd，再让tkinter的根窗体实例更新top.update()，vlc开始播放即可。



# 目前要改进的地方（不会改了）

**HPicBrowser：**

1. 锐化功能还要多试验一下，看设置参数为多少合适。

2. 幻灯片切换没有特效。

   

**HVidBrowser：**

1. 循环播放视频的情况下，重新开始循环时会卡顿一下。解决的方法是把视频直接读到内存中，然后让vlc读内存内容。但目前找不到相关方法，官方文档难读的很。
