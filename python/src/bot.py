from typing import List, Union
from core.action import MoveAction, ShootAction, RotateBladeAction, SwitchWeaponAction, SaveAction
from core.consts import Consts
from core.game_state import GameState, PlayerWeapon, Point
from core.map_state import MapState
import math
import heapq


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
            print(cell)

class MyBot:

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

    def __init__(self):
        self.name = "ChevyMalibu2010"  # 10 characters
        self.__map_state = None
        self.path = []
        self.mapstate = []
        self.lastposition = (0,0)
        self.directions = [(100,0),(0,-100),(-100,0),(0,100)]
        self.directioncount = 0
        self.moving = False
        self.map = Map()
        self.oncookie = False



    
        
    def on_tick(self, game_state: GameState) -> List[Union[MoveAction, SwitchWeaponAction, RotateBladeAction, ShootAction, SaveAction]]:
        actions = []
        mystate = next((player for player in game_state.players if player.name == self.name), None)
        
        if not mystate:
            return actions

        playercoord = mystate.pos
        currentlocation = self.createPoint(playercoord)
        closestcookie = self.nearestcoin(currentlocation,list(game_state.coins))
        cookiecell,cookielocation = closestcookie
        currentcell = self.currentCell(currentlocation)

        if currentlocation == self.lastposition and self.moving and self.oncookie is False:
            # ADD WALL logic here if needed
            self.directioncount = (self.directioncount + 1) % 4
            # print(f"WALL encountered. New direction: {self.directioncount}")
            self.getWall(currentlocation)
            self.moving = False
        elif currentlocation == self.lastposition and self.moving:
            dx, dy = self.directions[self.directioncount]
            destination = (currentlocation[0] + dx, currentlocation[1] + dy)
            self.moving = True    
            actions.append(MoveAction(destination))
    
        if cookiecell == currentcell:
            
            actions.append(MoveAction(cookielocation))
            self.oncookie = True
            



        if not self.moving:
            dx, dy = self.directions[self.directioncount]
            destination = (currentlocation[0] + dx, currentlocation[1] + dy)
            self.moving = True    
            actions.append(MoveAction(destination))

        # print(f"Current location: {currentlocation}")
        # print(f"Destination: {mystate.dest}")
        
        self.lastposition = currentlocation
        return actions

    def on_start(self, map_state: MapState):
        self.__map_state = map_state
        print(map_state)

    def createPoint(self,location: Point):
        return (round(location.x,2),round(location.y,2))
    


    def on_end(self):
        pass
    def find_nearest_coin(self, coins, our_position):
        return min(coins, key=lambda coin: self.distance(coin.position, our_position), default=None)

    def nearestcoin(self, pos, coins):
        index=0
        smallestindex = 0
        shortestdistance = 100000
        distance = 0

        for coin in coins: 
            coinlocation = self.createPoint(coin.pos)
            distance = self.distance(coinlocation,pos)

            if distance < shortestdistance:
                shortestdistance=distance
                smallestindex=index
            index+=1
            

        cell = self.currentCell(self.createPoint(coins[smallestindex].pos))
        location = self.createPoint(coins[smallestindex].pos)
            
        return cell, location
            
    def distance(self, tuple1, tuple2):
        return ((tuple1[0] - tuple2[0])**2 + (tuple1[1] - tuple2[1])**2)**0.5

    