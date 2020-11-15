import matplotlib as mpl
mpl.rcParams['toolbar'] = 'None'

from matplotlib import pyplot as plt
import numpy as np
import time
import subprocess

# ==============defining variables===========================

# user-const
VIEW_HOUR = 0.1  # 소수점 값이 들어가면 정확한 눈금이 안 나올 수도 있음
UPDATE_DELAY = 1
USER_X_TICK = 5  # min 단위
USER_LINE_THICKNESS = 1
WINDOW_TITLE = "snmp get"
BPS = True  # which means Bps=False


# constant (sec based)
HOUR = 60 * 60
MINUTE = 60
DATA_LEN = VIEW_HOUR*HOUR//UPDATE_DELAY+1  # +1 is not necessary but since memory is not a big issue, used +1 or safety


# same order as bps_data,LOCAL_Ext, AVG , .... => remember!!!
commands = []
# colors
options = []

# read file  ....dirty, need update
with open("config.txt", "r", encoding="UTF-8") as f:
    lines = f.readlines()
    for i in range(len(lines)):
        temp = lines[i].split(" ")  # 띄어쓰기로 구분  ?color=green ?fill=True TestApp.exe
        temp_d = {"fill": "", "color": "", "name": ""}  # 미리 옵션을 지정
        for j in range(len(temp)):  # list
            if temp[j][0] == '?':  # 옵션 확인
                temp_user_option = temp[j][1:].split("=")
                temp_d[temp_user_option[0]] = temp_user_option[1]  # ewww dirty
        options.append(temp_d)

        for i in temp:
            if i[0] != '?':
                commands.append(i)

        commands.append(" ".join(temp_commands))
        temp_commands = []

# commands len
COMMAND_COUNT = len(commands)

# for exit
active = True

# bps_data
bps_data = np.empty((COMMAND_COUNT, 0), int)
time_data = np.empty((COMMAND_COUNT, 0), int)

# LOCAL_Ext value
MAX = [0 for _ in range(len(commands))]
AVG = [0 for _ in range(len(commands))]

# OID list
OID = []

# for legend-plots, legend, artist
plots = []
legends = []
legends_artist = []

# temp diction -- for np append  -- usage:np_temp_dictionary[data].append([value])
np_temp_dictionary = {"bps_data": [], "time_data": []}

# for comparison for BPS data
first_value = [0 for _ in range(len(commands))]
second_value = [0 for _ in range(len(commands))]

# set up oid --- almost same as get_value
for i in commands:
    SG = str(subprocess.getoutput(i)).split("\n")
    for d in SG:
        if "OID" in d:
            OID.append(d.split('=')[1].replace(" ", ""))


# setup for-legend var --- provide empty space, may be depreciated
for i in range(COMMAND_COUNT):
    plots.append(None)
    legends.append(None)
    legends_artist.append(None)


# ==============defining functions===========================

# get value from snmpget and store them as 0x
def get_value(command):
    # print(command)
    SnmpGet = str(subprocess.getoutput(command)).split("\n")

    for dat in SnmpGet:
        if "Value" in dat:
            if BPS:
                return int(dat.split('=')[1].replace(" ", ""), 16) * 8 / UPDATE_DELAY  # x8 to 'bit'
            else:
                return int(dat.split('=')[1].replace(" ", ""), 16) / UPDATE_DELAY

    print(f"error! failed to catch correct value. see {SnmpGet}")
    return 0


# Epoch time to
def epoch_to_time(t):
    temp = time.localtime(t)
    return f"{temp.tm_hour}:{temp.tm_min:02}"


# sec to hour:min:sec
def sec_format(t):
    tm_hour = int(((t // 60) // 60) % 24)
    tm_min = int((t // 60) % 60)
    tm_sec = int(t % 60)
    return f"{tm_hour}:{tm_min:02}:{tm_sec:02}"


# break 'while'
def handle_close(evt):
    global active
    active = False


def set_axes_label_old():
    # make ticks first
    """x축 틱"""
    tick_label = []  # set ticks first
    new_label = []  # label
    temp_current_time = CurrentTime  # temp value to keep currenttime from changing
    temp_leftover = (CurrentTime // 60) % USER_X_TICK  # 전체 분을 User_X_TICk로 나눔 ->나머지 구하기
    temp_current_time -= temp_leftover * MINUTE  # temp_current_time 을 5분 단위로 조정
    for _ in range(1, int((60 / USER_X_TICK) * VIEW_HOUR + 1)):  #
        tick_label.append(temp_current_time)
        temp_current_time -= USER_X_TICK * MINUTE

    axes.set_xticks(tick_label)  # set ticks

    """x축 라벨"""
    for i in tick_label:
        new_label.append(epoch_to_time(int(i)))

    axes.set_xticklabels(new_label)

    """y축 틱"""
    temp_ymax = axes.get_ylim()[1]
    temp_exp = np.log2(temp_ymax)//10  # temp1 재사용
    temp_unit = int(np.log10(temp_ymax)) * np.power(1024, temp_exp)

    # x: 100, 10 등 단위. y는 한계 계수
    temp_ytick = [np.power(10, temp_unit) * y for y in range(10) if np.power(10, temp_unit)*y < temp_ymax]
    axes.set_yticks(temp_ytick)

    """y축 라벨"""
    temp_list = []
    for i in temp_ytick:
        temp_list.append(f'{i:.00f}{"BPS" if temp_exp==0 else "Kbps" if temp_exp==1 else "Mbps" if temp_exp==2 else "Gbps" if temp_exp==3 else "Tbps"}')

    axes.set_yticklabels(temp_list)


def set_axes_label():
    # make ticks first
    """x축 틱"""
    tick_label = []  # set ticks first
    new_label = []  # label
    temp_current_time = CurrentTime  # temp value to keep currenttime from changing
    temp_leftover = (CurrentTime // 60) % USER_X_TICK  # 전체 분을 User_X_TICk로 나눔 ->나머지 구하기
    temp_current_time -= temp_leftover * MINUTE  # temp_current_time 을 5분 단위로 조정
    for _ in range(1, int((60 / USER_X_TICK) * VIEW_HOUR + 1)):  #
        tick_label.append(temp_current_time)
        temp_current_time -= USER_X_TICK * MINUTE

    axes.set_xticks(tick_label)  # set ticks

    """x축 라벨"""
    for i in tick_label:
        new_label.append(epoch_to_time(int(i)))

    axes.set_xticklabels(new_label)

    """y축 틱"""
    temp_ymax = axes.get_ylim()[1]
    temp_exp1 = np.log2(temp_ymax) // 10  # temp1 재사용
    temp_unit = int(np.log10(temp_ymax / 1024 ** temp_exp1))  # -->10단위?

    # x: 100, 10 등 단위. y는 한계 계수
    temp_ytick = [10 ** temp_unit * y * 1024 ** temp_exp1 for y in range(10) if
                  10 ** temp_unit * y * 1024 ** temp_exp1 < temp_ymax]

    axes.set_yticks(temp_ytick)

    """y축 라벨"""
    temp_list = []
    for i in temp_ytick:
        temp_list.append(
            f'{int(i / 1024 ** temp_exp1) if temp_exp1 < 3 else int(i / 1024 ** 2):,}{"BPS" if temp_exp1 == 0 else "Kbps" if temp_exp1 == 1 else "Mbps"}')

    axes.set_yticklabels(temp_list)

def show_legend():
    pos = 1
    temp_ymin = axes.get_ylim()[1] / 5
    temp1 = np.log2(temp_ymin * 5) // 10
    temp_list = []  # oid(name), BPS, avg, max
    temp_list2 = []

    # add

    # set cur/avg/max
    for i in range(COMMAND_COUNT):
        if options[i]["name"] == "":
            temp_list2.append(OID[i])
        else:
            temp_list2.append(options[i]["name"])
        temp_list2.append(f'{bps_data[i][-1] / (1024 ** (temp1)):.01f}{"BPS" if temp1 == 0 else "Kbps" if temp1 == 1 else "Mbps" if temp1 == 2 else "Gbps" if temp1 == 3 else "Tbps"}')
        temp_list2.append(f'{AVG[i] / (1024 ** (temp1)):.01f}{"BPS" if temp1 == 0 else "Kbps" if temp1 == 1 else "Mbps" if temp1 == 2 else "Gbps" if temp1 == 3 else "Tbps"}')
        temp_list2.append(f'{MAX[i] / (1024 ** (temp1)):.01f}{"BPS" if temp1 == 0 else "Kbps" if temp1 == 1 else "Mbps" if temp1 == 2 else "Gbps" if temp1 == 3 else "Tbps"}')
        temp_list.append(temp_list2)
        temp_list2 = []

    # set cur/avg/max
    for i in range(COMMAND_COUNT):
        txt = f'{temp_list[i][0]}\n'
        txt += f'cur:{temp_list[i][1]}\n'
        txt += f'avg:{temp_list[i][2]}\n'
        txt += f'max:{temp_list[i][3]}'
        legends[i] = plt.legend(handles=[plots[i]], labels=[txt], loc='upper left', bbox_to_anchor=(1, pos))
        try:
            axes.artists[i] = legends[i]
        except IndexError:
            axes.add_artist(legends[i])
        pos -= 0.3


# trim data if needed
def trim_data():
    if len(bps_data[0]) > DATA_LEN:
        np.delete(bps_data, (0), axis=1)
        np.delete(time_data, (0), axis=1)


# ==============defining plot================================
# current time
CurrentTime = time.time()
# for timer
timer_start = CurrentTime

# set plot
fig = plt.figure()
fig.canvas.mpl_connect('close_event', handle_close)

axes = plt.axes()
axes.set_xlim([CurrentTime - HOUR * VIEW_HOUR, CurrentTime])
axes.set_ylim([0, 100])

plt.ion()  # enable update
plt.xticks(rotation=45)
plt.grid(True, color='gray', alpha=0.5, linestyle='--')
fig.canvas.set_window_title(WINDOW_TITLE)

# show graph first
plt.tight_layout()
plt.show()

# before starting, get value first
for i in range(COMMAND_COUNT):
    first_value[i] = get_value(commands[i])
    second_value[i] = first_value[i]


# make graph first
for i in range(COMMAND_COUNT):
    # add to list for legend
    plots[i], = plt.plot(time_data[i], bps_data[i], color=options[i]["color"], label=OID[i])#, animated=True)
    # TODO cpu problem
    # if options[i]["fill"] == "True":
    #     plt.fill_between(time_data[i], bps_data[i], facecolor=options[i]["color"])

# stop to admire our empty window axes and ensure it is rendered at
# least once.
#
# We need to fully draw the figure at its final size on the screen
# before we continue on so that :
#  a) we have the correctly sized and drawn background to grab
#  b) we have a cached renderer so that ``ax.draw_artist`` works
# so we spin the event loop to let the backend process any pending operations
plt.pause(0.1)

# get copy of entire figure (everything inside fig.bbox) sans animated artist
bg = fig.canvas.copy_from_bbox(fig.bbox)
# draw the animated artist, this uses a cached renderer
for i in range(COMMAND_COUNT):
    axes.draw_artist(plots[i])
# show the result to the screen, this pushes the updated RGBA buffer from the
# renderer to the GUI framework so you can see it
fig.canvas.blit(fig.bbox)

while active:
    # reset the background back in the canvas state, screen unchanged
    fig.canvas.restore_region(bg)

    # (very first) current time
    CurrentTime = time.time()

    # first, get value
    for i in range(COMMAND_COUNT):
        # assign first
        first_value[i] = get_value(commands[i])

        # check for error
        # if not first_value[i]:
        #     print("error")
        #     active = False
        #     break

        # add data to temp after subtraction
        np_temp_dictionary["bps_data"].append([first_value[i] - second_value[i]])
        # test: print(f"first:{first_value[i]}, second:{second_value[i]}....so{first_value[i] - second_value[i]}")
        # assign first value to second one
        second_value[i] = first_value[i]

        # get time
        np_temp_dictionary["time_data"].append([CurrentTime])


    # append np
    bps_data = np.append(bps_data, np.array(np_temp_dictionary["bps_data"]), axis=1)
    time_data = np.append(time_data, np.array(np_temp_dictionary["time_data"]), axis=1)

    # trim np if needed
    trim_data()

    # reset np_temp_dictionary
    np_temp_dictionary["bps_data"].clear()
    np_temp_dictionary["time_data"].clear()

    # calc max and avg
    for i in range(COMMAND_COUNT):
        AVG[i] = np.average(bps_data[i])
        MAX[i] = np.max(bps_data[i])

    # set limit (plot)
    axes.set_xlim([CurrentTime - HOUR * VIEW_HOUR, CurrentTime])
    axes.set_ylim([0, np.max(bps_data) + np.max(bps_data) * 0.1])

    # set axes label
    set_axes_label()

    # set legend
    show_legend()

    # adjust layout
    plt.tight_layout()

    # ==============handle events and update========================================
    # draw plots
    for i in range(COMMAND_COUNT):
        # add to list for legend
        plots[i].set_data(time_data[i], bps_data[i])
        plots[i].set_linewidth(USER_LINE_THICKNESS)
        # TODO cpu problem
        # if options[i]["fill"] == "True":
        #     plt.fill_between(time_data[i], bps_data[i], facecolor=options[i]["color"])

    # update the artist, neither the canvas state nor the screen have changed
    # re-render the artist, updating the canvas state, but not the screen
    for i in range(COMMAND_COUNT):
        axes.draw_artist(plots[i])
    # copy the image to the GUI state, but screen might not changed yet
    fig.canvas.blit(fig.bbox)

    plt.pause(UPDATE_DELAY)  # THANK GOD I FOUND THIS FUNCTION NO MORE WORRIES ABOUT SPEED
