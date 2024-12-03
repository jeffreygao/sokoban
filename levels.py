# 推箱子游戏关卡定义

LEVELS = [
    # Level 1 - Tutorial (1箱子，1目标)
    [
        "##########",
        "#   @    #",
        "#  $     #",
        "#   .    #",
        "##########"
    ],
    # Level 2 (2箱子，2目标)
    [
        "############",
        "#    .     #",
        "#  @$ .    #",
        "#    #     #",
        "#   $      #",
        "############"
    ],
    # Level 3 (3箱子，3目标)
    [
        "############",
        "#    .    .#",
        "#  @ $ $   #",
        "#    #  .  #",
        "#   $      #",
        "############"
    ],
    # Level 4 (3箱子，3目标)
    [
        "#############",
        "#     #     #",
        "#   $ . .   #",
        "# @  ###    #",
        "#   $ .     #",
        "#   $       #",
        "#############"
    ],
    # Level 5 (4箱子，4目标)
    [
        "##############",
        "#   #    #   #",
        "#   $  $ # @ #",
        "#   #$ $ #   #",
        "# . . . .$   #",
        "##############"
    ],
    # Level 6 (4箱子，4目标)
    [
        "##############",
        "#      . . . #",
        "#  $ $ ###   #",
        "#   @$       #",
        "#  $ $     . #",
        "#            #",
        "##############"
    ],
    # Level 7 - 移动逻辑测试关卡
    [
        "###############",
        "#   #   #     #",
        "# @ $   $  .  #",
        "#   #   #  .  #",
        "#   $   #     #",
        "#   #   #     #",
        "###############"
    ],
    # Level 8 (6箱子，6目标)
    [
        "###############",
        "#  .  #  .  . #",
        "# $ $ # $ $   #",
        "#  #   @  #   #",
        "# $ $ # $ $   #",
        "#  .  #  .  . #",
        "###############"
    ],
    # Level 9 (6箱子，6目标)
    [
        "###############",
        "#      . . .  #",
        "#  $ $ ###    #",
        "#  $ @ $ #    #",
        "#  $ $ # #    #",
        "#  . . .      #",
        "###############"
    ],
    # Level 10 (6箱子，6目标)
    [
        "################",
        "#   #   #   #  #",
        "# $   $   $    #",
        "#  . . . .     #",
        "#   # @ #      #",
        "#  . . .       #",
        "# $   $   $    #",
        "################"
    ]
]

# 更新关卡元数据
LEVEL_DATA = [
    {
        'name': '教程',
        'par_moves': 10,
        'par_pushes': 4
    },
    {
        'name': '基础',
        'par_moves': 15,
        'par_pushes': 6
    },
    {
        'name': '双重麻烦',
        'par_moves': 20,
        'par_pushes': 8
    },
    {
        'name': '三重挑战',
        'par_moves': 25,
        'par_pushes': 10
    },
    {
        'name': '进阶路径',
        'par_moves': 30,
        'par_pushes': 12
    },
    {
        'name': '智者之路',
        'par_moves': 35,
        'par_pushes': 14
    },
    {
        'name': '移动逻辑测试',
        'par_moves': 40,
        'par_pushes': 16
    },
    {
        'name': '大师课程',
        'par_moves': 45,
        'par_pushes': 18
    },
    {
        'name': '宗师之境',
        'par_moves': 50,
        'par_pushes': 20
    },
    {
        'name': '传说',
        'par_moves': 55,
        'par_pushes': 22
    }
]
