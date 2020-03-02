# coding:utf-8
import re
import time


def get_zh2num_dict():
    num2zh = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九"]
    # 不想打字，拼接字符串
    for i in range(100):
        if i < 10:
            pass
        elif i >= 10 and i < 20:
            m = i % 10
            r = "十"
            if m != 0:
                r += num2zh[m]
            num2zh.append(r)
        elif i >= 20 and i < 100:
            m = i % 10
            index = i // 10
            r = num2zh[index] + "十"
            if m != 0:
                r += num2zh[m]
            num2zh.append(r)
        else:
            raise ValueError("Not support")
    zh2num = dict([(zh, i) for i, zh in enumerate(num2zh)])
    return zh2num


def is_include(query, keywords: list, return_word=False):
    for keyword in keywords:
        if keyword in query:
            if return_word:
                return True, keyword
            return True
    if return_word:
        return False, None
    return False


class Extractor:
    def __init__(self):
        self.year_extract_keyword = ["明年"]
        self.year_extract_pattern = re.compile("(?P<value>[0-9]{1,2})年后")

        self.month_extract_keyword = ["下一个月"]
        self.month_extract_pattern = re.compile("(?P<value>[0-9]{1,2})个{0,1}月后")

        self.day_extract_keyword = ["今天", "明天", "后天", "大后天", "今日", "后日", "明日"]
        self.day_extract_pattern = re.compile("(?P<value>[0-9]{1,2})[天|日]后")
        self.day_extract_pattern2 = re.compile("(?P<value>[0-9]{1,2})[日|号][^后]")
        self.time_format_pattern = re.compile("[小时|点][半|钟]{0,1}(.{1,3}分钟{0,1}.{1,3}秒钟{0,1}){0,1}")
        self.time_extract_pattern = re.compile("[0-9]{1,2}:[0-9]{1,2}:[0-9]{1,2}")
        self.zh2num_dict = get_zh2num_dict()

    def zh2num(self, text):
        result = text
        keys = sorted(self.zh2num_dict, key=lambda x: self.zh2num_dict[x], reverse=True)  # 从九十九往零检查，替换
        for key in keys:
            if key in result:
                result = result.replace(key, str(self.zh2num_dict[key]))
        return result

    def time_format(self, text):
        """
        中文格式时间转换
        :param text:
        :return:
        """
        match_str = re.search(self.time_format_pattern, text)
        if match_str is None:
            return text
        else:
            match_str = match_str[0]
            result = match_str
            if "时" in match_str:
                result = result.replace("时", ":")
            elif "点钟" in match_str:
                result = result.replace("点钟", ":")
            elif "点" in match_str:
                result = result.replace("点", ":")
            if "半" in text:
                result = result.replace("半", "30:")
            elif "分钟" in match_str:
                result = result.replace("分钟", ":")
            elif "分" in text:
                result = result.replace("分", ":")
            else:
                result += "00:"
            if "秒" in match_str:
                result = result.replace("秒", "")
            else:
                result += "00"
            text = text.replace(match_str, result)
            return text

    def _extract(self, string):
        month_day = [-1, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
        now_time = time.time()

        time_array = time.localtime(int(now_time))
        format_time = time.strftime("%Y:%m:%d:%H:%M:%S", time_array)
        time_list = list(map(int, format_time.split(":")))
        # 闰年？
        if time_list[0] % 4 == 0 and time_list[0] % 400 == 0:
            month_day[2] = 29
        # 检查年份
        flag, word = is_include(string, self.year_extract_keyword, return_word=True)
        if flag:
            if word == "明年":
                time_list[0] += 1
        else:
            match_result = self.year_extract_pattern.search(string)
            if match_result:
                value = match_result.group("value")
                time_list[0] += int(value)
        # 检查月
        flag, word = is_include(string, self.month_extract_keyword, return_word=True)
        if flag:
            if word == "下一个月":
                time_list[1] += 1
        else:
            match_result = self.month_extract_pattern.search(string)
            if match_result:
                value = match_result.group("value")
                value = int(value)
                time_list[1] += value % 12
                if value > 12:
                    time_list[0] += (value // 12)
        # 检查日子
        flag, word = is_include(string, self.day_extract_keyword, return_word=True)
        if flag:
            if "明" in word:
                time_list[2] += 1
            elif "后" in word:
                v = 2
                if "大" in word:
                    v = 3
                time_list[2] += v
        else:

            match_result = self.day_extract_pattern.search(string)
            if match_result:
                value = match_result.group("value")
                value = int(value)
                rest_day = month_day[time_list[1]] - time_list[2]  # 当前月剩下的日子
                if value <= rest_day:
                    time_list[2] += value
                else:
                    # TODO 如果超过不止一个月
                    time_list[2] += value - rest_day
                    time_list[1] += 1
                    if time_list[1] > 12:
                        time_list[0] += 1
                        time_list[1] = time_list[1] % 12

            match_result = self.day_extract_pattern2.search(string)
            if match_result:
                value = match_result.group("value")
                value = int(value)
                time_list[2] = value

        # 设置时分秒
        match_result = self.time_extract_pattern.search(string)
        if match_result:
            time_string = match_result[0]
            h, m, s = time_string.split(":")
            if any(["中午" in string, "下午" in string, "晚上" in string]) and int(h) <= 12:
                h = int(h) + 12
            time_list[3] = int(h)
            time_list[4] = int(m)
            time_list[5] = int(s)
        # 转成时间戳
        time_list = tuple(time_list) + (0, 0, 0)
        timestamp = time.mktime(time_list)
        return time_list, timestamp

    def extract(self, string):
        """

        :param string:
        :return:
        """
        # 先转成数字
        string = self.zh2num(string)
        string = self.time_format(string)
        time_list, timestamp = self._extract(string)
        return time_list, timestamp


