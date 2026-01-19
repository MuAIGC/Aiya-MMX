# ~/ComfyUI/custom_nodes/ComfyUI-Aiya-MMX/nodes/prompt_kit.py
from __future__ import annotations
from ..register import register_node
import random

CATEGORY = "哎呀✦MMX/prompt"

# ================================================================================
# 一、图片维度节点（7 个）
# ================================================================================
# ① 纯视角
PURE_ANGLES = {
    "随机": ("", ""),
    "正面": ("从正面视角拍摄", "shot from a front angle"),
    "正侧": ("从正侧视角拍摄", "shot from a perpendicular side angle"),
    "斜侧(3/4)": ("从斜侧3/4视角拍摄", "shot from a three-quarter angle"),
    "背面": ("从背面视角拍摄", "shot from a rear angle"),
    "过肩": ("从过肩视角拍摄", "shot from an over-the-shoulder angle"),
    "鸟瞰": ("从鸟瞰视角拍摄", "shot from a bird’s-eye angle"),
    "俯视": ("从俯视视角拍摄", "shot from a high-angle looking down"),
    "平视": ("从平视视角拍摄", "shot from an eye-level angle"),
    "仰视": ("从仰视视角拍摄", "shot from a low-angle looking up"),
    "虫眼": ("从虫眼视角拍摄", "shot from a bug’s-eye angle"),
    "极远景": ("从极远景视角拍摄", "shot from an extreme long-shot angle"),
    "远景": ("从远景视角拍摄", "shot from a long-shot angle"),
    "全身": ("从全身视角拍摄", "shot from a full-length angle"),
    "中景": ("从中景视角拍摄", "shot from a medium-shot angle"),
    "中近景": ("从中近景视角拍摄", "shot from a medium-close-up angle"),
    "近景": ("从近景视角拍摄", "shot from a close-up angle"),
    "特写": ("从特写视角拍摄", "shot from a close-up angle"),
    "极特写": ("从极特写视角拍摄", "shot from an extreme close-up angle"),
    "荷兰角": ("从荷兰角视角拍摄", "shot from a Dutch-tilt angle"),
    "主观POV": ("从主观POV视角拍摄", "shot from a first-person POV angle"),
    "第三人称": ("从第三人称视角拍摄", "shot from a third-person angle"),
    "镜面反射": ("从镜面反射视角拍摄", "shot from a mirror-reflection angle"),
    "水面反射": ("从水面反射视角拍摄", "shot from a water-reflection angle"),
    "玻璃反射": ("从玻璃反射视角拍摄", "shot from a glass-reflection angle"),
    "剪影": ("从剪影视角拍摄", "shot from a back-lit silhouette angle"),
    "阴影": ("从阴影视角拍摄", "shot from a shadow-only angle"),
    "手持": ("从手持视角拍摄", "shot from a handheld angle"),
    "滑轨平移": ("从滑轨平移视角拍摄", "shot from a slider-pan angle"),
    "摇臂上升": ("从摇臂上升视角拍摄", "shot from a crane-rising angle"),
    "摇臂下降": ("从摇臂下降视角拍摄", "shot from a crane-lowering angle"),
    "推镜": ("从推镜视角拍摄", "shot from a dolly-in angle"),
    "拉镜": ("从拉镜视角拍摄", "shot from a dolly-out angle"),
    "侧跟踪": ("从侧跟踪视角拍摄", "shot from a side-tracking angle"),
    "后跟踪": ("从后跟踪视角拍摄", "shot from a back-tracking angle"),
    "环绕": ("从环绕视角拍摄", "shot from a 360-orbit angle"),
    "甩鞭": ("从甩鞭摇镜视角拍摄", "shot from a whip-pan angle"),
    "变焦推拉": ("从变焦推拉视角拍摄", "shot from a zoom-push-pull angle"),
    "静止锁定": ("从静止锁定视角拍摄", "shot from a locked-off angle"),
    "航拍正俯": ("从航拍正俯视角拍摄", "shot from a drone straight-down angle"),
    "航拍45°": ("从航拍45°俯视角拍摄", "shot from a drone 45° downward angle"),
    "卫星俯视": ("从卫星俯视视角拍摄", "shot from a satellite top-down angle"),
    "潜望镜": ("从潜望镜视角拍摄", "shot from a periscope angle"),
    "钥匙孔": ("从钥匙孔视角拍摄", "shot from a keyhole angle"),
    "窥视孔": ("从窥视孔视角拍摄", "shot from a peephole angle"),
    "裂缝": ("从裂缝视角拍摄", "shot from a crack-in-the-wall angle"),
    "栅栏缝": ("从栅栏缝视角拍摄", "shot from a through-the-fence angle"),
    "车轮底": ("从车轮底视角拍摄", "shot from a under-the-wheel angle"),
    "桌面底": ("从桌面底视角拍摄", "shot from a under-the-table angle"),
    "书架缝": ("从书架缝视角拍摄", "shot from a between-books angle"),
    "楼梯间": ("从楼梯间仰视视角拍摄", "shot from a stairwell-looking-up angle"),
    "电梯顶": ("从电梯顶俯视视角拍摄", "shot from an elevator-top-looking-down angle"),
    "冰箱内": ("从冰箱内向外视角拍摄", "shot from inside-the-fridge-looking-out angle"),
    "衣柜内": ("从衣柜内向外视角拍摄", "shot from inside-the-closet-looking-out angle"),
    "车窗侧": ("从车窗侧视角拍摄", "shot from a side-car-window angle"),
    "后视镜": ("从后视镜视角拍摄", "shot from a rear-view-mirror angle"),
    "显微镜": ("从显微镜视角拍摄", "shot from a microscopic angle"),
    "望远镜": ("从望远镜视角拍摄", "shot from a telescopic angle"),
    "门猫眼": ("从门猫眼视角拍摄", "shot from a door-peephole angle"),
    "窗框": ("从窗框视角拍摄", "shot from a window-frame angle"),
    "拱廊": ("从拱廊框景视角拍摄", "shot from an archway-framing angle"),
    "隧道": ("从隧道尽头视角拍摄", "shot from a tunnel-end angle"),
    "管道": ("从管道内部视角拍摄", "shot from a inside-the-pipe angle"),
    "纸筒": ("从纸筒窥视视角拍摄", "shot from a paper-tube peephole angle"),
    "杯底": ("从杯底仰视视角拍摄", "shot from a bottom-of-the-cup angle"),
    "灯罩内": ("从灯罩内向外视角拍摄", "shot from inside-the-lamp-shade angle"),
    "花瓶口": ("从花瓶口俯视视角拍摄", "shot from a vase-mouth looking-down angle"),
    "沙漏腰": ("从沙漏腰视角拍摄", "shot from a hourglass-waist angle"),
    "相框": ("从相框内向外视角拍摄", "shot from inside-a-photo-frame angle"),
    "屏幕": ("从屏幕内向外视角拍摄", "shot from inside-the-screen-looking-out angle"),
    "手机屏": ("从手机屏视角拍摄", "shot from a phone-screen angle"),
    "手表镜": ("从手表镜反射视角拍摄", "shot from a watch-glass reflection angle"),
    "玻璃球": ("从玻璃球折射视角拍摄", "shot from a glass-ball refraction angle"),
    "水晶棱镜": ("从水晶棱镜视角拍摄", "shot from a crystal-prism angle"),
    "水滴": ("从水滴折射视角拍摄", "shot from a water-droplet refraction angle"),
    "雨滴": ("从雨滴视角拍摄", "shot from a raindrop surface angle"),
    "肥皂泡": ("从肥皂泡视角拍摄", "shot from a soap-bubble surface angle"),
    "鱼眼": ("从鱼眼视角拍摄", "shot from a fisheye angle"),
    "LensBaby": ("从LensBaby偏移视角拍摄", "shot from a LensBaby tilt-shift angle"),
    "针孔": ("从针孔视角拍摄", "shot from a pinhole angle"),
    "Split-Diopter": ("从Split-Diopter半裂焦视角拍摄", "shot from a split-diopter angle"),
    "SnorriCam": ("从SnorriCam胸挂视角拍摄", "shot from a SnorriCam chest-mount angle"),
    "GoPro超视": ("从GoPro超视角拍摄", "shot from a GoPro SuperView angle"),
    "360全景": ("从360全景视角拍摄", "shot from a 360-panorama angle"),
    "VR180": ("从VR180立体视角拍摄", "shot from a VR180 stereoscopic angle"),
    "无人机环绕": ("从无人机环绕视角拍摄", "shot from a drone orbit angle"),
    "无人机俯冲": ("从无人机俯冲视角拍摄", "shot from a drone dive angle"),
    "无人机拉升": ("从无人机拉升视角拍摄", "shot from a drone rise angle"),
    "无人机倒退": ("从无人机倒退视角拍摄", "shot from a drone pull-back angle"),
    "无人机侧飞": ("从无人机侧飞视角拍摄", "shot from a drone side-flight angle"),
    "无人机跟踪": ("从无人机跟踪视角拍摄", "shot from a drone tracking angle"),
    "无人机环绕上升": ("从无人机环绕上升视角拍摄", "shot from a drone orbit-rise angle"),
    "无人机环绕下降": ("从无人机环绕下降视角拍摄", "shot from a drone orbit-descend angle"),
}

class PureCameraAngle:
    DESCRIPTION = "📷 纯视角术语（无滤镜）（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"视角": (list(PURE_ANGLES.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 视角, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 视角 == "随机":
            random.seed(seed)
            视角 = random.choice(list(PURE_ANGLES.keys())[1:])
        return PURE_ANGLES[视角]

# ② 专业滤镜
PRO_FILTERS = {
    "随机": ("", ""),
    "高反差黑白": ("高反差黑白滤镜", "high-contrast monochrome filter"),
    "低反差柔灰": ("低反差柔灰滤镜", "low-contrast soft-grey filter"),
    "硬调黑白": ("硬调黑白滤镜", "hard-tone black-and-white filter"),
    "中间调": ("中间调黑白滤镜", "mid-tone monochrome filter"),
    "Kodak Portra 400": ("Kodak Portra 400 胶片滤镜", "Kodak Portra 400 film filter"),
    "Kodak Gold 200": ("Kodak Gold 200 胶片滤镜", "Kodak Gold 200 film filter"),
    "Fuji Velvia 50": ("Fuji Velvia 50 胶片滤镜", "Fuji Velvia 50 film filter"),
    "Fuji Pro 400H": ("Fuji Pro 400H 胶片滤镜", "Fuji Pro 400H film filter"),
    "Kodak Ektar 100": ("Kodak Ektar 100 胶片滤镜", "Kodak Ektar 100 film filter"),
    "Kodak Tri-X 400": ("Kodak Tri-X 400 胶片滤镜", "Kodak Tri-X 400 film filter"),
    "Ilford HP5 Plus": ("Ilford HP5 Plus 胶片滤镜", "Ilford HP5 Plus film filter"),
    "Teal-Orange Blockbuster": ("Teal-Orange 大片LUT", "teal-orange blockbuster LUT"),
    "SLog3 to 709": ("SLog3 to Rec709 标准LUT", "SLog3 to Rec709 standard LUT"),
    "CLog to 709": ("CLog to Rec709 标准LUT", "CLog to Rec709 standard LUT"),
    "Kodak 2383 Print": ("Kodak 2383 打印胶片LUT", "Kodak 2383 print film LUT"),
    "Fuji 3513 Print": ("Fuji 3513 打印胶片LUT", "Fuji 3513 print film LUT"),
    "Arri Alexa Rec709": ("Arri Alexa Rec709 LUT", "Arri Alexa Rec709 LUT"),
    "DJI D-Cinelike": ("DJI D-Cinelike 标准LUT", "DJI D-Cinelike standard LUT"),
    "钨丝灯暖调": ("钨丝灯暖调滤镜", "tungsten warm-tone filter"),
    "日光冷调": ("日光冷调滤镜", "daylight cool-tone filter"),
    "阴雨天冷调": ("阴雨天冷调滤镜", "overcast cool-tone filter"),
    "烛光暖调": ("烛光暖调滤镜", "candle-light warm-tone filter"),
    "霓虹冷调": ("霓虹冷调滤镜", "neon cool-tone filter"),
    "S曲线增强": ("S曲线对比增强滤镜", "S-curve contrast-enhancement filter"),
    "反S曲线柔化": ("反S曲线柔化滤镜", "inverted S-curve softening filter"),
    "硬 clipping": ("硬 clipping 对比滤镜", "hard-clipping contrast filter"),
    "软 clipping": ("软 clipping 对比滤镜", "soft-clipping contrast filter"),
    "高饱和": ("高饱和滤镜", "high-saturation filter"),
    "低饱和": ("低饱和滤镜", "low-saturation filter"),
    "零饱和": ("零饱和黑白滤镜", "zero-saturation monochrome filter"),
    "自然饱和": ("自然饱和保留滤镜", "natural-saturation-preserving filter"),
    "交叉冲洗": ("交叉冲洗滤镜", "cross-processing filter"),
    "漂白绕过": ("漂白绕过滤镜", "bleach-bypass filter"),
    "push 处理": ("push 处理增感滤镜", "push-process gain filter"),
    "pull 处理": ("pull 处理减感滤镜", "pull-process reduce filter"),
    "复古褪色": ("复古褪色滤镜", "vintage fade filter"),
    "银版照相": ("银版照相风格滤镜", "daguerreotype style filter"),
    "蓝晒印相": ("蓝晒印相风格滤镜", "cyanotype style filter"),
    "锡版照相": ("锡版照相风格滤镜", "tintype style filter"),
    "HDR 合并": ("HDR 合并滤镜", "HDR merge filter"),
    "CLAHE 局部增强": ("CLAHE 局部对比增强滤镜", "CLAHE local contrast enhancement filter"),
    "去雾": ("去雾滤镜", "dehaze filter"),
    "锐化": ("锐化滤镜", "sharpening filter"),
    "高斯柔焦": ("高斯柔焦滤镜", "Gaussian soft-focus filter"),
    "扩散滤镜": ("扩散柔焦滤镜", "diffusion soft-focus filter"),
    "颗粒添加": ("颗粒添加滤镜", "grain-addition filter"),
    "噪点削减": ("噪点削减滤镜", "noise-reduction filter"),
    "摩尔纹削减": ("摩尔纹削减滤镜", "moiré-reduction filter"),
    "边缘增强": ("边缘增强滤镜", "edge-enhancement filter"),
    "浮雕效果": ("浮雕效果滤镜", "emboss-effect filter"),
    "负片反转": ("负片反转滤镜", "negative-inversion filter"),
    "红外模拟": ("红外模拟滤镜", "infrared-simulation filter"),
    "X光模拟": ("X光模拟滤镜", "X-ray-simulation filter"),
    "热成像模拟": ("热成像模拟滤镜", "thermal-simulation filter"),
}

class ProFilterTerm:
    DESCRIPTION = "🎞️ 专业滤镜术语（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"滤镜": (list(PRO_FILTERS.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 滤镜, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 滤镜 == "随机":
            random.seed(seed)
            滤镜 = random.choice(list(PRO_FILTERS.keys())[1:])
        return PRO_FILTERS[滤镜]

# ③ 光照方向
LIGHT_DIR = {
    "随机": ("", ""),
    "顶光": ("顶光", "overhead light"),
    "45°侧前": ("45°侧前主光", "45° key light from front-side"),
    "正侧光": ("正侧光", "side light"),
    "逆光": ("逆光", "back light"),
    "轮廓光": ("轮廓光", "rim light"),
    "底光": ("底光", "under light"),
    "顶逆光": ("顶逆光", "top-back light"),
    "低角度仰光": ("低角度仰光", "low-angle uplight"),
    "斜顶光": ("斜顶光", "oblique top light"),
    "侧前顶光": ("侧前顶光", "front-side top light"),
    "侧后顶光": ("侧后顶光", "back-side top light"),
    "正前顶光": ("正前顶光", "front-top light"),
    "正后顶光": ("正后顶光", "back-top light"),
    "环绕顶光": ("环绕顶光", "overhead ring light"),
    "蝴蝶顶光": ("蝴蝶顶光", "butterfly overhead light"),
    "伦勃朗侧光": ("伦勃朗侧光", "Rembrandt side light"),
    "分割侧光": ("分割侧光", "split side light"),
    "短侧光": ("短侧光", "short-side light"),
    "宽侧光": ("宽侧光", "broad-side light"),
    "侧逆光": ("侧逆光", "side-back light"),
    "低侧光": ("低侧光", "low-side light"),
    "高侧光": ("高侧光", "high-side light"),
    "交叉背光": ("交叉背光", "cross back light"),
    "正前平光": ("正前平光", "flat front light"),
    "侧前填充": ("侧前填充光", "front-side fill"),
    "背填充": ("背填充光", "back fill light"),
    "顶填充": ("顶填充光", "overhead fill light"),
    "底填充": ("底填充光", "under fill light"),
    "反光板跳光": ("反光板跳光", "bounce light from reflector"),
    "柔光箱顶光": ("柔光箱顶光", "softbox overhead light"),
    "雷达罩前光": ("雷达罩前光", "beauty-dish front light"),
    "抛物面聚焦": ("抛物面聚焦光", "parabolic focused light"),
    "菲涅耳硬光": ("菲涅耳硬光", "Fresnel hard light"),
    "LED环形顶光": ("LED环形顶光", "LED ring overhead light"),
    "日窗侧光": ("日窗侧光", "window daylight side"),
    "云漫射顶光": ("云漫射顶光", "cloud-diffused top light"),
    "霓虹侧光": ("霓虹侧光", "neon side light"),
    "烛光底光": ("烛光底光", "candle under light"),
    "火光侧光": ("火光侧光", "firelight side"),
    "月光顶光": ("月光顶光", "moonlight overhead"),
}

class LightDirection:
    DESCRIPTION = "💡 光照方向（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"方向": (list(LIGHT_DIR.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 方向, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 方向 == "随机":
            random.seed(seed)
            方向 = random.choice(list(LIGHT_DIR.keys())[1:])
        return LIGHT_DIR[方向]

# ④ 光质
LIGHT_QUALITY = {
    "随机": ("", ""),
    "硬光": ("硬光", "hard light"),
    "柔光": ("柔光", "soft light"),
    "漫射光": ("漫射光", "diffused light"),
    "聚光": ("聚光", "focused beam"),
    "散光": ("散光", "spilled light"),
    "斑驳投影": ("斑驳投影", "dappled projection"),
    "平行光束": ("平行光束", "collimated beam"),
    "点光源硬光": ("点光源硬光", "point-source hard light"),
    "面光源柔光": ("面光源柔光", "area-source soft light"),
    "球面漫射": ("球面漫射", "spherical diffused"),
    "柱面光": ("柱面光", "cylindrical light"),
    "环形均匀": ("环形均匀光", "ring uniform light"),
    "二向柔光": ("二向柔光", "bidirectional soft light"),
    "天幕柔光": ("天幕柔光", "skydome soft light"),
    "阴云漫射": ("阴云漫射", "overcast diffused"),
    "薄云柔化": ("薄云柔化", "thin-cloud softened"),
    "窗帘柔光": ("窗帘柔光", "curtain-softened light"),
    "柔光箱": ("柔光箱光", "softbox light"),
    "雷达罩": ("雷达罩光", "beauty-dish light"),
    "抛物面柔光": ("抛物面柔光", "parabolic soft light"),
    "菲涅耳硬光": ("菲涅耳硬光", "Fresnel hard light"),
    "LED点硬": ("LED点硬光", "LED point hard"),
    "LED面柔": ("LED面柔光", "LED panel soft"),
    "钨丝聚焦": ("钨丝聚焦硬光", "tungsten focused hard"),
    "卤素硬光": ("卤素硬光", "halogen hard light"),
    "HMI聚光": ("HMI聚光", "HMI focused beam"),
    "激光束": ("激光束", "laser beam"),
    "荧光漫射": ("荧光漫射", "fluorescent diffused"),
    "日窗软": ("日窗软光", "window soft daylight"),
    "反跳柔光": ("反跳柔光", "bounce soft light"),
    "云幕柔光": ("云幕柔光", "cloud-dome soft"),
    "雾幕散射": ("雾幕散射", "fog-screen scattered"),
    "纱幕散射": ("纱幕散射", "scrim-scattered light"),
    "水纹投影": ("水纹投影", "water-pattern projection"),
    "树叶斑驳": ("树叶斑驳", "leaf-dappled light"),
}

class LightQuality:
    DESCRIPTION = "🌈 光质（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"光质": (list(LIGHT_QUALITY.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 光质, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 光质 == "随机":
            random.seed(seed)
            光质 = random.choice(list(LIGHT_QUALITY.keys())[1:])
        return LIGHT_QUALITY[光质]

# ⑤ 天气大气
WEATHER_ATMO = {
    "随机": ("", ""),
    "晴空": ("晴空", "clear sky"),
    "薄雾": ("薄雾", "thin haze"),
    "浓雾": ("浓雾", "dense fog"),
    "轻雨": ("轻雨", "drizzle"),
    "暴雨": ("暴雨", "heavy rain"),
    "雪": ("雪", "snow"),
    "沙尘": ("沙尘", "dust storm"),
    "极光": ("极光", "aurora backdrop"),
    "日冕": ("日冕", "corona"),
    "高层云": ("高层云", "altostratus"),
    "积雨云": ("积雨云", "cumulonimbus"),
    "层积云": ("层积云", "stratocumulus"),
    "卷云": ("卷云", "cirrus"),
    "卷层云": ("卷层云", "cirrostratus"),
    "积云": ("积云", "cumulus"),
    "层云": ("层云", "stratus"),
    "雨层云": ("雨层云", "nimbostratus"),
    "高积云": ("高积云", "altocumulus"),
    "卷积云": ("卷积云", "cirrocumulus"),
    "晨雾": ("晨雾", "morning mist"),
    "辐射雾": ("辐射雾", "radiation fog"),
    "平流雾": ("平流雾", "advection fog"),
    "蒸发雾": ("蒸发雾", "evaporation fog"),
    "冰雾": ("冰雾", "ice fog"),
    "冻雨": ("冻雨", "freezing rain"),
    "霰": ("霰", "sleet"),
    "冰雹": ("冰雹", "hail"),
    "雷暴": ("雷暴", "thunderstorm"),
    "龙卷风": ("龙卷风", "tornado"),
    "彩虹": ("彩虹", "rainbow"),
    "幻日": ("幻日", "sun dog"),
    "幻月": ("幻月", "moon dog"),
    "宝光": ("宝光", "Brocken spectre"),
    "云海": ("云海", "cloud sea"),
    "平流雾云海": ("平流雾云海", "advection-fog cloud sea"),
    "辐射雾云海": ("辐射雾云海", "radiation-fog cloud sea"),
    "火山烟": ("火山烟", "volcanic smoke"),
    "森林雾": ("森林雾", "forest fog"),
    "城市雾": ("城市雾", "urban fog"),
    "海岸雾": ("海岸雾", "coastal fog"),
    "湖雾": ("湖雾", "lake fog"),
    "河雾": ("河雾", "river fog"),
    "谷雾": ("谷雾", "valley fog"),
    "山帽云": ("山帽云", "lenticular cloud"),
    "旗云": ("旗云", "banner cloud"),
    "对流云": ("对流云", "convective cloud"),
    "层云底": ("层云底", "stratus base"),
    "卷云带": ("卷云带", "cirrus streak"),
}

class WeatherAtmo:
    DESCRIPTION = "🌩️ 天气大气（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"天气": (list(WEATHER_ATMO.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 天气, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 天气 == "随机":
            random.seed(seed)
            天气 = random.choice(list(WEATHER_ATMO.keys())[1:])
        return WEATHER_ATMO[天气]

# ⑥ 温度感受
TEMP_FEEL = {
    "随机": ("", ""),
    "钨丝暖": ("钨丝暖", "tungsten warm"),
    "日光中性": ("日光中性", "daylight neutral"),
    "阴冷": ("阴冷", "overcast cool"),
    "霓虹冷": ("霓虹冷", "neon cold"),
    "篝火极暖": ("篝火极暖", "campfire very warm"),
    "月光极冷": ("月光极冷", "moonlight very cool"),
    "烛火暖": ("烛火暖", "candle warm"),
    "火光橙": ("火光橙", "firelight orange"),
    "黄昏金": ("黄昏金", "golden hour warm"),
    "蓝小时冷": ("蓝小时冷", "blue hour cold"),
    "黎明中性": ("黎明中性", "dawn neutral"),
    "午夜冷蓝": ("午夜冷蓝", "midnight cold blue"),
    "雪地冷青": ("雪地冷青", "snow cold cyan"),
    "沙漠暖黄": ("沙漠暖黄", "desert warm yellow"),
    "海洋冷绿": ("海洋冷绿", "ocean cold green"),
    "森林微冷": ("森林微冷", "forest slightly cool"),
    "城市钠暖": ("城市钠暖", "urban sodium warm"),
    "LED冷白": ("LED冷白", "LED cold white"),
    "卤素暖白": ("卤素暖白", "halogen warm white"),
    "HMI中性": ("HMI中性", "HMI neutral"),
    "荧光冷绿": ("荧光冷绿", "fluorescent cold green"),
    "反拍暖": ("反拍暖", "bounce warm"),
    "云漫冷": ("云漫冷", "cloud diffused cool"),
    "雾漫冷": ("雾漫冷", "fog diffused cool"),
    "霞光暖": ("霞光暖", "afterglow warm"),
    "极光冷绿": ("极光冷绿", "aurora cold green"),
    "火山暖红": ("火山暖红", "volcano warm red"),
    "银幕冷灰": ("银幕冷灰", "screen cold grey"),
    "投影暖": ("投影暖", "projector warm"),
    "激光冷": ("激光冷", "laser cold"),
}

class TempFeel:
    DESCRIPTION = "🌡️ 温度感受（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"温度": (list(TEMP_FEEL.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 温度, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 温度 == "随机":
            random.seed(seed)
            温度 = random.choice(list(TEMP_FEEL.keys())[1:])
        return TEMP_FEEL[温度]

# ⑦ 景深规划
DOF_PLAN = {
    "随机": ("", ""),
    "全景深": ("全景深", "deep focus"),
    "浅景深": ("浅景深", "shallow DOF"),
    "前景模糊": ("前景模糊", "foreground blur"),
    "背景奶油": ("背景奶油虚化", "creamy background bokeh"),
    "双焦 Split": ("双焦 Split-Diopter", "split-diopter dual focus"),
    "超浅景深": ("超浅景深", "ultra-shallow DOF"),
    "极端浅景": ("极端浅景", "extreme shallow DOF"),
    "中景深": ("中景深", "medium DOF"),
    "深景深": ("深景深", "deep DOF"),
    "超深景深": ("超深景深", "ultra-deep DOF"),
    "焦前雾": ("焦前雾", "foreground mist"),
    "焦后雾": ("焦后雾", "background mist"),
    "前焦平面": ("前焦平面", "front focal plane"),
    "后焦平面": ("后焦平面", "back focal plane"),
    "焦平面偏移": ("焦平面偏移", "focal-plane tilt"),
    "移轴景深": ("移轴景深", "tilt-shift DOF"),
    "LensBaby 弯曲景": ("LensBaby 弯曲景深", "LensBaby curved-plane DOF"),
    "圆环景深": ("圆环景深", "donut bokeh DOF"),
    "猫眼景深": ("猫眼景深", "cat-eye bokeh DOF"),
    "泡泡景深": ("泡泡景深", "bubble bokeh DOF"),
    "二线性景深": ("二线性景深", "busy bokeh DOF"),
    "奶油景深": ("奶油景深", "creamy bokeh DOF"),
    "涡旋景深": ("涡旋景深", "swirly bokeh DOF"),
    "鱼鳞景深": ("鱼鳞景深", "fish-scale bokeh DOF"),
    "点焦景深": ("点焦景深", "spot-focus DOF"),
    "线焦景深": ("线焦景深", "line-focus DOF"),
    "面焦景深": ("面焦景深", "plane-focus DOF"),
    "体焦景深": ("体焦景深", "volume-focus DOF"),
    "纳米景深": ("纳米景深", "nano-scale DOF"),
    "微距浅景": ("微距浅景", "macro shallow DOF"),
}

class DOFPlan:
    DESCRIPTION = "🔍 景深规划（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"景深": (list(DOF_PLAN.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 景深, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 景深 == "随机":
            random.seed(seed)
            景深 = random.choice(list(DOF_PLAN.keys())[1:])
        return DOF_PLAN[景深]

# ================================================================================
# 二、视频维度节点（10 个）
# ================================================================================
# ⑻ 镜头运动
CAM_MOTION = {
    "随机": ("", ""),
    "静止锁定": ("静止锁定镜头", "locked-off shot"),
    "推镜": ("推镜", "dolly-in"),
    "拉镜": ("拉镜", "dolly-out"),
    "左移": ("左移镜头", "truck-left"),
    "右移": ("右移镜头", "truck-right"),
    "上升": ("上升镜头", "boom-up"),
    "下降": ("下降镜头", "boom-down"),
    "摇左": ("摇左镜头", "pan-left"),
    "摇右": ("摇右镜头", "pan-right"),
    "摇上": ("摇上镜头", "tilt-up"),
    "摇下": ("摇下镜头", "tilt-down"),
    "甩鞭左": ("甩鞭左摇", "whip-pan-left"),
    "甩鞭右": ("甩鞭右摇", "whip-pan-right"),
    "变焦推拉": ("变焦推拉", "zoom-push-pull"),
    "轨道环绕": ("轨道环绕", "orbital track"),
    "轨道俯仰": ("轨道俯仰", "track-tilt-combo"),
    "轨道螺旋": ("轨道螺旋", "helical track"),
    "手持微抖": ("手持微抖", "handheld micro-shake"),
    "斯坦尼跟随": ("斯坦尼跟随", "steadicam follow"),
    "自由落体": ("自由落体镜头", "free-fall camera"),
    "无人机俯冲": ("无人机俯冲", "drone dive"),
    "无人机拉升": ("无人机拉升", "drone rise"),
    "无人机侧飞": ("无人机侧飞", "drone side-flight"),
    "无人机环绕上升": ("无人机环绕上升", "drone orbit-rise"),
    "无人机环绕下降": ("无人机环绕下降", "drone orbit-descend"),
    "车载前推": ("车载前推", "car-mount push"),
    "车载后拉": ("车载后拉", "car-mount pull"),
    "车载侧跟": ("车载侧跟", "car-mount side-track"),
    "摇臂上升+前推": ("摇臂上升+前推", "crane-up + dolly-in"),
    "摇臂下降+后拉": ("摇臂下降+后拉", "crane-down + dolly-out"),
    "滑轨侧移+推镜": ("滑轨侧移+推镜", "slider-side + dolly-in"),
    "滑轨斜移": ("滑轨斜移", "slider-diagonal"),
    "滑轨弧形": ("滑轨弧形", "slider-arc"),
    "滑轨旋转": ("滑轨旋转", "slider-rotate"),
    "滑轨俯仰": ("滑轨俯仰", "slider-tilt"),
    "滑轨螺旋": ("滑轨螺旋", "slider-helical"),
    "滑轨甩鞭": ("滑轨甩鞭", "slider-whip-pan"),
    "滑轨变焦": ("滑轨变焦", "slider-zoom"),
    "滑轨自由落体": ("滑轨自由落体", "slider-free-fall"),
    "滑轨斯坦尼": ("滑轨斯坦尼", "slider-steadicam"),
    "滑轨手持": ("滑轨手持", "slider-handheld"),
    "螺旋上升": ("螺旋上升镜头", "helical-up"),
    "螺旋下降": ("螺旋下降镜头", "helical-down"),
    "螺旋侧移": ("螺旋侧移", "helical-side"),
    "螺旋甩鞭": ("螺旋甩鞭", "helical-whip"),
    "螺旋变焦": ("螺旋变焦", "helical-zoom"),
    "螺旋自由落体": ("螺旋自由落体", "helical-free-fall"),
    "螺旋斯坦尼": ("螺旋斯坦尼", "helical-steadicam"),
    "螺旋手持": ("螺旋手持", "helical-handheld"),
    "螺旋轨道": ("螺旋轨道", "helical-track"),
    "螺旋无人机": ("螺旋无人机", "helical-drone"),
    "螺旋车载": ("螺旋车载", "helical-car-mount"),
    "螺旋摇臂": ("螺旋摇臂", "helical-crane"),
    "螺旋滑轨": ("螺旋滑轨", "helical-slider"),
    "螺旋复合": ("螺旋复合运动", "helical-combo"),
}

class CameraMotion:
    DESCRIPTION = "📹 镜头运动（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"镜头运动": (list(CAM_MOTION.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 镜头运动, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 镜头运动 == "随机":
            random.seed(seed)
            镜头运动 = random.choice(list(CAM_MOTION.keys())[1:])
        return CAM_MOTION[镜头运动]

# ⑼ 运动速度
MOTION_SPEED = {
    "随机": ("", ""),
    "凝固": ("速度 0% 凝固", "speed 0% freeze"),
    "极慢": ("速度 10% 极慢", "speed 10% ultra-slow"),
    "慢动作": ("速度 25% 慢动作", "speed 25% slow motion"),
    "常速": ("速度 100% 常速", "speed 100% real-time"),
    "稍快": ("速度 150% 稍快", "speed 150% quick"),
    "快速": ("速度 200% 快速", "speed 200% fast"),
    "急速": ("速度 400% 急速", "speed 400% rapid"),
    "光速": ("速度 1000% 光速", "speed 1000% light-speed"),
    "时间冻结": ("时间冻结帧", "frame-freeze"),
    "时间切片": ("时间切片", "time-slice"),
    "倒放": ("倒放", "reverse playback"),
    "频闪 4fps": ("频闪 4fps", "strobe 4 fps"),
    "跳剪 6fps": ("跳剪 6fps", "jump-cut 6 fps"),
    "抽帧 12fps": ("抽帧 12fps", "frame-drop 12 fps"),
    "光流补帧": ("光流补帧", "optical-flow interpolation"),
    "矢量帧混合": ("矢量帧混合", "vector-frame blend"),
    "神经慢动作": ("神经慢动作", "AI-slomo"),
    "阶梯加速": ("阶梯加速", "step-ramp speed-up"),
    "阶梯减速": ("阶梯减速", "step-ramp slow-down"),
    "指数加速": ("指数加速", "exponential speed-up"),
    "指数减速": ("指数减速", "exponential slow-down"),
    "bounce 回弹": ("bounce 回弹变速", "bounce speed ramp"),
    "elastic 弹性": ("elastic 弹性变速", "elastic speed ramp"),
    "overshoot 过冲": ("overshoot 过冲变速", "overshoot speed ramp"),
    "back 回退": ("back 回退变速", "back speed ramp"),
    "circ 圆弧": ("circ 圆弧变速", "circular ease speed ramp"),
    "quint 五次": ("quint 五次变速", "quintic ease speed ramp"),
    "AI 语义变速": ("AI 语义变速", "AI semantic speed ramp"),
    "对象感知变速": ("对象感知变速", "object-aware speed ramp"),
    "音频 BPM 变速": ("音频 BPM 变速", "audio BPM speed ramp"),
    "字幕驱动变速": ("字幕驱动变速", "subtitle-driven speed ramp"),
    "深度感知变速": ("深度感知变速", "depth-aware speed ramp"),
    "情感驱动变速": ("情感驱动变速", "emotion-driven speed ramp"),
    "跟踪点变速": ("跟踪点变速", "tracking-point speed ramp"),
    "光流变速": ("光流变速", "optical-flow speed ramp"),
    "语义遮罩变速": ("语义遮罩变速", "semantic-mask speed ramp"),
    "风格化变速": ("风格化变速", "stylized speed ramp"),
    "随机阶梯变速": ("随机阶梯变速", "random step speed ramp"),
    "噪波变速": ("噪波变速", "noise-driven speed ramp"),
    "正弦变速": ("正弦变速", "sine-wave speed ramp"),
    "三角变速": ("三角变速", "triangle-wave speed ramp"),
    "方波变速": ("方波变速", "square-wave speed ramp"),
    "锯齿变速": ("锯齿变速", "sawtooth-wave speed ramp"),
    "脉冲变速": ("脉冲变速", "pulse speed ramp"),
    "线性反弹变速": ("线性反弹变速", "linear bounce speed ramp"),
    "指数反弹变速": ("指数反弹变速", "exponential bounce speed ramp"),
    "弹性振荡变速": ("弹性振荡变速", "elastic oscillation speed ramp"),
    "过冲回弹变速": ("过冲回弹变速", "overshoot bounce speed ramp"),
    "AI 智能平滑变速": ("AI 智能平滑变速", "AI smart smooth speed ramp"),
    "AI 智能阶梯变速": ("AI 智能阶梯变速", "AI smart step speed ramp"),
}

class MotionSpeed:
    DESCRIPTION = "⏩ 运动速度（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"速度": (list(MOTION_SPEED.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 速度, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 速度 == "随机":
            random.seed(seed)
            速度 = random.choice(list(MOTION_SPEED.keys())[1:])
        return MOTION_SPEED[速度]

# ⑽ 转场语义
TRANS_SEM = {
    "随机": ("", ""),
    "硬切": ("硬切转场", "hard cut"),
    "淡入淡出": ("淡入淡出", "fade in-out"),
    "交叉溶解": ("交叉溶解", "cross dissolve"),
    "闪白": ("闪白转场", "flash-white"),
    "闪黑": ("闪黑转场", "flash-black"),
    "擦除左→右": ("擦除左→右", "wipe left-to-right"),
    "擦除右←左": ("擦除右←左", "wipe right-to-left"),
    "擦除上↓下": ("擦除上↓下", "wipe top-to-bottom"),
    "擦除下↑上": ("擦除下↑上", "wipe bottom-to-top"),
    "圆形展开": ("圆形展开", "iris open"),
    "圆形收缩": ("圆形收缩", "iris close"),
    "百叶窗横": ("百叶窗横", "horizontal blinds"),
    "百叶窗竖": ("百叶窗竖", "vertical blinds"),
    "像素排序": ("像素排序转场", "pixel-sort transition"),
    "故障撕裂": ("故障撕裂转场", "glitch tear transition"),
    "抖动闪白": ("抖动闪白", "shake flash-white"),
    "透镜畸变": ("透镜畸变转场", "lens distortion transition"),
    "变焦模糊": ("变焦模糊转场", "zoom-blur transition"),
    "旋转模糊": ("旋转模糊转场", "spin-blur transition"),
    "缩放旋转": ("缩放旋转", "zoom-spin"),
    "滑动左→右": ("滑动左→右", "slide left-to-right"),
    "滑动右←左": ("滑动右←左", "slide right-to-left"),
    "滑动上↓下": ("滑动上↓下", "slide top-to-bottom"),
    "滑动下↑上": ("滑动下↑上", "slide bottom-to-top"),
    "立方体左→右": ("立方体左→右", "cube left-to-right"),
    "立方体右←左": ("立方体右←左", "cube right-to-left"),
    "立方体上↓下": ("立方体上↓下", "cube top-to-bottom"),
    "立方体下↑上": ("立方体下↑上", "cube bottom-to-top"),
    "翻页左→右": ("翻页左→右", "page-turn left-to-right"),
    "翻页右←左": ("翻页右←左", "page-turn right-to-left"),
    "全息闪烁": ("全息闪烁转场", "hologram flicker transition"),
    "数据块切换": ("数据块切换", "data-block switch"),
    "水墨晕染": ("水墨晕染转场", "ink-wash dissolve"),
    "火焰燃烧": ("火焰燃烧转场", "flame burn transition"),
    "雪花覆盖": ("雪花覆盖转场", "snowflake cover"),
    "叶子飞散": ("叶子飞散转场", "leaf scatter"),
    "纸张撕裂": ("纸张撕裂转场", "paper tear"),
    "镜头光晕转场": ("镜头光晕转场", "lens-flare transition"),
    "色差分离转场": ("色差分离转场", "chromatic-aberration split"),
    "像素化转场": ("像素化转场", "pixelate transition"),
    "矢量形状转场": ("矢量形状转场", "vector-shape transition"),
    "AI 语义融合": ("AI 语义融合", "AI semantic blend"),
    "摩尔波纹": ("摩尔波纹转场", "moiré wave transition"),
    "波纹变形": ("波纹变形转场", "ripple warp"),
    "闪帧跳切": ("闪帧跳切", "flash-frame jump"),
    "动态模糊溶解": ("动态模糊溶解", "motion-blur dissolve"),
    "光流变形": ("光流变形转场", "optical-flow warp"),
    "深度图融合": ("深度图融合", "depth-map blend"),
    "语义遮罩切换": ("语义遮罩切换", "semantic-mask cut"),
    "风格化涂抹": ("风格化涂抹", "stylized smear"),
    "液体流动": ("液体流动转场", "liquid flow"),
    "烟雾消散": ("烟雾消散转场", "smoke dissipate"),
    "灰尘扬起": ("灰尘扬起转场", "dust blow"),
    "玻璃碎裂": ("玻璃碎裂转场", "glass shatter"),
    "镜头晃动闪黑": ("镜头晃动闪黑", "shake flash-black"),
    "RGB 分离闪": ("RGB 分离闪", "RGB split flash"),
    "跟踪点切换": ("跟踪点切换", "tracking-point cut"),
    "时间码跳切": ("时间码跳切", "timecode jump"),
    "字幕驱动切换": ("字幕驱动切换", "subtitle-driven cut"),
}

class TransSemantic:
    DESCRIPTION = "🔄 转场语义（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"转场": (list(TRANS_SEM.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 转场, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 转场 == "随机":
            random.seed(seed)
            转场 = random.choice(list(TRANS_SEM.keys())[1:])
        return TRANS_SEM[转场]

# ⑾ 帧率快门
FPS_SHUTTER = {
    "随机": ("", ""),
    "6 fps 卡通": ("6 fps 卡通感", "6 fps cartoon feel"),
    "12 fps 抽帧": ("12 fps 抽帧", "12 fps frame-drop"),
    "15 fps 早期胶片": ("15 fps 早期胶片", "15 fps early film"),
    "24 fps 电影": ("24 fps 电影标准", "24 fps cinematic standard"),
    "25 fps PAL": ("25 fps PAL 制式", "25 fps PAL broadcast"),
    "30 fps NTSC": ("30 fps NTSC 制式", "30 fps NTSC broadcast"),
    "48 fps 高帧": ("48 fps 高帧", "48 fps high-frame"),
    "50 fps PAL 高帧": ("50 fps PAL 高帧", "50 fps PAL high-frame"),
    "60 fps 流体": ("60 fps 流体", "60 fps fluid"),
    "90 fps 超流体": ("90 fps 超流体", "90 fps super-fluid"),
    "120 fps 慢动作": ("120 fps 慢动作", "120 fps slow-motion"),
    "240 fps 极慢": ("240 fps 极慢", "240 fps ultra-slow"),
    "480 fps 超级慢": ("480 fps 超级慢", "480 fps super-slow"),
    "1000 fps 科研慢": ("1000 fps 科研级慢动作", "1000 fps scientific slow-motion"),
    "180° 标准快门": ("180° 标准快门", "180° standard shutter"),
    "90° 清晰快门": ("90° 清晰快门", "90° crisp shutter"),
    "45° 极清晰快门": ("45° 极清晰快门", "45° ultra-crisp shutter"),
    "270° 运动模糊": ("270° 运动模糊", "270° motion-blur shutter"),
    "360° 极致模糊": ("360° 极致模糊", "360° extreme-blur shutter"),
    "1/50 s 标准": ("1/50 s 标准", "1/50 s standard"),
    "1/100 s 清晰": ("1/100 s 清晰", "1/100 s crisp"),
    "1/250 s 极清晰": ("1/250 s 极清晰", "1/250 s ultra-crisp"),
    "1/24 s 电影模糊": ("1/24 s 电影模糊", "1/24 s cinematic blur"),
    "1/12 s 极致模糊": ("1/12 s 极致模糊", "1/12 s extreme blur"),
    "自适应快门": ("自适应快门", "adaptive shutter angle"),
    "动态模糊增强": ("动态模糊增强", "motion-blur enhanced"),
    "清晰帧优先": ("清晰帧优先", "crisp-frame priority"),
    "AI 光流快门": ("AI 光流快门", "AI optical-flow shutter"),
    "卷帘快门模拟": ("卷帘快门模拟", "rolling-shutter simulation"),
    "全局快门模拟": ("全局快门模拟", "global-shutter simulation"),
    "高速电子快门": ("高速电子快门", "high-speed electronic shutter"),
    "低光慢快门": ("低光慢快门", "low-light slow shutter"),
    "日光快快门": ("日光快快门", "daylight fast shutter"),
    "夜景超慢快门": ("夜景超慢快门", "night ultra-slow shutter"),
    "闪光同步快门": ("闪光同步快门", "flash-sync shutter"),
}

class FpsShuttle:
    DESCRIPTION = "🎞️ 帧率 & 快门角度（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"帧率快门": (list(FPS_SHUTTER.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 帧率快门, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 帧率快门 == "随机":
            random.seed(seed)
            帧率快门 = random.choice(list(FPS_SHUTTER.keys())[1:])
        return FPS_SHUTTER[帧率快门]

# ⑿ 运动模糊类型
MOTION_BLUR = {
    "随机": ("", ""),
    "方向模糊": ("方向运动模糊", "directional motion blur"),
    "旋转模糊": ("旋转运动模糊", "rotational motion blur"),
    "缩放模糊": ("缩放运动模糊", "zoom motion blur"),
    "轨道模糊": ("轨道运动模糊", "orbital motion blur"),
    "手持抖动模糊": ("手持抖动模糊", "handheld shake blur"),
    "镜头位移模糊": ("镜头位移模糊", "lens-shift motion blur"),
    "变焦爆发模糊": ("变焦爆发模糊", "zoom-burst blur"),
    "螺旋模糊": ("螺旋运动模糊", "helical motion blur"),
    "随机向量模糊": ("随机向量模糊", "random-vector motion blur"),
    "AI 光流模糊": ("AI 光流模糊", "AI optical-flow blur"),
    "高速方向模糊": ("高速方向模糊", "high-speed directional blur"),
    "低速旋转模糊": ("低速旋转模糊", "low-speed rotational blur"),
    "径向缩放模糊": ("径向缩放模糊", "radial zoom blur"),
    "离心旋转模糊": ("离心旋转模糊", "centrifugal spin blur"),
    "向心旋转模糊": ("向心旋转模糊", "centripetal spin blur"),
    "抛物线轨迹模糊": ("抛物线轨迹模糊", "parabolic trail blur"),
    "自由落体模糊": ("自由落体模糊", "free-fall motion blur"),
    "弹射加速模糊": ("弹射加速模糊", "catapult acceleration blur"),
    "急停模糊": ("急停模糊", "emergency-stop blur"),
    "反弹回弹模糊": ("反弹回弹模糊", "bounce-back blur"),
    "过冲模糊": ("过冲模糊", "overshoot blur"),
    "弹性振荡模糊": ("弹性振荡模糊", "elastic oscillation blur"),
    "阶梯变速模糊": ("阶梯变速模糊", "step-ramp blur"),
    "指数变速模糊": ("指数变速模糊", "exponential ramp blur"),
    "线性加速模糊": ("线性加速模糊", "linear acceleration blur"),
    "线性减速模糊": ("线性减速模糊", "linear deceleration blur"),
    "缓入模糊": ("缓入模糊", "ease-in blur"),
    "缓出模糊": ("缓出模糊", "ease-out blur"),
    "缓入缓出模糊": ("缓入缓出模糊", "ease-in-out blur"),
    "Bounce 模糊": ("Bounce 模糊", "bounce blur"),
    "Elastic 模糊": ("Elastic 模糊", "elastic blur"),
    "Back 模糊": ("Back 模糊", "back blur"),
    "Circ 模糊": ("Circ 模糊", "circular ease blur"),
    "Quint 模糊": ("Quint 模糊", "quintic ease blur"),
}

class MotionBlur:
    DESCRIPTION = "💨 运动模糊类型（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"模糊类型": (list(MOTION_BLUR.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 模糊类型, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 模糊类型 == "随机":
            random.seed(seed)
            模糊类型 = random.choice(list(MOTION_BLUR.keys())[1:])
        return MOTION_BLUR[模糊类型]

# ⒀ 镜头呼吸
LENS_BREATH = {
    "随机": ("", ""),
    "无呼吸": ("无呼吸锁定", "no breathing locked"),
    "轻微呼吸": ("轻微呼吸（电影定焦）", "slight breathing cine-prime"),
    "明显呼吸": ("明显呼吸（相机镜头）", "obvious breathing photo-lens"),
    "大幅呼吸": ("大幅呼吸（变形宽银幕）", "heavy breathing anamorphic"),
    "呼吸+焦点移位": ("呼吸+焦点移位", "breathing + rack-focus"),
    "变形宽银幕呼吸": ("变形宽银幕呼吸", "anamorphic breathing"),
    "球面镜头呼吸": ("球面镜头呼吸", "spherical lens breathing"),
    "长焦微呼吸": ("长焦微呼吸", "telephoto micro-breathing"),
    "广角明显呼吸": ("广角明显呼吸", "wide-angle obvious breathing"),
    "微距放大呼吸": ("微距放大呼吸", "macro magnification breathing"),
    "变焦呼吸": ("变焦呼吸", "zoom breathing"),
    "定焦无呼吸": ("定焦无呼吸", "prime no breathing"),
    "电影变焦呼吸": ("电影变焦呼吸", "cine-zoom breathing"),
    "相机变焦呼吸": ("相机变焦呼吸", "photo-zoom breathing"),
    "电动变焦呼吸": ("电动变焦呼吸", "motor-zoom breathing"),
    "手动变焦呼吸": ("手动变焦呼吸", "manual-zoom breathing"),
    "Parfocal 无呼吸": ("Parfocal 无呼吸", "Parfocal no breathing"),
    "Varifocal 明显呼吸": ("Varifocal 明显呼吸", "Varifocal obvious breathing"),
    "Isco 变形呼吸": ("Isco 变形呼吸", "Isco anamorphic breathing"),
    "Cooke 轻微呼吸": ("Cooke 轻微呼吸", "Cooke slight breathing"),
    "Zeiss 微呼吸": ("Zeiss 微呼吸", "Zeiss micro-breathing"),
    "Sigma 明显呼吸": ("Sigma 明显呼吸", "Sigma obvious breathing"),
    "Sony 电动呼吸": ("Sony 电动呼吸", "Sony motor breathing"),
    "Canon 自然呼吸": ("Canon 自然呼吸", "Canon natural breathing"),
}

class LensBreathing:
    DESCRIPTION = "👃 镜头呼吸（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"镜头呼吸": (list(LENS_BREATH.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 镜头呼吸, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 镜头呼吸 == "随机":
            random.seed(seed)
            镜头呼吸 = random.choice(list(LENS_BREATH.keys())[1:])
        return LENS_BREATH[镜头呼吸]

# ⒁ 稳定模式
STAB_MODE = {
    "随机": ("", ""),
    "锁定三脚架": ("锁定三脚架", "locked-off tripod"),
    "滑轨匀速": ("滑轨匀速", "slider constant"),
    "斯坦尼": ("斯坦尼稳定", "steadicam glide"),
    "手持微抖": ("手持微抖", "handheld micro-shake"),
    "电子增稳 EIS": ("电子增稳 EIS", "electronic image stabilization EIS"),
    "机械云台": ("机械云台", "mechanical gimbal"),
    "自由落体": ("自由落体", "free-fall"),
    "车载减震": ("车载减震", "car-mount shock absorption"),
    "无人机三轴": ("无人机三轴", "drone 3-axis gimbal"),
    "无人机 FPV": ("无人机 FPV", "drone FPV"),
    "无人机 cinematic": ("无人机 cinematic", "drone cinematic"),
    "机内 IBIS": ("机内 IBIS", "in-body IBIS"),
    "AI 后期稳定": ("AI 后期稳定", "AI post-stabilization"),
    "光学陀螺稳定": ("光学陀螺稳定", "optical gyro stabilization"),
    "车载斯坦尼": ("车载斯坦尼", "car-mount steadicam"),
    "车载手持": ("车载手持", "car-mount handheld"),
    "车载锁定": ("车载锁定", "car-mount locked"),
    "船载减震": ("船载减震", "boat-mount stabilization"),
    "机载云台": ("机载云台", "aircraft gimbal"),
    "肩扛斯坦尼": ("肩扛斯坦尼", "shoulder steadicam"),
    "胸挂斯坦尼": ("胸挂斯坦尼", "chest steadicam"),
    "腰挂斯坦尼": ("腰挂斯坦尼", "waist steadicam"),
    "SnorriCam 胸挂": ("SnorriCam 胸挂", "SnorriCam chest-mount"),
    "头盔云台": ("头盔云台", "helmet gimbal"),
    "背包云台": ("背包云台", "backpack gimbal"),
    "绳索悬挂云台": ("绳索悬挂云台", "rope-suspension gimbal"),
    "滑索云台": ("滑索云台", "zip-line gimbal"),
    "摇臂稳定": ("摇臂稳定", "crane stabilized"),
    "轨道斯坦尼": ("轨道斯坦尼", "track steadicam"),
    "轨道手持": ("轨道手持", "track handheld"),
    "轨道锁定": ("轨道锁定", "track locked"),
    "伸缩炮稳定": ("伸缩炮稳定", "telescopic crane stable"),
    "陀螺仪稳定": ("陀螺仪稳定", "gyro-stabilized"),
    "机械陀螺稳定": ("机械陀螺稳定", "mechanical gyro stable"),
    "电子陀螺稳定": ("电子陀螺稳定", "electronic gyro stable"),
    "光纤陀螺稳定": ("光纤陀螺稳定", "fiber-optic gyro stable"),
    "微机电陀螺稳定": ("微机电陀螺稳定", "MEMS gyro stable"),
}

class StabMode:
    DESCRIPTION = "🛠️ 稳定模式（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"稳定模式": (list(STAB_MODE.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 稳定模式, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 稳定模式 == "随机":
            random.seed(seed)
            稳定模式 = random.choice(list(STAB_MODE.keys())[1:])
        return STAB_MODE[稳定模式]

# ⒂ 景深动画
DOF_ANI = {
    "随机": ("", ""),
    "固定景深": ("固定景深", "locked DOF"),
    "推镜浅→深": ("推镜浅→深", "dolly-in shallow to deep"),
    "拉镜深→浅": ("拉镜深→浅", "dolly-out deep to shallow"),
    "焦点前→后": ("焦点前→后", "focus front to back"),
    "焦点后→前": ("焦点后→前", "focus back to front"),
    "双焦切换 Split": ("双焦切换 Split-Diopter", "split-diopter swap"),
    "移轴扫焦": ("移轴扫焦", "tilt-shift focus sweep"),
    "呼吸焦移位": ("呼吸焦移位", "breathing focus shift"),
    "宏微拉焦": ("宏微拉焦", "macro rack focus"),
    "无限远→最近": ("无限远→最近", "infinity to closest"),
    "最近→无限远": ("最近→无限远", "closest to infinity"),
    "循环拉焦": ("循环拉焦", "pump rack focus"),
    "超浅景深动画": ("超浅景深动画", "ultra-shallow DOF animation"),
    "深景深动画": ("深景深动画", "deep DOF animation"),
    "前景雾扫焦": ("前景雾扫焦", "foreground mist focus sweep"),
    "背景雾扫焦": ("背景雾扫焦", "background mist focus sweep"),
    "点焦追踪": ("点焦追踪", "spot-focus tracking"),
    "线焦扫描": ("线焦扫描", "line-focus scan"),
    "面焦推移": ("面焦推移", "plane-focus push"),
    "体焦漫游": ("体焦漫游", "volume-focus roam"),
    "纳米级拉焦": ("纳米级拉焦", "nano-scale rack"),
    "微距浅景动画": ("微距浅景动画", "macro shallow DOF animation"),
    "猫眼拉焦": ("猫眼拉焦", "cat-eye rack focus"),
    "圆环拉焦": ("圆环拉焦", "donut bokeh rack"),
    "涡旋拉焦": ("涡旋拉焦", "swirly bokeh rack"),
    "奶油拉焦": ("奶油拉焦", "creamy bokeh rack"),
    "二线性拉焦": ("二线性拉焦", "busy bokeh rack"),
    "鱼鳞拉焦": ("鱼鳞拉焦", "fish-scale bokeh rack"),
    "泡泡拉焦": ("泡泡拉焦", "bubble bokeh rack"),
    "LensBaby 弯曲拉焦": ("LensBaby 弯曲拉焦", "LensBaby curved rack"),
    "移轴循环拉焦": ("移轴循环拉焦", "tilt-shift loop rack"),
    "AI 语义自动拉焦": ("AI 语义自动拉焦", "AI semantic auto rack"),
}

class DOFAnimation:
    DESCRIPTION = "🔍 景深动画（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"景深动画": (list(DOF_ANI.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 景深动画, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 景深动画 == "随机":
            random.seed(seed)
            景深动画 = random.choice(list(DOF_ANI.keys())[1:])
        return DOF_ANI[景深动画]

# ⒃ 速度曲线
SPEED_CURVE = {
    "随机": ("", ""),
    "线性加速": ("线性加速", "linear speed-up"),
    "线性减速": ("线性减速", "linear slow-down"),
    "缓入加速": ("缓入加速", "ease-in speed-up"),
    "缓出减速": ("缓出减速", "ease-out slow-down"),
    "缓入缓出": ("缓入缓出", "ease-in-out"),
    "阶梯加速": ("阶梯加速", "step-ramp speed-up"),
    "阶梯减速": ("阶梯减速", "step-ramp slow-down"),
    "指数加速": ("指数加速", "exponential speed-up"),
    "指数减速": ("指数减速", "exponential slow-down"),
    "bounce 回弹": ("bounce 回弹变速", "bounce speed ramp"),
    "elastic 弹性": ("elastic 弹性变速", "elastic speed ramp"),
    "overshoot 过冲": ("overshoot 过冲变速", "overshoot speed ramp"),
    "back 回退": ("back 回退变速", "back speed ramp"),
    "circ 圆弧": ("circ 圆弧变速", "circular ease speed ramp"),
    "quint 五次": ("quint 五次变速", "quintic ease speed ramp"),
    "AI 语义变速": ("AI 语义变速", "AI semantic speed ramp"),
    "对象感知变速": ("对象感知变速", "object-aware speed ramp"),
    "音频 BPM 变速": ("音频 BPM 变速", "audio BPM speed ramp"),
    "字幕驱动变速": ("字幕驱动变速", "subtitle-driven speed ramp"),
    "深度感知变速": ("深度感知变速", "depth-aware speed ramp"),
    "情感驱动变速": ("情感驱动变速", "emotion-driven speed ramp"),
    "跟踪点变速": ("跟踪点变速", "tracking-point speed ramp"),
    "光流变速": ("光流变速", "optical-flow speed ramp"),
    "语义遮罩变速": ("语义遮罩变速", "semantic-mask speed ramp"),
    "风格化变速": ("风格化变速", "stylized speed ramp"),
    "随机阶梯变速": ("随机阶梯变速", "random step speed ramp"),
    "噪波变速": ("噪波变速", "noise-driven speed ramp"),
    "正弦变速": ("正弦变速", "sine-wave speed ramp"),
    "三角变速": ("三角变速", "triangle-wave speed ramp"),
    "方波变速": ("方波变速", "square-wave speed ramp"),
    "锯齿变速": ("锯齿变速", "sawtooth-wave speed ramp"),
    "脉冲变速": ("脉冲变速", "pulse speed ramp"),
    "线性反弹变速": ("线性反弹变速", "linear bounce speed ramp"),
    "指数反弹变速": ("指数反弹变速", "exponential bounce speed ramp"),
    "弹性振荡变速": ("弹性振荡变速", "elastic oscillation speed ramp"),
    "过冲回弹变速": ("过冲回弹变速", "overshoot bounce speed ramp"),
    "AI 智能平滑变速": ("AI 智能平滑变速", "AI smart smooth speed ramp"),
    "AI 智能阶梯变速": ("AI 智能阶梯变速", "AI smart step speed ramp"),
}

class SpeedCurve:
    DESCRIPTION = "〰️ 速度曲线（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"速度曲线": (list(SPEED_CURVE.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 速度曲线, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 速度曲线 == "随机":
            random.seed(seed)
            速度曲线 = random.choice(list(SPEED_CURVE.keys())[1:])
        return SPEED_CURVE[速度曲线]

# ⒄ AI 语义运镜
AI_CAM_MOVE = {
    "随机": ("", ""),
    "对象锁定环绕": ("对象锁定环绕", "object-lock orbit"),
    "对象锁定跟随": ("对象锁定跟随", "object-lock follow"),
    "人脸追踪推拉": ("人脸追踪推拉", "face-tracking push-pull"),
    "眼球追踪摇镜": ("眼球追踪摇镜", "eye-tracking pan"),
    "手势追踪升降": ("手势追踪升降", "gesture-tracking boom"),
    "语音驱动推拉": ("语音驱动推拉", "voice-driven push-pull"),
    "音乐 BPM 自动推拉": ("音乐 BPM 自动推拉", "music BPM auto push-pull"),
    "字幕驱动切换": ("字幕驱动切换", "subtitle-driven cut"),
    "深度图自动轨道": ("深度图自动轨道", "depth-map auto orbit"),
    "光流自动避障": ("光流自动避障", "optical-flow auto avoid"),
    "语义分割自动对焦": ("语义分割自动对焦", "semantic-segmentation auto focus"),
    "情感驱动速度": ("情感驱动速度", "emotion-driven speed"),
    "对象感知变速": ("对象感知变速", "object-aware speed ramp"),
    "深度感知变速": ("深度感知变速", "depth-aware speed ramp"),
    "语义遮罩运镜": ("语义遮罩运镜", "semantic-mask camera move"),
    "AI 智能跟随": ("AI 智能跟随", "AI smart follow"),
    "AI 智能环绕": ("AI 智能环绕", "AI smart orbit"),
    "AI 智能推拉": ("AI 智能推拉", "AI smart push-pull"),
    "AI 智能摇移": ("AI 智能摇移", "AI smart pan-tilt"),
    "AI 智能升降": ("AI 智能升降", "AI smart boom"),
    "AI 智能变焦": ("AI 智能变焦", "AI smart zoom"),
    "AI 智能聚焦": ("AI 智能聚焦", "AI smart focus"),
    "AI 智能拉焦": ("AI 智能拉焦", "AI smart rack-focus"),
    "AI 智能景深": ("AI 智能景深", "AI smart DOF"),
    "AI 智能稳定": ("AI 智能稳定", "AI smart stabilization"),
    "AI 智能去抖": ("AI 智能去抖", "AI smart de-shake"),
    "AI 智能裁剪": ("AI 智能裁剪", "AI smart crop"),
    "AI 智能缩放": ("AI 智能缩放", "AI smart scale"),
    "AI 智能旋转": ("AI 智能旋转", "AI smart rotate"),
    "AI 智能翻转": ("AI 智能翻转", "AI smart flip"),
    "AI 智能变速": ("AI 智能变速", "AI smart speed ramp"),
    "AI 智能转场": ("AI 智能转场", "AI smart transition"),
    "AI 智能遮罩": ("AI 智能遮罩", "AI smart mask"),
    "AI 智能抠像": ("AI 智能抠像", "AI smart keying"),
    "AI 智能修复": ("AI 智能修复", "AI smart inpaint"),
    "AI 智能超分": ("AI 智能超分", "AI smart super-res"),
    "AI 智能插帧": ("AI 智能插帧", "AI smart frame-interpolation"),
    "AI 智能去噪": ("AI 智能去噪", "AI smart denoise"),
    "AI 智能去模糊": ("AI 智能去模糊", "AI smart deblur"),
    "AI 智能 HDR": ("AI 智能 HDR", "AI smart HDR"),
    "AI 智能色彩匹配": ("AI 智能色彩匹配", "AI smart color match"),
    "AI 智能风格迁移": ("AI 智能风格迁移", "AI smart style transfer"),
    "AI 智能景深预测": ("AI 智能景深预测", "AI smart depth prediction"),
    "AI 智能光流估计": ("AI 智能光流估计", "AI smart optical-flow estimation"),
}

class AISemanticCam:
    DESCRIPTION = "🧠 AI 语义运镜（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"ai_cam": (list(AI_CAM_MOVE.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, ai_cam, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if ai_cam == "随机":
            random.seed(seed)
            ai_cam = random.choice(list(AI_CAM_MOVE.keys())[1:])
        return AI_CAM_MOVE[ai_cam]

# ================================================================================
# 三、图片 & 视频 最佳组合预置（2 个节点）
# ================================================================================
# ⒅ 图片组合
IMG_COMBO = {
    "随机": ("", ""),
    "黄金人像大师": (
        "从斜侧3/4视角拍摄，Kodak Portra 400 胶片滤镜，45°侧前主光，柔光箱柔光，晴空，黄昏金暖，浅景深奶油虚化",
        "shot from a three-quarter angle, Kodak Portra 400 film filter, 45° key light from front-side, softbox soft light, clear sky, golden hour warm, shallow DOF creamy bokeh"
    ),
    "蓝调城市赛博": (
        "从鸟瞰视角拍摄，Teal-Orange 大片LUT，霓虹侧光，阴云漫射，蓝小时冷调，深景深",
        "bird’s-eye angle, teal-orange blockbuster LUT, neon side light, overcast diffused, blue hour cold, deep focus"
    ),
    "烛光晚餐情绪": (
        "从过肩视角拍摄，烛光暖调滤镜，烛光底光，窗帘柔光，薄雾，钨丝暖，超浅景深",
        "over-shoulder angle, candle-warm filter, candle under light, curtain-softened light, thin haze, tungsten warm, ultra-shallow DOF"
    ),
    "晨光森林童话": (
        "从低角度仰光视角拍摄，Fuji Pro 400H 胶片滤镜，侧前顶光，树叶斑驳，晨雾，黎明中性，中景深",
        "low-angle uplight angle, Fuji Pro 400H film filter, front-side top light, leaf-dappled, morning mist, dawn neutral, medium DOF"
    ),
    "工业硬调黑白": (
        "从正面视角拍摄，高反差黑白滤镜，菲涅耳硬光，点光源硬光，高层云，零饱和，全景深",
        "front angle, high-contrast monochrome filter, Fresnel hard light, point-source hard, altostratus, zero saturation, deep focus"
    ),
    "霓虹雨夜孤独": (
        "从车窗侧视角拍摄，霓虹冷调滤镜，霓虹侧光，水纹投影，暴雨，霓虹冷，背景奶油虚化",
        "car-window-side angle, neon-cold filter, neon side light, water-pattern projection, heavy rain, neon cold, creamy background bokeh"
    ),
    "镜面对称艺术": (
        "从镜面反射视角拍摄，S曲线对比增强滤镜，正前顶光，镜面反射，晴空，日光中性，对称空镜景深",
        "mirror-reflection angle, S-curve contrast filter, front-top light, mirror reflection, clear sky, daylight neutral, symmetrical empty-frame DOF"
    ),
    "沙漠热浪孤独": (
        "从望远镜视角拍摄，复古褪色滤镜，云幕柔光，沙尘，沙漠暖黄，深景深",
        "telescopic angle, vintage fade filter, cloud-dome soft light, dust storm, desert warm yellow, deep focus"
    ),
    "森林迷雾神秘": (
        "从拱廊框景视角拍摄，低饱和滤镜，云漫射顶光，森林雾，森林微冷，前景雾扫焦",
        "archway-framing angle, low-saturation filter, cloud-diffused top light, forest fog, forest slightly cool, foreground mist focus sweep"
    ),
    "城市钠灯夜骑": (
        "从车载前推视角拍摄，城市钠暖滤镜，路灯橙侧光，城市雾，城市钠暖，猫眼景深",
        "car-mount push angle, urban sodium-warm filter, street-orange side light, urban fog, urban sodium warm, cat-eye bokeh DOF"
    ),
    "极近微距细节": (
        "从显微镜视角拍摄，LensBaby 弯曲景深，LED环形顶光，超浅景深",
        "microscopic angle, LensBaby curved DOF, LED ring overhead light, ultra-shallow DOF"
    ),
    "高空云海上帝": (
        "从卫星俯视视角拍摄，云幕柔光，云海，冷调，全景深",
        "satellite top-down angle, cloud-dome soft light, cloud sea, cool tone, deep focus"
    ),
    "复古 VHS 记忆": (
        "从 4:3 复古视角拍摄，VHS 追踪线滤镜， CRT 扫描纹，4:3 帧比例，复古褪色，零饱和",
        "4:3 retro angle, VHS tracking-line filter, CRT scan lines, 4:3 frame, vintage fade, zero saturation"
    ),
    "烛光读书会": (
        "从钥匙孔视角拍摄，烛光暖调滤镜，烛光暖，反光板跳光，薄雾，浅景深",
        "keyhole angle, candle-warm filter, candle warm, bounce reflector, thin haze, shallow DOF"
    ),
    "工业机械力量": (
        "从车轮底视角拍摄，硬调黑白滤镜，菲涅耳硬光，高层云，硬光，高反差黑白",
        "under-wheel angle, hard-tone monochrome filter, Fresnel hard light, altostratus, hard light, high-contrast mono"
    ),
    "镜面倒影对称": (
        "从水面反射视角拍摄，镜像对称构图，镜面反射，日光中性，对称空镜景深",
        "water-reflection angle, mirror-symmetrical framing, mirror reflection, daylight neutral, symmetrical empty-frame DOF"
    ),
    "高空俯视云海": (
        "从无人机环绕下降视角拍摄，俯视广角，云海，冷调，深景深",
        "drone orbit-descend angle, top-down wide, cloud sea, cool tone, deep focus"
    ),
    "森林童话微光": (
        "从 360 小行星视角拍摄，Fuji Velvia 50 胶片滤镜，树叶斑驳，森林雾，微冷，中景深",
        "360 tiny-planet angle, Fuji Velvia 50 film filter, leaf-dappled, forest fog, slightly cool, medium DOF"
    ),
    "城市夜景赛博": (
        "从螺旋无人机视角拍摄，Teal-Orange 大片LUT，霓虹冷调，城市雾，背景奶油虚化",
        "helical-drone angle, teal-orange blockbuster LUT, neon-cold filter, urban fog, creamy background bokeh"
    ),
    "极慢机械动作": (
        "从滑轨螺旋视角拍摄，神经慢动作，S曲线对比增强，硬光，极慢，运动模糊增强",
        "slider-helical angle, AI-slomo, S-curve contrast, hard light, ultra-slow, motion-blur enhanced"
    ),
    "高速弹射加速": (
        "从弹射加速模糊视角拍摄，指数加速变速，高速方向模糊，光速，急速",
        "catapult-acceleration blur angle, exponential speed-up, high-speed directional blur, light-speed, rapid"
    ),
    "黄昏金边人像": (
        "从斜侧光视角拍摄，黄昏金边逆光，Kodak Portra 400，柔光，黄金时刻，浅景深奶油",
        "oblique-side-light angle, golden-hour rim backlight, Kodak Portra 400, soft light, golden hour, creamy shallow DOF"
    ),
    "镜面万花筒": (
        "从镜面万花筒视角拍摄，镜像网格，对称迷幻，霓虹冷，深景深",
        "mirror-kaleidoscope angle, mirror-grid, symmetrical psychedelia, neon cold, deep focus"
    ),
    "高空云海环轨": (
        "从无人机环绕轨道视角拍摄，云海，冷调，全景深",
        "drone orbit-track angle, cloud sea, cool tone, deep focus"
    ),
    "工业冷峻对称": (
        "从对称空镜视角拍摄，高反差黑白，正前顶光，硬光，城市雾，零饱和",
        "symmetrical empty-frame angle, high-contrast mono, front-top light, hard light, urban fog, zero saturation"
    ),
    "森林晨雾童话": (
        "从窗框视角拍摄，Fuji Pro 400H 胶片滤镜，晨雾，森林雾，微冷，中景深",
        "window-frame angle, Fuji Pro 400H film filter, morning mist, forest fog, slightly cool, medium DOF"
    ),
    "城市霓虹夜雨": (
        "从霓虹雨夜视角拍摄，霓虹冷调，暴雨，城市雾，背景奶油虚化",
        "neon-rainy-night angle, neon-cold filter, heavy rain, urban fog, creamy background bokeh"
    ),
    "高空俯视云海": (
        "从卫星俯视视角拍摄，云海，冷调，深景深",
        "satellite top-down angle, cloud sea, cool tone, deep focus"
    ),
    "微观水滴世界": (
        "从水滴折射视角拍摄，微距浅景，LED环形顶光，超浅景深",
        "water-droplet refraction angle, macro shallow, LED ring overhead, ultra-shallow DOF"
    ),
    "复古宝丽来": (
        "从宝丽来边框视角拍摄，Polaroid 边框，复古褪色，钨丝暖，浅景深",
        "Polaroid-frame angle, Polaroid border, vintage fade, tungsten warm, shallow DOF"
    ),
}

class ImageComboPreset:
    DESCRIPTION = "🎨 图片最佳组合预置（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"图片组合": (list(IMG_COMBO.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 图片组合, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 图片组合 == "随机":
            random.seed(seed)
            图片组合 = random.choice(list(IMG_COMBO.keys())[1:])
        return IMG_COMBO[图片组合]

# ⒆ 视频组合
VID_COMBO = {
    "随机": ("", ""),
    "电影级推镜慢动作": (
        "推镜镜头，速度 25% 慢动作，交叉溶解转场，24 fps 电影标准+180° 标准快门，方向运动模糊，轻微呼吸，斯坦尼稳定，推镜浅→深深深景动画，缓入缓出速度曲线，AI 智能跟随",
        "dolly-in camera move, 25% slow motion speed, cross dissolve transition, 24 fps cinematic + 180° standard shutter, directional motion blur, slight breathing, steadicam stabilization, dolly-in shallow to deep DOF animation, ease-in-out speed curve, AI smart follow"
    ),
    "赛博霓虹夜雨高速": (
        "无人机俯冲，速度 400% 急速，RGB 分离闪转场，60 fps 流体+1/100 s 清晰快门，高速方向模糊，明显呼吸，无人机三轴稳定，固定景深，线性加速速度曲线，AI 语义遮罩运镜",
        "drone dive camera move, 400% rapid speed, RGB split flash transition, 60 fps fluid + 1/100 s crisp shutter, high-speed directional motion blur, obvious breathing, drone 3-axis gimbal stabilization, locked DOF, linear acceleration speed curve, AI semantic mask camera move"
    ),
    "Vlog 轻快日常": (
        "滑轨侧移，速度 150% 稍快，滑动左→右转场，30 fps NTSC+180° 标准快门，方向运动模糊，轻微呼吸，滑轨匀速稳定，固定景深，缓入加速速度曲线，AI 智能裁剪",
        "slider-side camera move, 150% quick speed, slide left-to-right transition, 30 fps NTSC + 180° standard shutter, directional motion blur, slight breathing, slider constant stabilization, locked DOF, ease-in acceleration speed curve, AI smart crop"
    ),
    "工业冷峻对称推镜": (
        "推镜镜头，速度 50% 慢动作，闪黑转场，24 fps 电影+270° 运动模糊快门，低速旋转模糊，无呼吸，锁定三脚架，深景深动画，线性减速速度曲线，AI 语义分割自动对焦",
        "dolly-in camera move, 50% slow motion speed, flash-black transition, 24 fps cinematic + 270° motion-blur shutter, low-speed rotational blur, no breathing, locked-off tripod stabilization, deep DOF animation, linear deceleration speed curve, AI semantic-segmentation auto focus"
    ),
    "森林童话螺旋上升": (
        "螺旋上升，速度 25% 慢动作，水墨晕染转场，48 fps 高帧+180° 标准快门，螺旋运动模糊，轻微呼吸，斯坦尼稳定，前景雾扫焦，缓入缓出速度曲线，AI 智能景深",
        "helical-up camera move, 25% slow motion speed, ink-wash dissolve transition, 48 fps high-frame + 180° standard shutter, helical motion blur, slight breathing, steadicam stabilization, foreground mist focus sweep, ease-in-out speed curve, AI smart DOF"
    ),
    "城市夜景车载高速": (
        "车载侧跟，速度 400% 急速，镜头光晕转场，60 fps 流体+1/100 s 清晰快门，高速方向模糊，明显呼吸，车载减震稳定，固定景深，线性加速速度曲线，AI 智能跟随",
        "car-mount side-track camera move, 400% rapid speed, lens-flare transition, 60 fps fluid + 1/100 s crisp shutter, high-speed directional motion blur, obvious breathing, car-mount shock absorption stabilization, locked DOF, linear acceleration speed curve, AI smart follow"
    ),
    "微距水滴纳米景深": (
        "螺旋变焦，速度 12 fps 抽帧，圆形展开转场，240 fps 极慢+1/250 s 极清晰快门，随机向量模糊，大幅呼吸，机内 IBIS 稳定，纳米级拉焦，AI 语义变速，AI 智能超分",
        "helical-zoom camera move, 12 fps frame-drop speed, iris open transition, 240 fps ultra-slow + 1/250 s ultra-crisp shutter, random-vector motion blur, heavy breathing, in-body IBIS stabilization, nano-scale rack-focus, AI semantic speed ramp, AI smart super-resolution"
    ),
    "复古 VHS 记忆闪白": (
        "甩鞭右摇，速度 15 fps 早期胶片，闪白转场，15 fps 早期胶片+360° 极致模糊快门，VHS 追踪线模糊，明显呼吸，VHS 家用稳定，固定景深，阶梯减速速度曲线，AI 智能修复",
        "whip-pan-right camera move, 15 fps early-film speed, flash-white transition, 15 fps early film + 360° extreme-blur shutter, VHS tracking-line blur, obvious breathing, VHS home stable, locked DOF, step-ramp slow-down speed curve, AI smart restoration"
    ),
    "高空云海环绕上帝": (
        "无人机环绕轨道，速度 25% 慢动作，交叉溶解转场，48 fps 高帧+180° 标准快门，方向运动模糊，轻微呼吸，无人机三轴稳定，超深景深，缓入缓出速度曲线，AI 智能景深",
        "drone orbit-track camera move, 25% slow motion speed, cross dissolve transition, 48 fps high-frame + 180° standard shutter, directional motion blur, slight breathing, drone 3-axis gimbal stabilization, ultra-deep DOF, ease-in-out speed curve, AI smart DOF"
    ),
    "车载斯坦尼跟随": (
        "车载斯坦尼跟随，速度 150% 稍快，滑动左→右转场，30 fps NTSC+180° 标准快门，方向运动模糊，轻微呼吸，车载斯坦尼稳定，固定景深，缓入加速速度曲线，AI 智能跟随",
        "car-mount steadicam follow, 150% quick speed, slide left-to-right transition, 30 fps NTSC + 180° standard shutter, directional motion blur, slight breathing, car-mount steadicam stabilization, locked DOF, ease-in acceleration speed curve, AI smart follow"
    ),
    "船载减震海浪": (
        "船载减震，速度 100% 常速，硬切转场，25 fps PAL+180° 标准快门，手持抖动模糊，明显呼吸，船载减震稳定，固定景深，线性速度曲线，AI 智能稳定",
        "boat-mount shock absorption, 100% real-time speed, hard cut transition, 25 fps PAL + 180° standard shutter, handheld shake blur, obvious breathing, boat-mount shock absorption stabilization, locked DOF, linear speed curve, AI smart stabilization"
    ),
    "摇臂上升+前推电影": (
        "摇臂上升+前推，速度 50% 慢动作，交叉溶解转场，24 fps 电影+180° 标准快门，方向运动模糊，轻微呼吸，摇臂稳定，推镜浅→深深景动画，缓入缓出速度曲线，AI 语义分割自动对焦",
        "crane-up + dolly-in camera move, 50% slow motion speed, cross dissolve transition, 24 fps cinematic + 180° standard shutter, directional motion blur, slight breathing, crane stabilization, dolly-in shallow to deep DOF animation, ease-in-out speed curve, AI semantic-segmentation auto focus"
    ),
    "伸缩炮高速拉伸": (
        "伸缩炮拉伸，速度 400% 急速，透镜畸变转场，60 fps 流体+1/100 s 清晰快门，弹射加速模糊，大幅呼吸，伸缩炮稳定，固定景深，指数加速速度曲线，AI 智能去抖",
        "telescopic crane stretch, 400% rapid speed, lens distortion transition, 60 fps fluid + 1/100 s crisp shutter, catapult acceleration blur, heavy breathing, telescopic crane stabilization, locked DOF, exponential acceleration speed curve, AI smart de-shake"
    ),
    "肩扛斯坦尼人文": (
        "肩扛斯坦尼，速度 100% 常速，硬切转场，25 fps PAL+180° 标准快门，手持微抖模糊，轻微呼吸，肩扛斯坦尼稳定，固定景深，常速曲线，AI 智能色彩匹配",
        "shoulder steadicam, 100% real-time speed, hard cut transition, 25 fps PAL + 180° standard shutter, handheld micro-shake blur, slight breathing, shoulder steadicam stabilization, locked DOF, real-time speed curve, AI smart color match"
    ),
    "头盔云台 FPV 高速": (
        "头盔云台 FPV，速度 600% 超流体，闪黑转场，90 fps 超流体+1/250 s 极清晰快门，高速方向模糊，明显呼吸，头盔云台稳定，固定景深，线性加速速度曲线，AI 智能光流估计",
        "helmet gimbal FPV, 600% super-fluid speed, flash-black transition, 90 fps super-fluid + 1/250 s ultra-crisp shutter, high-speed directional motion blur, obvious breathing, helmet gimbal stabilization, locked DOF, linear acceleration speed curve, AI smart optical-flow estimation"
    ),
    "光纤陀螺稳定科研": (
        "光纤陀螺稳定，速度 25% 慢动作，圆形展开转场，240 fps 极慢+1/250 s 极清晰快门，随机向量模糊，无呼吸，光纤陀螺稳定，纳米级拉焦，AI 语义变速，AI 智能插帧",
        "fiber-optic gyro stabilization, 25% slow motion speed, iris open transition, 240 fps ultra-slow + 1/250 s ultra-crisp shutter, random-vector motion blur, no breathing, fiber-optic gyro stabilization, nano-scale rack-focus, AI semantic speed ramp, AI smart frame-interpolation"
    ),
    "AI 智能风格迁移": (
        "AI 智能风格迁移运镜，速度 150% 稍快，AI 语义融合转场，30 fps NTSC+180° 标准快门，AI 光流模糊，轻微呼吸，AI 后期稳定，固定景深，AI 智能风格迁移速度曲线，AI 智能风格迁移",
        "AI smart style-transfer camera move, 150% quick speed, AI semantic blend transition, 30 fps NTSC + 180° standard shutter, AI optical-flow blur, slight breathing, AI post-stabilization, locked DOF, AI smart style-transfer speed curve, AI smart style transfer"
    ),
}

class VideoComboPreset:
    DESCRIPTION = "🎬 视频最佳组合预置（中英双语）"
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("prompt_cn", "prompt_en")
    FUNCTION = "pick"
    CATEGORY = CATEGORY
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"视频组合": (list(VID_COMBO.keys()), {"default": "随机"}),
                             "手动输入": ("STRING", {"default": "", "multiline": True})},
                "optional": {"seed": ("INT", {"default": 0, "min": 0, "max": 0xffffffffffffffff})}}
    def pick(self, 视频组合, 手动输入, seed=0):
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if 视频组合 == "随机":
            random.seed(seed)
            视频组合 = random.choice(list(VID_COMBO.keys())[1:])
        return VID_COMBO[视频组合]

# ================================================================================
# 四、双语 ColorPicker（改造原 color_picker.py）
# ================================================================================
PALETTE = {
    "纯白": "#FFFFFF",
    "标准蓝": "#3C7BFF",
    "鲜红": "#FF0000",
    "浅蓝": "#94C4FF",
    "淡青": "#E0F7FF",
    "薄荷": "#D6F5D6",
    "淡粉": "#FFE6F0",
    "暖黄": "#FFF8E1",
    "薰衣草": "#E8E3FF",
    "蛋壳": "#FDF6E3",
    "冰灰": "#F2F5F7",
    "云朵": "#FAFAFA",
    "雾银": "#EBEFF2",
    "柔紫": "#F2E6FF",
    "奶茶": "#F8F0E5",
    "抹茶": "#E8F5E9",
    "天空": "#E3F2FD",
    "蜜桃": "#FFF0F5",
    "牛仔": "#5B9BFF",
    "湖水": "#4FC3F7",
    "薄荷绿": "#7CFFBF",
    "樱花": "#FFB7C5",
    "柠檬": "#FFFACD",
    "奶油": "#FFFDD0",
    "藕荷": "#D9C2D9",
    "藕粉": "#F5E6DE",
    "高级灰": "#B8BCC8",
    "石墨": "#708090",
    "渐变灰": ("#EBEBEB", "#C8C8C8"),
    "渐变米": ("#FFF8DC", "#FFE4B5"),
    "渐变蓝": ("#0070C0", "#6BB3FF"),
    "渐变薰衣草": ("#E8E3FF", "#C5B8FF"),
    "渐变薄荷": ("#D6F5D6", "#A8E6A8"),
    "渐变蜜桃": ("#FFF0F5", "#FFC5D9"),
    "渐变牛仔": ("#5B9BFF", "#8AB6FF"),
    "渐变柠檬": ("#FFFACD", "#FFF176"),
    "渐变藕荷": ("#D9C2D9", "#C0A0C0"),
    "渐变暖黄": ("#FFF8E1", "#FFECB3"),
    "渐变冰蓝": ("#E0F7FF", "#B3E5FC"),
    "渐变抹茶": ("#E8F5E9", "#C8E6C9"),
    "渐变天空": ("#E3F2FD", "#BBDEFB"),
    "渐变湖水": ("#4FC3F7", "#81D4FA"),
    "渐变高级灰": ("#B8BCC8", "#9AA0B8"),
    "渐变樱花": ("#FFB7C5", "#FF8FA3"),
    "渐变雾银": ("#EBEFF2", "#DDE2E6"),
    "渐变奶油": ("#FFFDD0", "#FFF8B8"),
}

class ColorPicker_mmx:
    DESCRIPTION = (
        "💕 哎呀✦颜色选择器（下拉+自定义）\n\n"
        "下拉：60+ 预置纯色/渐变 HEX\n"
        "自定义：任意 HEX/RGB 字符串\n\n"
        "输出：纯色→“颜色名#HEX”\n"
        "      渐变→“颜色名（#HEX向#HEX渐变）”"
    )
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("color_text_cn", "color_text_en")
    FUNCTION = "pick"
    CATEGORY = "哎呀✦MMX/color"

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "preset": (["自定义"] + list(PALETTE.keys()), {"default": "纯白"}),
                "custom_hex": ("STRING", {"default": "", "multiline": False}),
                "手动输入": ("STRING", {"default": "", "multiline": True}),
            }
        }

    def pick(self, preset: str, custom_hex: str, 手动输入: str) -> tuple[str, ...]:
        if 手动输入.strip():
            return (手动输入.strip(), 手动输入.strip())
        if custom_hex.strip():
            out = custom_hex.strip().upper()
            if not (out.startswith("#") and len(out) == 7):
                print(f"[ColorPicker_mmx] 警告：'{out}' 非标准 HEX，已回退 #FFFFFF")
                out = "#FFFFFF"
            result_cn = f"自定义{out}"
            result_en = f"Custom{out}"
        else:
            color_def = PALETTE.get(preset, "#FFFFFF")
            if isinstance(color_def, tuple):
                start, end = color_def
                result_cn = f"{preset}（{start}向{end}渐变）"
                result_en = f"{preset} gradient from {start} to {end}"
            else:
                result_cn = f"{preset}{color_def}"
                result_en = f"{preset}{color_def}"

        print(f"[ColorPicker_mmx] 输出 → {result_cn} | {result_en}")
        return (result_cn, result_en)

# ================================================================================
# 五、统一注册（图片 7 + 视频 10 + 组合 2 + 颜色 1 = 20 个节点）
# ================================================================================
register_node(PureCameraAngle,   "纯视角_mmx")
register_node(ProFilterTerm,     "专业滤镜_mmx")
register_node(LightDirection,    "光照方向_mmx")
register_node(LightQuality,      "光质_mmx")
register_node(WeatherAtmo,       "天气大气_mmx")
register_node(TempFeel,          "温度感受_mmx")
register_node(DOFPlan,           "景深规划_mmx")

register_node(CameraMotion,      "镜头运动_mmx")
register_node(MotionSpeed,       "运动速度_mmx")
register_node(TransSemantic,     "转场语义_mmx")
register_node(FpsShuttle,        "帧率快门_mmx")
register_node(MotionBlur,        "运动模糊_mmx")
register_node(LensBreathing,     "镜头呼吸_mmx")
register_node(StabMode,          "稳定模式_mmx")
register_node(DOFAnimation,      "景深动画_mmx")
register_node(SpeedCurve,        "速度曲线_mmx")
register_node(AISemanticCam,     "AI语义运镜_mmx")

register_node(ImageComboPreset,  "图片组合预置_mmx")
register_node(VideoComboPreset,  "视频组合预置_mmx")

register_node(ColorPicker_mmx,   "颜色选择器_mmx")
