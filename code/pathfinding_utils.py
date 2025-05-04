import heapq

def heuristic(a, b):
    # Manhattan distance
    return abs(a[0] - b[0]) + abs(a[1] - b[1])

def astar(grid, start, goal):
    """
    grid: 2D list of 0 (walkable) and 1 (obstacle)
    start, goal: (x, y) tuples
    Returns: list of (x, y) tuples from start to goal (inclusive), or [] if no path
    """
    neighbors = [(0,1),(1,0),(-1,0),(0,-1)]
    # Early exit if start or goal is blocked
    if not (0 <= start[0] < len(grid[0]) and 0 <= start[1] < len(grid)) or not (0 <= goal[0] < len(grid[0]) and 0 <= goal[1] < len(grid)):
        return []
    if grid[start[1]][start[0]] == 1 or grid[goal[1]][goal[0]] == 1:
        return []

    close_set = set()
    came_from = {}
    gscore = {start:0}
    fscore = {start:heuristic(start, goal)}
    oheap = []
    heapq.heappush(oheap, (fscore[start], start))

    while oheap:
        current = heapq.heappop(oheap)[1]
        if current == goal:
            # Reconstruct path
            path = [current]
            while current in came_from:
                current = came_from[current]
                path.append(current)
            path.reverse()
            return path
        close_set.add(current)
        for i, j in neighbors:
            neighbor = (current[0]+i, current[1]+j)
            tentative_g_score = gscore[current] + 1
            if 0 <= neighbor[0] < len(grid[0]) and 0 <= neighbor[1] < len(grid):
                if grid[neighbor[1]][neighbor[0]] == 1:
                    continue
            else:
                continue
            if neighbor in close_set and tentative_g_score >= gscore.get(neighbor, float('inf')):
                continue
            if tentative_g_score < gscore.get(neighbor, float('inf')):
                came_from[neighbor] = current
                gscore[neighbor] = tentative_g_score
                fscore[neighbor] = tentative_g_score + heuristic(neighbor, goal)
                heapq.heappush(oheap, (fscore[neighbor], neighbor))
    return []

def build_grid(map_width, map_height, tile_size, obstacle_sprites):
    """
    Returns a 2D grid (list of lists) where 0=walkable, 1=obstacle.
    map_width, map_height: in pixels
    tile_size: size of one tile in pixels
    obstacle_sprites: pygame.sprite.Group of obstacles
    """
    grid_w = map_width // tile_size
    grid_h = map_height // tile_size
    grid = [[0 for _ in range(grid_w)] for _ in range(grid_h)]
    for sprite in obstacle_sprites:
        x = int(sprite.rect.x // tile_size)
        y = int(sprite.rect.y // tile_size)
        if 0 <= x < grid_w and 0 <= y < grid_h:
            grid[y][x] = 1
    return grid

def pos_to_grid(pos, tile_size):
    """Convert pixel position to grid coordinates."""
    return (int(pos[0] // tile_size), int(pos[1] // tile_size))

def grid_to_pos(grid_coord, tile_size):
    """Convert grid coordinates to pixel position (center of tile)."""
    return (grid_coord[0] * tile_size + tile_size // 2, grid_coord[1] * tile_size + tile_size // 2)
