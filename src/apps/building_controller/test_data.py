from datetime import datetime

from apps.building_controller.models import Floor, BuildingEntryPoint, StairCase, Building

expected_floor_th0_0 = Floor(0, [[16, 19]])
expected_floor_th0_1 = Floor(1, [[14, 19]])
expected_floor_th0_2 = Floor(2, [[14, 19]])
expected_floor_th0_3 = Floor(3, [[14, 19]])
expected_floor_th1_0 = Floor(-1, [[0, 19]])
expected_floor_th1_1 = Floor(0, [[0, 13], [20, 21]])
expected_floor_th1_2 = Floor(1, [[0, 13], [20, 21]])
expected_floor_th1_3 = Floor(2, [[0, 13], [20, 21]])
expected_floor_th1_4 = Floor(3, [[0, 13], [20, 21]])
entry_point_th0_0 = BuildingEntryPoint({
    "coord": [
        10.883620977401733,
        49.89582315312931
    ]
})
entry_point_th1_0 = BuildingEntryPoint({
    "coord": [
        10.88393747806549,
        49.89569874965762
    ]
}, )
entry_point_th1_1 = BuildingEntryPoint({
    "coord": [
        10.883757770061493,
        49.895605446843355
    ]
}, )
entry_point_th1_0_wheelchair = BuildingEntryPoint({
    "wheelchair": True,
    "coord": [
        10.88393747806549,
        49.89569874965762
    ]
}, )
entry_point_th1_1_wheelchair = BuildingEntryPoint({
    "wheelchair": False,
    "coord": [
        10.883757770061493,
        49.895605446843355
    ]
}, )
entry_point_th1_0_blocked = BuildingEntryPoint({
    "blocked": "3000-12-12",
    "coord": [
        10.88393747806549,
        49.89569874965762
    ]
}, )
entry_point_th1_1_blocked = BuildingEntryPoint({
    "blocked": "3000-12-12",
    "coord": [
        10.883757770061493,
        49.895605446843355
    ]
}, )
expected_staircase_1 = StairCase(1,
                                 "Turm",
                                 [expected_floor_th0_0, expected_floor_th0_1, expected_floor_th0_2,
                                  expected_floor_th0_3],
                                 [10.883663892745972, 49.89579550794111],
                                 [entry_point_th0_0],
                                 neighbours=[2])
expected_staircase_2 = StairCase(2,
                                 "Haupttreppe",
                                 [expected_floor_th1_0, expected_floor_th1_1, expected_floor_th1_2,
                                  expected_floor_th1_3, expected_floor_th1_4],
                                 [10.883814096450806, 49.89561235816914],
                                 [entry_point_th1_0, entry_point_th1_1],
                                 neighbours=[1])
expected_staircase_2_wheelchair = StairCase(2,
                                            "Haupttreppe",
                                            [expected_floor_th1_0, expected_floor_th1_1, expected_floor_th1_2,
                                             expected_floor_th1_3, expected_floor_th1_4],
                                            [10.883814096450806, 49.89561235816914],
                                            [entry_point_th1_0_wheelchair, entry_point_th1_1_wheelchair],
                                            neighbours=[1],
                                            wheelchair=True)
expected_staircase_2_blocked_staircase = StairCase(2,
                                                   "Haupttreppe",
                                                   [expected_floor_th1_0, expected_floor_th1_1, expected_floor_th1_2,
                                                    expected_floor_th1_3, expected_floor_th1_4],
                                                   [10.883814096450806, 49.89561235816914],
                                                   [entry_point_th1_0, entry_point_th1_1],
                                                   neighbours=[1],
                                                   blocked=datetime.strptime("3000-12-12", "%Y-%m-%d"))
expected_staircase_2_blocked_entries = StairCase(2,
                                                 "Haupttreppe",
                                                 [expected_floor_th1_0, expected_floor_th1_1, expected_floor_th1_2,
                                                  expected_floor_th1_3, expected_floor_th1_4],
                                                 [10.883814096450806, 49.89561235816914],
                                                 [entry_point_th1_0_blocked, entry_point_th1_1_blocked],
                                                 neighbours=[1],
                                                 )
expected_building_no_props = Building("M3", [expected_staircase_1, expected_staircase_2])
expected_building_wheelchair = Building("M3", [expected_staircase_1, expected_staircase_2_wheelchair])
expected_building_blocked_staircase= Building("M3", [expected_staircase_1, expected_staircase_2_blocked_staircase])
expected_building_blocked_entries = Building("M3", [expected_staircase_1, expected_staircase_2_blocked_entries])
