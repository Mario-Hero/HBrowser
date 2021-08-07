import platform
import vlc
import time

class Player:

    def __init__(self):
        self.media = vlc.MediaListPlayer()
        self.player = vlc.Instance()
        self.media_list = vlc.MediaList()
        self.media.set_playback_mode(vlc.PlaybackMode.loop)
        # self.media.get_media_player().video_set_mouse_input(True)

    def __del__(self):
        # self.media.stop()
        self.stop()
        # del self.player
        # del self.media
        # del self.media_list
        del self


    # 设置待播放的url地址或本地文件路径，每次调用都会重新加载资源
    def set_url(self, url):
        mediaListTemp = vlc.MediaList()
        mediaListTemp.add_media(self.player.media_new(url))
        self.media_list = mediaListTemp
        self.media.set_media_list(self.media_list)

    # 播放 成功返回0，失败返回-1
    def play(self, path=None):
        if path:
            '''
            stateTemp = self.media.get_media_player().get_state()
            if stateTemp == vlc.State.Paused or stateTemp == vlc.State.Playing or stateTemp == vlc.State.Opening:
                hwndTemp = self.media.get_media_player().get_hwnd()
                if hwndTemp:
                    self.set_window(0)
                    self.media.stop()
                    self.set_window(hwndTemp)
                else:
                    self.media.stop()
            self.media.stop()
            '''
            self.set_url(path)
            # time.sleep(0.05)
            self.media.play()

        else:
            self.media.play()

    # 暂停或播放
    def pauseOrPlay(self):
        if self.media.get_media_player().is_playing():
            self.media.get_media_player().pause()
        else:
            self.media.get_media_player().set_pause(0)

    def forward(self, ms=30000):
        return self.media.get_media_player().set_time(self.media.get_media_player().get_time() + ms)

    def backward(self, ms=30000):
        return self.media.get_media_player().set_time(self.media.get_media_player().get_time() - ms)

    # 恢复
    def resume(self):
        self.media.get_media_player().set_pause(0)

    # 停止
    def stop(self):
        self.media.stop()

    # 释放资源
    def release(self):
        return self.media.get_media_player().release()

    # 是否正在播放
    def is_playing(self):
        return self.media.get_media_player().is_playing()

    # 已播放时间，返回毫秒值
    def get_time(self):
        return self.media.get_media_player().get_time()

    # 拖动指定的毫秒值处播放。成功返回0，失败返回-1 (需要注意，只有当前多媒体格式或流媒体协议支持才会生效)
    def set_time(self, ms):
        return self.media.get_media_player().set_time(ms)

    # 音视频总长度，返回毫秒值
    def get_length(self):
        return self.media.get_media_player().get_length()

    # 获取当前音量（0~100）
    def volumeUp(self):
        return self.media.get_media_player().audio_set_volume(self.media.get_media_player().audio_get_volume() + 5)

    def volumeDown(self):
        return self.media.get_media_player().audio_set_volume(self.media.get_media_player().audio_get_volume() - 5)

    def get_volume(self):
        return self.media.get_media_player().audio_get_volume()

    # 设置音量（0~100）
    def set_volume(self, volume):
        return self.media.get_media_player().audio_set_volume(volume)

    # 返回当前状态：正在播放；暂停中；其他
    def get_state(self):
        state = self.media.get_media_player().get_state()
        if state == vlc.State.Playing:
            return 1
        elif state == vlc.State.Paused:
            return 0
        else:
            return state


    def is_Opening(self):
        return self.media.get_media_player().get_state() == vlc.State.Opening


    # 当前播放进度情况。返回0.0~1.0之间的浮点数
    def get_position(self):
        return self.media.get_media_player().get_position()

    # 拖动当前进度，传入0.0~1.0之间的浮点数(需要注意，只有当前多媒体格式或流媒体协议支持才会生效)
    def set_position(self, float_val):
        return self.media.get_media_player().set_position(float_val)

    # 获取当前文件播放速率
    def get_rate(self):
        return self.media.get_media_player().get_rate()

    # 设置播放速率（如：1.2，表示加速1.2倍播放）
    def set_rate(self, rate):
        return self.media.get_media_player().set_rate(rate)

    def faster(self):
        self.media.get_media_player().set_rate(self.media.get_media_player().get_rate() + 0.1)

    def slower(self):
        if self.media.get_media_player().get_rate() > 0.1:
            self.media.get_media_player().set_rate(self.media.get_media_player().get_rate() - 0.1)

    # 设置宽高比率（如"16:9","4:3"）
    def set_ratio(self, ratio):
        self.media.video_set_scale(0)  # 必须设置为0，否则无法修改屏幕宽高
        self.media.video_set_aspect_ratio(ratio)

    # 注册监听器
    def add_callback(self, event_type, callback):
        self.media.get_media_player().event_manager().event_attach(event_type, callback)

    # 移除监听器
    def remove_callback(self, event_type):
        self.media.get_media_player().event_manager().event_detach(event_type)

    def set_window(self, wm_id):
        if platform.system() == 'Windows':
            self.media.get_media_player().set_hwnd(wm_id)
        else:
            self.media.get_media_player().set_xwindow(wm_id)
