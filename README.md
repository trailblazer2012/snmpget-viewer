# Snmp 트래픽 뷰어  v1.0
##### _by. JS_
## 사용법
**사용전 필요한 것**

`snmpget.exe` 이 있어야 하고 또는 프로그램의 반환 값의 형식이 아래와 같은 것이 있어야 합니다.
```commandline
...
OID=.1.3.6.1.2.1.31.1.1.1.10.436207616
Value=0x12857D29A9F95
...
```


**config.txt 사용법**

그래프 옵션주기:
- ?color=(색)
- ~~?fill=(True || False) (현재 지원하지 않는 기능입니다)~~
- ?name=(고유 이름, OID 대신 보여줄 이름)

_글씨를 붙혀써야 하고, 옵션 사이는 공백으로 구분해 주어야 합니다._

명령어는 옵션 뒤에 한칸 뛰고 쓰면 됩니다.

예시:
~~~commandline
?color=green ?name=IN ./snmpget.exe -r:___ -c:"___" -v:__ -o:____________
~~~

<br>

**main.py 사용법**

~~~python
...
# user-const
VIEW_HOUR = 0.1  # 소수점 값이 들어가면 정확한 눈금이 안 나올 수도 있음
UPDATE_DELAY = 1
USER_X_TICK = 5  # min 단위
USER_LINE_THICKNESS = 1
WINDOW_TITLE = "snmp get"
bps = True  # which means Bps=False
...
~~~
이 부분을 수정하면 됩니다.

- VIEW_HOUR: x축 전체 시간
- UPDATE_DELAY:업데이트 주기
- USER_X_TICK:x축 눈금 단위(분 기준)
- USER_LINE_THICKNESS:선 두께 (1이하를 추천, 소수이여도 괜찮음)
- WINDOW_TITLE:창 제목
- bps: 단위를 bps로 할지, Bps로 할지 정하는 변수

## 참고사항
- 그림을 그리는 과정에서 소요되는 시간이 추가로 추가되어서 업데이트 주기는 실제보다 길 수도 있습니다.
- 화면 크기를 바꿀시 업데이트 주기만큼의 시간이 지난 후에 그래프가 화면을 채우게 됩니다.
- 종료시 루프에서 탈출하는데 업데이트 주기만큼의 시간이 추가로 걸립니다.
- 처음 그래프가 생길 때는 범주 부분이 안 보일 수 있지만, **업데이트 주기를 지나고 나면** 현재크기에 딱 맞게 조정됩니다.

## 사용전 다운로드가 필요한 패키지 목록
- matplotlib-pyplot
    - `pip install matplotlib` 로 설치가 가능합니다.
    