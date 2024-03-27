import colorsys
import math
import os
from PIL import Image, ImageDraw

TWELFTH_ROOT_TWO = 1.05946309436

HEADERS = "Name,Ratio,Cents"
JI_LIMIT = 7
EDO_RANGE = range(5, 48 + 1)

def fmt(n, precision):
    return f"{n:.{precision}f}".rstrip("0").rstrip(".")

def edo_name(n):
    return f"{n}-EDO"

class Interval:
    def __init__(self, name, ratio):
        self.name = name
        self.ratio = ratio
        self.cents = 100 * math.log(ratio, TWELFTH_ROOT_TWO)
        return

    def to_csv(self):
        return f"{self.name},{fmt(self.ratio, 4)},{fmt(self.cents, 2)}"

def get_JI(limit):
    arr = []
    arr.append(Interval(name="1/1", ratio=1))
    arr.append(Interval(name="2/1", ratio=2))
    for d in range(1, limit + 1):
        for n in range(1, d):
            gcd = math.gcd(n, d)
            if gcd == 1:
                n = n + d
                entry = Interval(
                    name=f"{n}/{d}",
                    ratio=n / d
                )
                arr.append(entry)
    return arr

def get_EDO(divisions):
    arr = []
    for i in range(1, divisions):
        entry = Interval(
            name=f"{divisions}-EDO °{i}",
            ratio=math.pow(2, i / divisions)
        )
        arr.append(entry)
    return arr

# Add the data
ji_intervals = get_JI(7)
ji_intervals.sort(key=lambda interval: interval.cents)

edo_data = {}
for n in EDO_RANGE:
    edo_data[edo_name(n)] = get_EDO(n)

# Write the CSVs
try:
    os.makedirs("./csv")
except:
    None

ji_table = f"{HEADERS}\n"
for interval in ji_intervals:
    ji_table += f"{interval.to_csv()}\n"

file = open("./csv/JI.csv", "w")
file.write(ji_table)
file.close()

for temperament_name, intervals in edo_data.items():
    edo_table = f"{HEADERS}\n"
    for interval in intervals:
        edo_table += f"{interval.to_csv()}\n"
    file = open(f"./csv/{temperament_name}.csv", "w")
    file.write(edo_table)
    file.close()

# Make the image
EDO_BLOCK_SIZE = 40

height = EDO_BLOCK_SIZE * (len(EDO_RANGE) + 1)
img = Image.new('RGB', (1200, height), (0, 0, 0))
draw = ImageDraw.Draw(img)

for i, (temperament_name, intervals) in enumerate(edo_data.items()):
    y_bot = (i + 1) * EDO_BLOCK_SIZE
    y_top = (i + 2) * EDO_BLOCK_SIZE
    draw.rectangle(
        xy=[(0, y_bot), (1200, y_top)],
        fill=(0, 0, 0) if i % 2 == 0 else (15, 15, 20)
    )
    draw.line(
        xy=[(0, y_bot), (1200, y_bot)],
        fill=(255, 255, 255),
        width=1
    )
    for degree, interval in enumerate(intervals):
        draw.line(
            xy=[(interval.cents, y_bot), (interval.cents, y_top)],
            fill=(255, 255, 255),
            width=1
        )
        draw.text(
            xy=(interval.cents - 8, (y_bot + y_top) / 2),
            text=f"{degree + 1}",
            fill=(255, 255, 255),
            anchor="mm",
            stroke_width=0,
            font_size=10
        )
    draw.text(
        xy=(1200 - 8, (y_bot + y_top) / 2),
        text=f"{len(intervals) + 1}",
        fill=(255, 255, 255),
        anchor="mm",
        stroke_width=0,
        font_size=10
    )

for i, interval in enumerate(ji_intervals):
    if interval.ratio == 1 or interval.ratio == 2:
        continue
    hsv = colorsys.hsv_to_rgb((interval.ratio - 1) * 1.1, 0.8, 0.8)
    fill = (int(255 * hsv[0]), int(255 * hsv[1]), int(255 * hsv[2]))
    draw.line(
        xy=[(interval.cents, EDO_BLOCK_SIZE), (interval.cents, height)],
        fill=fill,
        width=2
    )
    draw.text(
        xy=(interval.cents, EDO_BLOCK_SIZE - 12 if i % 2 == 0 else 12),
        text=f"{interval.name}",
        fill=fill,
        anchor="mm",
        stroke_width=0,
        font_size=14
    )

# Save the image
try:
    os.makedirs("./img")
except:
    None

img.save("./img/edo-ji-chart.png")

# Done
print("done!")
