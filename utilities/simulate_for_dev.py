# ### 读取 xephem格式用 readdb 方法
# ### 写出 xepheme格式， 用 writedb 方法
# ######### 人造卫星为 tle格式, 这里用readtle方法来阅读
# import ephem
# import json
#
# with open('../data/satellites.json', 'r') as f:
#     satellites = json.loads(f.read())
#
# tles = {}
# for satellite in satellites:
#     if satellite['tle'] == []:
#         continue
#
#     name = satellite['name'].upper()
#     norad_id = satellite['norad_id']
#     tle = satellite['tle']
#
#     print(name)
#
#     if name != "ISS (ZARYA)":
#         continue
#
#     print(tle)
#
#     if len(tle) < 5:
#         continue
#
#     line1 = name.upper()
#     line2 = tle[0] + ' ' +\
#             tle[1] + ' ' * (7 - len(tle[1])) +\
#             tle[2] + ' ' * (9 - len(tle[2])) +\
#             tle[3] + ' ' * 2 +\
#             tle[4] + ' ' * 2 +\
#             tle[5] + ' ' * 2 +\
#             tle[6] + ' ' + tle[7] + ' ' * 2 + tle[8]
#     line3 = tle[9] + ' ' +\
#             tle[10] + ' ' * (7 - len(tle[10])) +\
#             tle[11] + ' ' * (9 - len(tle[11])) +\
#             tle[12] + ' ' * 1 +\
#             tle[13] + ' ' * 2 +\
#             tle[14] + ' ' * (len(tle[4]) - len(tle[14])) +\
#             tle[15] + ' ' + tle[16]
#     print(line1)
#     print(line2)
#     print(line3)
#     print()
#
#
#     iss = ephem.readtle(line1, line2, line3)
#     iss.compute('2020/04/18')
#     print('%s %s' % (iss.sublong, iss.sublat))
#
#     tles.update({satellite['norad_id']: satellite['tle']})
#
# line1 = "ISS (ZARYA)"
# line2 = "1 25544U 98067A   03097.78853147  .00021906  00000-0  28403-3 0  8652"
# line3 = "2 25544  51.6361  13.7980 0004256  35.6671  59.2566 15.58778559250029"
# iss = ephem.readtle(line1, line2, line3)
# iss.compute('2003/3/23')
# print('%s %s' % (iss.sublong, iss.sublat))