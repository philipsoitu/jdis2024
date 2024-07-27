from typing import List, Union
from core.action import MoveAction, ShootAction, RotateBladeAction, SwitchWeaponAction, SaveAction
from core.consts import Consts
from core.game_state import GameState, PlayerWeapon, Point
from core.map_state import MapState
import math
import heapq


class Cell:
    def __init__(self) -> None:
        
        self.up = False
        self.down = False
        self.left = False
        self.right = False


class MyBot:
    def __init__(self):
        self.name = "ChevyMalibu2010"  # 10 characters
        self.__map_state = None
        self.path = []
        self.mapstate = []
        self.lastposition = (0,0)
        self.directions = [(100,0),(0,-100),(-100,0),(0,100)]
        self.directioncount = 0
        self.moving = False



    
        
    def on_tick(self, game_state: GameState) -> List[Union[MoveAction, SwitchWeaponAction, RotateBladeAction, ShootAction, SaveAction]]:
        actions = []
        mystate = next((player for player in game_state.players if player.name == self.name), None)
        
        if not mystate:
            return actions

        playercoord = mystate.pos
        currentlocation = self.createPoint(playercoord)
        nearestcookiecell = self.find_nearest_coin()

        if currentlocation == self.lastposition and self.moving:
            # ADD WALL logic here if needed
            self.directioncount = (self.directioncount + 1) % 4
            print(f"WALL encountered. New direction: {self.directioncount}")
            currentcell = self.currentCell(currentlocation)
            print(currentcell)
            self.moving = False

        if not self.moving:
            dx, dy = self.directions[self.directioncount]
            destination = (currentlocation[0] + dx, currentlocation[1] + dy)
            self.moving = True    
            actions.append(MoveAction(destination))

        print(f"Current location: {currentlocation}")
        print(f"Destination: {destination if 'destination' in locals() else 'Not set'}")
        
        self.lastposition = currentlocation
        return actions

    def on_start(self, map_state: MapState):
        self.__map_state = map_state
        print(map_state)

    def createPoint(self,location: Point):
        return (round(location.x,2),round(location.y,2))
    
    def currentCell(self, location):
        x, y = location[0],location[1]
        cell_x = x // 10
        cell_y = y // 10
        return (cell_x, cell_y)

    def on_end(self):
        pass
    def find_nearest_coin(self, coins, our_position):
        return min(coins, key=lambda coin: self.distance(coin.position, our_position), default=None)

    def find_nearest_enemy(self, players, our_bot):
        enemies = [player for player in players if player['name'] != our_bot['name']]
        return min(enemies, key=lambda enemy: self.distance(enemy['position'], our_bot['position']), default=None)

    def distance(self, point1, point2):
        return ((point1.x - point2.x)**2 + (point1.y - point2.y)**2)**0.5

    def find_path(self, start: Point, goal: Point):
        def heuristic(a, b):
            return abs(b.x - a.x) + abs(b.y - a.y)

        def get_neighbors(point):
            neighbors = []
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
                next_point = Point(point.x + dx, point.y + dy)
                if 0 <= next_point.x < self.__map_state.size and 0 <= next_point.y < self.__map_state.size:
                    if self.__map_state.discrete_grid[int(next_point.y)][int(next_point.x)] == 0:
                        neighbors.append(next_point)
            return neighbors

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current = heapq.heappop(frontier)[1]

            if current.x == goal.x and current.y == goal.y:
                break

            for next in get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + heuristic(goal, next)
                    heapq.heappush(frontier, (priority, next))
                    came_from[next] = current

        if goal not in came_from:
            return None

        path = []
        current = goal
        while current != start:
            path.append(current)
            current = came_from[current]
        path.reverse()
        return path