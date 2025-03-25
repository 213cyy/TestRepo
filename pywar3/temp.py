class GeosetAnim:
    def __init__(self, geoset_id, keyframes):
        self.geoset_id = geoset_id
        self.keyframes = keyframes

    def interpolate_color(self, t):
        # t 是归一化时间 [0, 1]
        # 在这里实现贝塞尔曲线插值
        # 这只是一个占位符
        return self._bezier_interpolate(t, self.keyframes)

    def _bezier_interpolate(self, t, keyframes):
        # 实现具体的贝塞尔插值逻辑
        # 这部分需要根据关键帧和切线计算
        # 这里只是一个简单的线性插值示例
        start_kf = keyframes[0]
        end_kf = keyframes[-1]
        start_color = start_kf['color']
        end_color = end_kf['color']

        # 简单的线性插值
        interpolated_color = [
            start_color[i] + (end_color[i] - start_color[i]) * t
            for i in range(3)
        ]
        return interpolated_color

# 示例数据
keyframes = [
    {'time': 0, 'color': [0, 0, 0.862745], 'in_tan': [0, 0, 0.862745], 'out_tan': [0, 0, 0.862745]},
    {'time': 0.22, 'color': [0, 0, 0.862745], 'in_tan': [0, 0, 0.862745], 'out_tan': [0, 0.299346, 0.884967]},
    # 其他关键帧...
]

geoset_anim = GeosetAnim(geoset_id=0, keyframes=keyframes)

# 在渲染循环中使用
def render(time):
    t = normalize_time(time)  # 将时间归一化到 [0, 1]
    color = geoset_anim.interpolate_color(t)
    apply_color_to_geoset(geoset_anim.geoset_id, color)

def normalize_time(current_time):
    # 根据动画总时长将当前时间归一化
    animation_duration = 1080  # 假设总时长
    return current_time / animation_duration

def apply_color_to_geoset(geoset_id, color):
    # 将计算出的颜色应用到地理集合
    pass