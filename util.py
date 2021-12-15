# the chinese number must not to be 特辑
# only from 0 to 100
def convert(chinese_number):
    dict_numbers = {
        '零': 0,
        '一': 1,
        '二': 2,
        '三': 3,
        '四': 4,
        '五': 5,
        '六': 6,
        '七': 7,
        '八': 8,
        '九': 9,
    }
    dict_units = {
        '十': 10,
        '百': 100,
        '千': 1000
    }

    if chinese_number[0] == '零':
        return 0 if len(chinese_number) == 1 else -1

    ans = 0
    unit = 1
    base = 0

    for i in range(len(chinese_number)):
        if chinese_number[i] in dict_numbers.keys():
            base = dict_numbers[chinese_number[i]]
        elif chinese_number[i] in dict_units.keys():
            if base == 0:
                base = 1
            unit = dict_units[chinese_number[i]]
            ans += base * unit
            base = 0
            unit = 1
    if base != 0:
        ans += base * unit

    if unit != 1:
        ans += base * unit
    return ans
