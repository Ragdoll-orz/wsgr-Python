"""
ver 1.0
"""
import uiautomator2 as u2
import pytesseract
import cv2
import numpy
from time import sleep
import sys
"""
存在的问题：
    ocr第六章识别不了
"""


class WSGR:

    def __init__(self):
        # 连接设备
        self.device = u2.connect('127.0.0.1:5555')
        # 设置tesseract的路径（如果尚未在环境变量中配置）
        pytesseract.pytesseract.tesseract_cmd = r'D:\Tesseract\tesseract.exe'  # 根据你的安装位置调整
        self.dayMaxTanga = 50     # 战利品总数
        self.dayGotTanga = 0    # 今天获得战利品数
        self.dayMaxShip = 500   # 能获得船的总数
        self.dayGotShip = 0     # 今天获得船的数量
        self.dock = 0   # 船坞容量
        self.shipInDock = 0     # 当前船只数
        self.battle_times = 0  # 本次出击次数
        self.harvest_times = 0  # 收获次数
        self.bucket = 0     # 消耗的桶

        self.type = 0   # 模式：战利品0、活动练级1、地图练级2、纯远征3
        self.team = 3   # 队伍

        self.init()
        while True:
            if self.dayGotTanga == self.dayMaxTanga or self.shipInDock == self.dock:
                print(f"战利品：{self.dayGotTanga}/{self.dayMaxTanga}  捞船：{self.shipInDock}/{self.dock}")
                print('结束')
                break
            print(f"战利品：{self.dayGotTanga}/{self.dayMaxTanga}  捞船：{self.shipInDock}/{self.dock}")
            self.controller()

    def test(self):     # 测试用
        self.clicks(896, 487)  # 点击出征

    def controller(self, maps=None, area=None):
        if self.type == 0:  # 战利品
            self.select_map(9, 1)
            self.is_ship_ok()   # 检查船只
            self.battle_control()
        elif self.type == 1:
            pass
        elif self.type == 2:
            pass
        elif self.type == 3:
            pass
        else:
            print("模式选择异常")
            sys.exit()

    def battle_control(self):
        self.clicks(835, 506)    # 点击开始出征
        self.clicks(500, 500, 2)  # 加速
        self.clicks(500, 500)  # 加速
        self.clicks(500, 500)  # 加速
        # self.wait(783, 476, 945, 525, "开始战斗")
        self.wait(640, 477, 773, 525, "撤退")
        self.battle()

        self.wait(300, 340, 350, 365, "前进")     # 第二场战斗
        self.clicks(330, 350, )     # 点击前进
        self.clicks(500, 500, 2)  # 加速
        self.clicks(500, 500)  # 加速
        self.clicks(500, 500)  # 加速
        self.wait(640, 477, 773, 525, "撤退")
        if self.ocr(self.screenshot(34, 242, 74, 263)) != "补给":
            print("未发现补给舰")
            self.clicks(707, 502)   # 撤退, 回到出征
            return
        self.battle()
        self.dayGotTanga += 1
        self.wait(300, 340, 350, 365, "前进")  # 第三场战斗
        self.clicks(632, 353)   # 撤退

    def battle(self):
        self.clicks(864, 503, 2)  # 开始战斗
        # 阵型选择，待优化
        self.clicks(600, 490)   # 单横
        self.wait(400, 20, 570, 80, "战斗", 600, 340, 650, 362, "放弃")

    def wait(self, x1, y1, x2, y2, text1=None, a1=None, b1=None, a2=None, b2=None, text2=None, flag=None):
        if text2 is None:
            if flag is None:
                while True:
                    text = str(self.ocr(self.screenshot(x1, y1, x2, y2, False)))
                    if text != text1:
                        if text1 == "前进":
                            self.clicks(500, 400, 4)  # 防止网络波动
                        print(f"等待结束-{text1}")
                        sleep(1)
                    else:
                        print(f"{text1}-结束")
                        break
            else:
                while True:
                    if self.ocr(self.screenshot(x1, y1, x2, y2, False)) == flag:
                        print("结束")
                        break
                    else:
                        print("等待结果")
                        sleep(1)
        else:
            while True:
                if self.ocr(self.screenshot(x1, y1, x2, y2)) == text1:    # 结算页面
                    self.battle_end()
                    print(f"{text1}-结束")
                    break
                sleep(1)
                if self.ocr(self.screenshot(a1, b1, a2, b2)) == text2:  # 是否夜战
                    self.clicks(630, 353)   # 点击放弃
                    self.wait(400, 20, 570, 80, "战斗")
                    self.battle_end()
                    print(f"{text2}-结束")
                    break
                else:
                    print(f"等待结束-{text1}-{text2}")
                    sleep(1)

    # def wait_color(self, x, y, flag):   # 待优化
    #     while True:
    #         if self.color_compare(self.screenshot(x, y))

    def battle_end(self):
        sleep(3)
        # self.wait(578, 294, 724, 363, flag=True)
        self.clicks(500, 400, 4)  # 战斗结果
        # self.wait(578, 294, 724, 363, flag=False)
        self.clicks(500, 400, 4)  # 经验加成
        if self.color_compare(self.screenshot(759, 173), "战斗结果"):
            self.clicks(500, 400, 3)  # 船只获取
            self.dayGotShip += 1
            self.shipInDock += 1

    def is_ship_ok(self):   # 需位于出征准备页
        y = 90
        temp = 1
        for x in range(107, 571, 116):      # 107,90,  223,y
            if self.team == temp:
                self.clicks(x, y, 2)
            temp += 1
        self.clicks(422, 425, 2)  # 点击快速修理
        for i in range(2):
            print(f"第{i+1}次检查")
            y = 324
            num = 1
            for x in range(53, 713, 120):
                if self.color_compare(self.screenshot(x, y), "出征检查") is not True:  # 53,324, 163,y
                    self.clicks(422, 425, 2)    # 点击快速修理
                    self.clicks(x, y, 2)   # 修理船只
                    self.bucket += 1
                    print(f"已修理第{num}位船只")
                else:
                    print(f"第{num}位船只，良好")
                num += 1

    def select_map(self, maps, area):   # 需位于出征页面，选择地图
        text = self.ocr(self.screenshot(36, 281, 107, 311))     # 获取章节信息
        print(text)
        num_chs = ['一', '二', '三', '四', '五', '六', '七', '八', '九']
        sm_num = None
        for arg in num_chs:
            if text.find(arg) != -1:
                sm_num = num_chs.index(arg) + 1
        if sm_num is None:
            print(f"章节选择错误->ocr结果：{text}")
            sys.exit()
        while True:     # 控制章节选择
            if sm_num == maps:
                break
            if maps > sm_num:
                self.clicks(90, 364, 2)     # 点章节下面
                sm_num += 1
            elif maps < sm_num:
                self.clicks(90, 235, 2)     # 点章节上面
                sm_num -= 1
        text = self.ocr(self.screenshot(672, 93, 879, 118))     # 获取海域信息
        text = text.split('/')
        sm_area = int(text[0].split('-')[1])
        while True:     # 控制海域选择
            if sm_area == area:
                self.clicks(600, 280, 2)    # 进入海域
                break
            if area > sm_area:
                self.clicks(932, 280, 2)
                sm_area += 1
            elif area < sm_area:
                self.clicks(256, 280, 2)
                sm_area -= 1

    def init(self):     # 获取战利品数量，船只数量等
        text1 = '船坞容量'
        text2 = '战利品数量'
        text3 = '打捞船只数量'
        self.clicks(762, 488, 2)   # 点击船坞
        self.clicks(822, 246, 2)   # 点击船只，进入船坞
        self.ocr_handle(self.screenshot(857, 16, 927, 37), 'shipInDock', 'dock', text1)
        sleep(1)
        self.clicks(30, 30, 2)      # 返回
        self.clicks(30, 30, 2)      # 返回，到主界面
        self.is_expedition_over("主界面")      # 验证远征完成，来到出征页面
        self.ocr_handle(self.screenshot(773, 16, 822, 34), 'dayGotTanga', 'dayMaxTanga', text2)
        self.ocr_handle(self.screenshot(868, 14, 926, 33), 'dayGotShip', 'dayMaxShip', text3)
        print(f"{text1}:{self.shipInDock}/{self.dock} {text2}:{self.dayGotTanga}/{self.dayMaxTanga} {text3}:{self.dayGotShip}/{self.dayMaxShip}")

    def screenshot(self, x1, y1, x2=None, y2=None, grey=True):
        ss = self.device.screenshot(format='opencv')  # 截图
        if x2 is None:    # 获取某点颜色
            color_rgb = ss[y1, x1][::-1]
            # print(f"RGB颜色值: {color_rgb}")
            return color_rgb
        ss = ss[y1:y2, x1:x2]   # 裁剪后的图片
        if grey:
            ss = cv2.cvtColor(ss, cv2.COLOR_BGR2GRAY)     # 灰度处理
        cv2.imwrite('./image/temp.png', ss)      # 保存图片
        return ss

    @staticmethod
    def ocr(img, lang=r'chi_sim'):
        text = pytesseract.image_to_string(img, lang)
        text = text.replace('\n', '')  # 去除换行
        # print(text)
        return text

    def ocr_handle(self, img, name1, name2, ps):
        text = pytesseract.image_to_string(img)     # ocr
        if text:
            text = text.replace('\n', '')   # 去除换行
            text = text.split('/')  # 按/分割
            setattr(self, name1, int(text[0]))   # 修改传入的变量值
            setattr(self, name2, int(text[1]))
            print(f"{ps}:{getattr(self, name1)}/{getattr(self, name2)}")
        else:
            print(f"未找到-{ps}ocr")

    def is_expedition_over(self, text):
        if text == '主界面':   # 255,100,54
            if self.color_compare(self.screenshot(934, 455), text):     # 判断远征完成
                self.clicks(896, 487)   # 点击出征
                self.expedition()
            else:
                self.clicks(896, 487)  # 点击出征
        elif text == '出征':
            pass
        else:
            print(f"{text}：远征检查出错")
            sys.exit()

    def expedition(self):   # 远征，已进入远征页面
        while True:     # 820,147  ,x,254
            flag = True
            x = 820
            for y in range(147, 575, 107):  # 循环4次
                if self.color_compare(self.screenshot(x, y), "远征"):     # 判断远征完成
                    self.expedition_click(x, y)
                    flag = False
            if flag:
                print(f"今日远征:{self.harvest_times}次")
                self.clicks(175, 23, 2)  # 出征页面
                break

    def expedition_click(self, x, y):
        self.clicks(x, y, 2)   # 点击收获
        self.clicks(x, y, 2)   # 点击继续
        self.clicks(369, 434, 2)   # 继续改编队远征
        self.harvest_times += 1

    @staticmethod
    def color_compare(color_rgb, text):
        if text == "主界面":
            # 预定义颜色
            predefined_color_rgb = numpy.array([255, 100, 54])      # 远征红点，红色
            # 颜色相似阈值
            threshold = 50
        elif text == "出征检查":
            predefined_color_rgb = numpy.array([73, 163, 125])      # 正常血量，绿色
            threshold = 50
        elif text == "远征":
            predefined_color_rgb = numpy.array([253, 228, 66])      # 远征完成,黄色
            threshold = 50
        elif text == "战斗结果":
            predefined_color_rgb = numpy.array([255, 227, 144])     # 战斗结果,黄色
            threshold = 50
        else:
            print(f"{text}:颜色比较异常")
            sys.exit()
        # 计算颜色的欧氏距离
        distance = numpy.linalg.norm(color_rgb - predefined_color_rgb)
        # print(f"颜色距离: {distance}")
        # 判断颜色是否相似（距离阈值可以根据需要调整）
        if distance < threshold:
            # print("颜色相似")
            return True
        else:
            # print("颜色不相似")
            return False

    def clicks(self, x, y, time=1):
        self.device.click(x, y)     # 点击x,y坐标
        sleep(time)    # 延时,秒


if __name__ == '__main__':
    wsgr = WSGR()
    # wsgr.ocr_handle(wsgr.screenshot(772, 11, 820, 32))
    # wsgr.screenshot(934, 455)


