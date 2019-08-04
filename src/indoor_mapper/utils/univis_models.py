class MinimalRoom:
    def __init__(self, building_key, level, number):
        self.building_key = building_key
        self.number = number
        self.level = level


class Room:
    def __init__(self, univis_room):
        self.building_key = None
        self.number = None
        self.level = None
        self._init_room_number(univis_room)

    def _init_room_number(self, univis_room):
        splitted_room_id = str(univis_room['short']).split('/')
        splitted_room_number = splitted_room_id[1].split('.')
        self.building_key = splitted_room_id[0]
        self.level = int(splitted_room_number[0])
        self.number = int(splitted_room_number[1])

    def __str__(self):
        return f'{self.building_key}/{self.level:02d}.{self.number:03d}'
