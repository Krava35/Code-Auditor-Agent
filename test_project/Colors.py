class Colors(object):
    def __init__(self):
        self.grey = "\033[90m{}\033[0m"
        self.green2 = "\033[32m{}\033[0m"
        self.red = "\033[91m{}\033[0m"
        self.green = "\033[92m{}\033[0m"
        self.yellow = "\033[93m{}\033[0m"
        self.blue = "\033[94m{}\033[0m"
        self.pink = "\033[95m{}\033[0m"
        self.beige = "\033[96m{}\033[0m"
        self.red2 = "\033[31m{}\033[0m"

    def set_grey(self, text):
        return self.grey.format(text)

    def set_green2(self, text):
        return self.green2.format(text)

    def set_red(self, text):
        return self.red.format(text)

    def set_green(self, text):
        return self.green.format(text)

    def set_yellow(self, text):
        return self.yellow.format(text)

    def set_blue(self, text):
        return self.blue.format(text)

    def set_pink(self, text):
        return self.pink.format(text)

    def set_beige(self, text):
        return self.beige.format(text)

    def set_red2(self, text):
        return self.red2.format(text)
