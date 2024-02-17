import math

def distance(point1, point2):
    return math.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)

def is_right_angle(side1, side2, hypotenuse):
    return abs(side1**2 + side2**2 - hypotenuse**2) < 1000

def is_right_triangle(points):
    print(points)
    # Compute the lengths of the three sides

    side1 = distance(points[0], points[1])
    side2 = distance(points[1], points[2])
    side3 = distance(points[2], points[0])
    
    # Check if any angle is 90 degrees
    if is_right_angle(side1, side2, side3) or \
       is_right_angle(side2, side3, side1) or \
       is_right_angle(side3, side1, side2):
        return True
    else:
        return False
