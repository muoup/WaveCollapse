import pygame
import random
import sys
from pygame.locals import *

sprite_sheet = pygame.image.load("tile_sheet.png")
pygame.init()
game_display = pygame.display.set_mode((800, 800))
TILE_SIZE = 50
cont_loop = True


class Tile:
    image = None
    subimage_pos = None
    connects = None

    def __init__(self, subimage_pos, connects):
        self.subimage_pos = subimage_pos
        self.image = pygame.Surface((8, 8))
        self.image.blit(sprite_sheet, (0, 0), (8 * subimage_pos[0], 8 * subimage_pos[1], 8, 8))
        self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))

        self.connects = connects


    def valid(self, dir, comp_tile):
        if comp_tile is None:
            return not self.connects[dir]

        if comp_tile.finalized_tile is None:
            return True

        ctile = comp_tile.finalized_tile

        valid = self.connects[dir] == ctile.connects[(dir + 2) % 4]
        return valid

    def valid_around(self, tiles_adjacent):
        for i, qtile in enumerate(tiles_adjacent):
            if not self.valid(i, qtile):
                return False

        return True

    def copy(self):
        return Tile(self.subimage_pos, self.connects)


tiles = [
    Tile([0, 0], [False, True, True, False]),
    Tile([1, 0], [False, True, True, True]),
    Tile([2, 0], [False, False, True, True]),
    Tile([3, 0], [True, False, True, False]),
    Tile([0, 1], [True, True, True, False]),
    Tile([1, 1], [True, True, True, True]),
    Tile([2, 1], [True, False, True, True]),
    Tile([3, 1], [False, True, False, True]),
    Tile([0, 2], [True, True, False, False]),
    Tile([1, 2], [True, True, False, True]),
    Tile([2, 2], [True, False, False, True]),
    Tile([3, 2], [False, False, False, False]),
    Tile([0, 3], [False, False, True, False]),
    Tile([1, 3], [True, False, False, False]),
    Tile([2, 3], [False, False, False, True]),
    Tile([3, 3], [False, True, False, False])
]


class QuantumTile:
    def __init__(self):
        self.surrounding_tiles = None
        self.finalized_tile = None
        self.possible_tiles = tiles.copy()
        self.pos = None

    def reset(self):
        self.finalized_tile = None
        self.possible_tiles = tiles.copy()

    def set_surrounding_tiles(self, surrounding_tiles):
        self.surrounding_tiles = surrounding_tiles.copy()

    def set_pos(self, pos):
        self.pos = pos

    def calc_possible(self):
        if self.finalized_tile is not None:
            return

        to_remove = []

        for ptile in self.possible_tiles:
            if not ptile.valid_around(self.surrounding_tiles):
                to_remove.append(ptile)

        for ptile in to_remove:
            self.possible_tiles.remove(ptile)

    def choose_random_tile(self):
        if self.finalized_tile is not None:
            return

        if len(self.possible_tiles) is 0:
            self.set_tile(tiles[11])
        else:
            choice = int(random.random() * len(self.possible_tiles))
            self.set_tile(self.possible_tiles[choice])

    def set_tile(self, ptile):
        tile_cpy = ptile.copy()
        self.possible_tiles.clear()
        self.finalized_tile = tile_cpy
        grid[self.pos[0]][self.pos[1]] = tile_cpy

        for tile_cpy in self.surrounding_tiles:
            if tile_cpy is not None:
                tile_cpy.calc_possible()


GRID_SIZE = int(800 / TILE_SIZE)
grid = [[tiles[11].copy() for x in range(GRID_SIZE)] for y in range(GRID_SIZE)]
quantum_grid = [[QuantumTile() for xx in range(GRID_SIZE)] for yy in range(GRID_SIZE)]


def render_tiles():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            game_display.blit(grid[x][y].image, (TILE_SIZE * x, TILE_SIZE * y))


def reset():
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            global cont_loop
            quantum_grid[x][y].reset()
            grid[x][y] = tiles[11].copy()
            cont_loop = True


for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        quantum_tile = quantum_grid[x][y]
        surrounding_tiles = [None, None, None, None]

        if y is not 0:
            surrounding_tiles[0] = quantum_grid[x][y - 1]
        if x is not GRID_SIZE - 1:
            surrounding_tiles[1] = quantum_grid[x + 1][y]
        if y is not GRID_SIZE - 1:
            surrounding_tiles[2] = quantum_grid[x][y + 1]
        if x is not 0:
            surrounding_tiles[3] = quantum_grid[x - 1][y]

        quantum_tile.set_surrounding_tiles(surrounding_tiles)
        quantum_tile.set_pos([x, y])

for x in range(GRID_SIZE):
    for y in range(GRID_SIZE):
        quantum_grid[x][y].calc_possible()

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_r:
                reset()

    game_display.fill((255, 255, 255))
    render_tiles()

    pygame.time.wait(25)

    if not cont_loop:
        continue

    least_entropy = []
    lowest_count = 10000000

    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            tile = quantum_grid[x][y]
            pos_count = len(tile.possible_tiles)

            if x is 0 or y is 0 or x is GRID_SIZE or y is GRID_SIZE:
                pos_count *= 2

            if pos_count > lowest_count or pos_count <= 1:
                continue

            if pos_count < lowest_count:
                least_entropy.clear()
                lowest_count = pos_count

            least_entropy.append(tile)

    if len(least_entropy) == 0:
        cont_loop = False
        continue

    random_tile = random.choice(least_entropy)
    random_tile.choose_random_tile()

    pygame.display.update()
