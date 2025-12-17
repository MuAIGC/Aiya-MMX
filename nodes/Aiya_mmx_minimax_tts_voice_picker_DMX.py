# Aiya_mmx_voice_picker_DMX.py  –  独立音色选择器
from __future__ import annotations
from ..register import register_node

# ========== 官方 80 种主音色 ID（2025-12 更新） ==========
VOICE_PRESETS = [
    "male-qn-qingse",        # 01 青涩青年        中文
    "male-qn-jingying",      # 02 精英青年        中文
    "male-qn-badao",         # 03 霸道青年        中文
    "male-qn-daxuesheng",    # 04 青年大学生      中文
    "female-shaonv",         # 05 少女            中文
    "female-yujie",          # 06 御姐            中文
    "female-chengshu",       # 07 成熟女性        中文
    "female-tianmei",        # 08 甜美女性        中文
    "male-qn-qingse-jingpin", # 09 青涩青年-b      中文
    "male-qn-jingying-jingpin", #10 精英青年-b      中文
    "male-qn-badao-jingpin", # 11 霸道青年-b      中文
    "male-qn-daxuesheng-jingpin", #12 大学生-b      中文
    "female-shaonv-jingpin", # 13 少女-b          中文
    "female-yujie-jingpin",  # 14 御姐-b          中文
    "female-chengshu-jingpin", #15 成熟女-b        中文
    "female-tianmei-jingpin", #16 甜美女-b        中文
    "clever_boy",            # 17 聪明男童        中文
    "cute_boy",              # 18 可爱男童        中文
    "lovely_girl",           # 19 萌萌女童        中文
    "cartoon_pig",           # 20 卡通猪小琪      中文
    "bingjiao_didi",         # 21 病娇弟弟        中文
    "junlang_nanyou",        # 22 俊朗男友        中文
    "chunzhen_xuedi",        # 23 纯真学弟        中文
    "lengdan_xiongzhang",    # 24 冷淡学长        中文
    "badao_shaoye",          # 25 霸道少爷        中文
    "tianxin_xiaoling",      # 26 甜心小玲        中文
    "qiaopi_mengmei",        # 27 俏皮萌妹        中文
    "wumei_yujie",           # 28 妩媚御姐        中文
    "diadia_xuemei",         # 29 嗲嗲学妹        中文
    "danya_xuejie",          # 30 淡雅学姐        中文
    "Chinese (Mandarin)_Reliable_Executive",      # 31 沉稳高管        中文
    "Chinese (Mandarin)_News_Anchor",             # 32 新闻女声        中文
    "Chinese (Mandarin)_Mature_Woman",            # 33 傲娇御姐        中文
    "Chinese (Mandarin)_Unrestrained_Young_Man",  # 34 不羁青年        中文
    "Arrogant_Miss",                              # 35 嚣张小姐        中文
    "Robot_Armor",                                # 36 机械战甲        中文
    "Chinese (Mandarin)_Kind-hearted_Antie",      # 37 热心大婶        中文
    "Chinese (Mandarin)_HK_Flight_Attendant",     # 38 港普空姐        中文
    "Chinese (Mandarin)_Humorous_Elder",          # 39 搞笑大爷        中文
    "Chinese (Mandarin)_Gentleman",               # 40 温润男声        中文
    "Chinese (Mandarin)_Warm_Bestie",             # 41 温暖闺蜜        中文
    "Chinese (Mandarin)_Male_Announcer",          # 42 播报男声        中文
    "Chinese (Mandarin)_Sweet_Lady",              # 43 甜美女声        中文
    "Chinese (Mandarin)_Southern_Young_Man",      # 44 南方小哥        中文
    "Chinese (Mandarin)_Wise_Women",              # 45 阅历姐姐        中文
    "Chinese (Mandarin)_Gentle_Youth",            # 46 温润青年        中文
    "Chinese (Mandarin)_Warm_Girl",               # 47 温暖少女        中文
    "Chinese (Mandarin)_Kind-hearted_Elder",      # 48 花甲奶奶        中文
    "Chinese (Mandarin)_Cute_Spirit",             # 49 憨憨萌兽        中文
    "Chinese (Mandarin)_Radio_Host",              # 50 电台男主播      中文
    "Chinese (Mandarin)_Lyrical_Voice",           # 51 抒情男声        中文
    "Chinese (Mandarin)_Straightforward_Boy",     # 52 率真弟弟        中文
    "Chinese (Mandarin)_Sincere_Adult",           # 53 真诚青年        中文
    "Chinese (Mandarin)_Gentle_Senior",           # 54 温柔学姐        中文
    "Chinese (Mandarin)_Stubborn_Friend",         # 55 嘴硬竹马        中文
    "Chinese (Mandarin)_Crisp_Girl",              # 56 清脆少女        中文
    "Chinese (Mandarin)_Pure-hearted_Boy",        # 57 清澈邻家弟      中文
    "Chinese (Mandarin)_Soft_Girl",               # 58 软软女孩        中文
    "Cantonese_ProfessionalHost（F)",             # 59 粤普女主持      粤语
    "Cantonese_GentleLady",                       # 60 粤语温柔女      粤语
    "Cantonese_ProfessionalHost（M)",             # 61 粤普男主持      粤语
    "Cantonese_PlayfulMan",                       # 62 粤语活泼男      粤语
    "Cantonese_CuteGirl",                         # 63 粤语可爱女      粤语
    "Cantonese_KindWoman",                        # 64 粤语善良女      粤语
    "Santa_Claus",                                # 65 圣诞老人        英文
    "Grinch",                                     # 66 格林奇          英文
    "Rudolph",                                    # 67 鲁道夫          英文
    "Arnold",                                     # 68 阿诺德          英文
    "Charming_Santa",                             # 69 魅力圣诞老人    英文
    "Charming_Lady",                              # 70 魅力女士        英文
    "Sweet_Girl",                                 # 71 甜美女孩        英文
    "Cute_Elf",                                   # 72 可爱精灵        英文
    "Attractive_Girl",                            # 73 魅力女孩        英文
    "Serene_Woman",                               # 74 宁静女士        英文
    "English_Trustworthy_Man",                    # 75 可信男士        英文
    "English_Graceful_Lady",                      # 76 优雅女士        英文
    "English_Aussie_Bloke",                       # 77 澳洲男士        英文
    "English_Whispering_girl",                    # 78 耳语少女        英文
    "English_Diligent_Man",                       # 79 勤奋男士        英文
    "English_Gentle-voiced_man",                  # 80 温柔男声        英文
]


class MiniMaxVoicePicker_DMX:
    DESCRIPTION = (
        "💕 哎呀✦MiniMax 音色选择器（DMXAPI）\n\n"
        "【用途】单独输出一个 voice_id 字符串，可连接下游 TTS 节点\n"
        "【列表】80 种官方主音色（中英粤全覆盖），下拉框即拿即用\n"
        "【连接】将本节点输出的「voice_id」接入「MiniMax TTS」的 custom_voice_id 口即可生效\n"
        "【好处】① 复用音色 ② 一键切换 ③ 工作流更直观"
    )

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("voice_in",)
    FUNCTION = "pick_voice"
    CATEGORY = "哎呀✦MMX/audio"

    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "音色选择": (VOICE_PRESETS, {
                    "default": "female-tianmei-jingpin",
                    "label": "官方主音色（80 种）"
                }),
            }
        }

    def pick_voice(self, 音色选择):
        # 下拉框值本身就是合法 ID，直接返回
        return (音色选择,)


# 注册节点
register_node(MiniMaxVoicePicker_DMX, "MiniMax TTS音色选择器_DMX")