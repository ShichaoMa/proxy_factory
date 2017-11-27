import pytesseract

from PIL import Image
from io import BytesIO

from functools import wraps, reduce


def parse_class(cls):
    """
    隐藏的解码函数
    :param cls:
    :return:
    """
    meta = dict(zip("ABCDEFGHIZ", range(10)))
    num = reduce(lambda x, y: x + str(meta.get(y)), cls, "")
    return int(num) >> 3


def parse_port(buffer):
    with Image.open(BytesIO(buffer)) as image:
        image = image.convert("RGB")
        gray_image = Image.new('1', image.size)
        width, height = image.size
        raw_data = image.load()
        image.close()
        for x in range(width):
            for y in range(height):
                value = raw_data[x, y]
                value = value[0] if isinstance(value, tuple) else value
                if value < 1:
                    gray_image.putpixel((x, y), 0)
                else:
                    gray_image.putpixel((x, y), 255)
        num = pytesseract.image_to_string(gray_image)
        result = guess(num)
        if result:
            return result
        else:
            new_char = list()
            for i in num:
                if i.isdigit():
                    new_char.append(i)
                else:
                    new_char.append(guess(i))
            return "".join(new_char)


def guess(word):
    try:
        mapping = {
            "b": "8",
            "o": "0",
            "e": "8",
            "s": "9",
            "a": "9",
            "51234": "61234",
            "3737": "9797",
            "3000": "9000",
            "52385": "62386",
        }
        return mapping[word.lower()]
    except KeyError:
        if len(word) == 1:
            print(word)
            return word


def exception_wrapper(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        try:
            return func(*args, **kwargs)
        except Exception as e:
            self.logger.warn("failed in %s: %s" % (func.__name__, e))
            return set()

    return wrapper
