from ocr import process_screenshot_file
from output import write_to_influx

result = process_screenshot_file("f0ede0d25f_Overwatch.png")
print(result)

write_to_influx(result)