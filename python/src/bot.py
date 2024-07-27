from typing import List, Union
from core.action import MoveAction, ShootAction, RotateBladeAction, SwitchWeaponAction, SaveAction
from core.consts import Consts
from core.game_state import GameState, PlayerWeapon, Point
from core.map_state import MapState
import math
import heapq
import numpy as np
from scipy.optimize import fsolve
import keyboard

class Cell:
    def __init__(self) -> None:
        self.walls = [False, False, False, False]  # [top, right, bottom, left]

class Map:
    def __init__(self) -> None:
        self.size = 10
        self.grid = [[Cell() for _ in range(self.size)] for _ in range(self.size)]

    def place_wall(self, x, y, direction):
        if x < 0 or x >= self.size or y < 0 or y >= self.size:
            print("Invalid cell coordinates")
            return

        if direction not in ["top", "right", "bottom", "left"]:
            print("Invalid direction. Use 'top', 'right', 'bottom', or 'left'")
            return

        directions = ["top", "right", "bottom", "left"]
        dir_index = directions.index(direction)

        # Place wall in the current cell
        self.grid[y][x].walls[dir_index] = True

        # Place wall in the adjacent cell
        adj_x, adj_y = x, y
        adj_dir_index = (dir_index + 2) % 4  # Opposite direction

        if direction == "top":
            adj_y -= 1
        elif direction == "right":
            adj_x += 1
        elif direction == "bottom":
            adj_y += 1
        elif direction == "left":
            adj_x -= 1

        # Check if adjacent cell is within the grid
        if 0 <= adj_x < self.size and 0 <= adj_y < self.size:
            self.grid[adj_y][adj_x].walls[adj_dir_index] = True

    def print_map(self):
        for row in self.grid:
            for cell in row:
                print(f"[{''.join('W' if w else ' ' for w in cell.walls)}]", end="")
            print()

class MyBot:
    def __init__(self):
        self.name = "ChevyMalibu2010"  # 10 characters
        self.__map_state = None
        self.map = Map()
        self.initialize = True
        self.move_speed = 10  # Adjust this value as needed

    def currentCell(self, location):
        x, y = location[0], location[1]
        cell_x = int(x // 10)
        cell_y = int(y // 10)
        return (cell_x, cell_y)

    def getWall(self, current_location):
        current_cell = self.currentCell(current_location)
        x, y = current_location

        # Calculate distances to cell boundaries
        distances = {
            "top": y % 10,
            "bottom": 10 - (y % 10),
            "left": x % 10,
            "right": 10 - (x % 10)
        }

        # Find the closest wall
        closest_wall = min(distances, key=distances.get)

        # Map the direction to the corresponding index in the Cell.walls list
        direction_to_index = {"top": 0, "right": 1, "bottom": 2, "left": 3}
        wall_index = direction_to_index[closest_wall]

        # Place the wall in the map
        self.map.place_wall(int(current_cell[0]), int(current_cell[1]), closest_wall)

        print(f"Closest wall: {closest_wall}")
        print(f"Current location: {current_location}")
        print(f"Current cell: {current_cell}")
        self.map.print_map()
        return closest_wall

    def on_tick(self, game_state: GameState) -> List[Union[MoveAction, SwitchWeaponAction, RotateBladeAction, ShootAction, SaveAction]]:
        actions = []
        mystate = next((player for player in game_state.players if player.name == self.name), None)

        if not mystate:
            return actions

        if self.initialize:
            actions.append(SwitchWeaponAction(PlayerWeapon.PlayerWeaponCanon))
            self.initialize = False

        # Shooting logic
        us = self.name_search(game_state.players, "ChevyMalibu2010")
        a = self.find_nearest_enemy(game_state.players, "ChevyMalibu2010")

        target_vel = [a.dest.x - a.pos.x, a.dest.y - a.pos.y]
        target_vel = [Consts.Player.SPEED/self.distance((0,0), (target_vel[0], target_vel[1]))*target_vel[0], 
                      Consts.Player.SPEED/self.distance((0,0), (target_vel[0], target_vel[1]))*target_vel[1]]

        predicted_position = self.predict(us.pos, a.pos, target_vel)
        actions.append(ShootAction(predicted_position))

        # Movement logic
        current_x, current_y = mystate.pos.x, mystate.pos.y
        move_x, move_y = 0, 0

        if keyboard.is_pressed('w'):
            move_y -= self.move_speed
        if keyboard.is_pressed('s'):
            move_y += self.move_speed
        if keyboard.is_pressed('a'):
            move_x -= self.move_speed
        if keyboard.is_pressed('d'):
            move_x += self.move_speed

        if move_x != 0 or move_y != 0:
            new_x = current_x + move_x
            new_y = current_y + move_y
            actions.append(MoveAction((new_x, new_y)))

        return actions

    def on_start(self, map_state: MapState):
        self.__map_state = map_state
        print(map_state)

    def createPoint(self, location: Point):
        return (round(location.x, 2), round(location.y, 2))

    def on_end(self):
        pass

    def find_nearest_coin(self, coins, our_position):
        return min(coins, key=lambda coin: self.distance(coin.position, our_position), default=None)

    def nearestcoin(self, pos, coins):
        index = 0
        smallestindex = 0
        shortestdistance = 100000
        distance = 0

        for coin in coins:
            coinlocation = self.createPoint(coin.pos)
            distance = self.distance(coinlocation, pos)

            if distance < shortestdistance:
                shortestdistance = distance
                smallestindex = index
            index += 1

        cell = self.currentCell(self.createPoint(coins[smallestindex].pos))
        location = self.createPoint(coins[smallestindex].pos)

        return cell, location

    def distance(self, tuple1, tuple2):
        return ((tuple1[0] - tuple2[0])**2 + (tuple1[1] - tuple2[1])**2)**0.5

    def find_nearest_enemy(self, players, our_name):
        name_closest_bot = ""
        smallest_distance = float('inf')

        my_pos = self.name_search(players, our_name).pos

        for player in players:
            if player.name != our_name:
                curr_distance = self.distance((my_pos.x, my_pos.y), (player.pos.x, player.pos.y))

                if curr_distance < smallest_distance:
                    smallest_distance = curr_distance
                    name_closest_bot = player.name

        target = self.name_search(players, name_closest_bot)

        return target

    def name_search(self, players, name):
        for player in players:
            if player.name == name:
                return player
        return None

    def predict(self, my_pos, target_pos, target_vel):
        def equations(t):
            x = target_pos.x + target_vel[0] * t
            y = target_pos.y + target_vel[1] * t
            d = np.sqrt((x - my_pos.x) ** 2 + (y - my_pos.y) ** 2)
            return d - Consts.Projectile.SPEED * t

        t_solution = fsolve(equations, 0)[0]

        x_intercept = target_pos.x + target_vel[0] * t_solution
        y_intercept = target_pos.y + target_vel[1] * t_solution

        return [x_intercept, y_intercept]