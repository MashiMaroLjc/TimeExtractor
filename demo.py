# coding:utf-8
from time_extractor import Extractor
example = [
    "八点提醒我出门",
    "大后天八点提醒我出门",
    "三月八日早上八点提醒我出门",
    "三月……嗯……八日早上八点提醒我出门",
    "三月八日中午一点提醒我出门",
    "三月八日晚上九点提醒我出门",
    "3月八日晚上9点提醒我出门",
    "3月八日晚上九点半提醒我出门",
    "3月八日晚上9点37分零六秒提醒我出门",
    "3月八日晚上09:37:06提醒我出门",
    "明年3月八日晚上09:37:06提醒我出门",
    "五十年后3月八日晚上09:37:06提醒我出门",
    "下一个月后3月八日晚上09:37:06提醒我出门",
    "十三个月后3月八日晚上09:37:06提醒我出门",
    "今天八点提醒我出门",
    "明天八点提醒我出门",
    "后天八点提醒我出门",
    "十天后八点提醒我出门",
    "二十日八点提醒我出么",
    "四十日后八点提醒我出么",
]
extractor = Extractor()
MAX_LEN = 100
print("测试例子")
for i, ex in enumerate(example):
    time_list, timestamp = extractor.extract(ex)
    time_str = "{}年{}月{}日,{}时{}分{}秒".format(time_list[0], time_list[1], time_list[2], \
                                            time_list[3], time_list[4], time_list[5])
    print(ex, " ---> ", time_str,timestamp)
