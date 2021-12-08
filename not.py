from PIL import Image, ImageDraw
import time

start_time = time.time()

tex_size = 512
img = Image.new('RGB', (tex_size, tex_size), color='black')

draw = ImageDraw.Draw(img)

for i in range(100):
    draw.polygon([(20 + i*2, 20), (0, 30), (100, 100)], fill=(255, 0, 0))

img.save("test.png")

print("--- %s seconds ---" % (time.time() - start_time))

# with Image.open("test.jpg") as im:
# im.rotate(90).show()
