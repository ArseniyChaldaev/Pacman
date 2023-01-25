import os


class Level:
    def __init__(self):
        self.map = None
        self.num = 0
        self.food_count = 0
        self.next_level()

    def next_level(self):
        self.num += 1
        fullname = os.path.join('data', f'levels/{self.num}.txt')
        if os.path.exists(fullname):
            with open(fullname, 'r') as level_file:
                self.map = [list(map(int, list(line.strip()))) for line in level_file.readlines()]
            self.food_count = sum(line.count(1) for line in self.map)
            return True
        else:
            self.map = []
            self.food_count = 0
            return False

    def reset(self):
        self.num = 0
        self.next_level()
