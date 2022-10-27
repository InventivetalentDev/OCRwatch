from ocr import process_screenshot_file
from output import write_to_influx, write_output

result = process_screenshot_file("d0db55a1bb_Overwatch.jpg")
print(result)

write_output(result)