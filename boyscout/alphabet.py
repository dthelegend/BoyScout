
alphabet = [ #X = LEFT, Y = RIGHT
    #000-045-090-135-180-225-270-315
    ['-','-','-','-','-','K','P','T'], ### 000
    ['-','-','W','-','E','L','Q','U'], ### 045
    ['J','-','X','Z','F','M','R','Y'], ### 090
    ['V','-','-','-','G','N','S','-'], ### 135
    ['D','-','-','-','-','A','B','C'], ### 180
    ['-','-','-','-','-','-','-','I'], ### 225
    ['-','-','-','-','-','H','-','-'], ### 270
    ['-','-','-','-','-','-','O','-']  ### 315
]


def getLetter(leftAngle, rightAngle):
    left = round(leftAngle/45)
    right = round(rightAngle/45)

    if left == 8:
        left = 0
    if right == 8:
        right = 0

    return alphabet[left][right]