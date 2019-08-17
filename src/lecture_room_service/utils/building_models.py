from typing import List

from building_controller.utils.univis_models import Room
from lector.utils.open_space_models import EntryPoint





# class Building:
#     def __init__(self, key, staircases: List[StairCase]):
#         self.key = key
#         self.staircases = staircases
#
#     def get_rooms_staircase(self, room: Room):
#         for staircase in self.staircases:
#             if room in staircase.rooms:
#                 return staircase
#         return None
#
#     def __str__(self):
#         output = f'Building {self.key}\n'
#         for staircase in self.staircases:
#             output += f'{staircase}\n'
#         return output


