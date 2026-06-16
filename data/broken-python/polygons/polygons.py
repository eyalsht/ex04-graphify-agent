import turtle


class Polygon(object):

    def __init__(self, sides, internal_angles_sum, internal_angle):
        self.sides = sides
        self.internal_angles_sum = internal_angles_sum
        self.internal_angle = internal_angle


# calculate the total internal angles, and the angles within
# a regular version of the polygon
def calc_polygon_details(sides):

    if sides < 3:
        raise ValueError(f"a polygon needs at least 3 sides, got {sides}")

    internal_angles_sum = (sides - 2) * 180
    internal_angle = internal_angles_sum / sides

    poly = Polygon(sides, internal_angles_sum, internal_angle)

    return poly


# draws a polygon using the turtle
def draw_polygon(polygon):

    # set up the screen and turtle
    scr = turtle.Screen()
    t = turtle.Turtle()
    t.pen(pencolor="red", pensize=2, fillcolor="green")

    length_of_edge = 50

    for i in range(0, polygon.sides):
        t.forward(length_of_edge)
        t.right(360 / polygon.sides)


sides = int(input("How many sides does your polygon have?: "))

polygon = calc_polygon_details(sides)

print("    Sides:", polygon.sides)
print("    Internal angles sum:", polygon.internal_angles_sum)
print("    Internal angle:", polygon.internal_angle)

draw = input("Would you like me to draw it? (Y/n): ")

if draw == "" or draw.lower() == "y":
    draw_polygon(polygon)
