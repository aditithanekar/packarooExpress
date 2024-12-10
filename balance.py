from container import container

def balance():

    
    # Create 8x12 grid representation
    grid = [[None for _ in range(12)] for _ in range(8)]
    
    def calculate_side_weights():
        left_weight = right_weight = 0
        # Column 6 is middle (index 5), so 0-5 is left, 6-11 is right
        for row in grid:
            for col in range(12):
                if row[col] is not None and not row[col].IsNAN and not row[col].IsUNUSED:
                    if col < 5:  # Left side
                        left_weight += row[col].weight
                    elif col > 5:  # Right side
                        right_weight += row[col].weight
        return left_weight, right_weight
    
    def is_balanced(left_w, right_w):
        if left_w == 0 and right_w == 0:
            return True
        if left_w == 0 or right_w == 0:
            return False
        ratio = abs(left_w - right_w) / max(left_w, right_w)
        return ratio <= 0.1  # 10% threshold
    
    def find_unused_spaces():
        unused = []
        for i in range(8):
            for j in range(12):
                if grid[i][j] is not None and grid[i][j].IsUNUSED:
                    unused.append((i, j))
        return unused
    
    def find_movable_containers():
        containers = []
        for i in range(8):
            for j in range(12):
                if grid[i][j] is not None and not grid[i][j].IsNAN and not grid[i][j].IsUNUSED:
                    # Check if container is on top (no container above it)
                    if i == 0 or grid[i-1][j] is None or grid[i-1][j].IsUNUSED:
                        containers.append((i, j))
        return containers
    
    def try_balance():
        left_weight, right_weight = calculate_side_weights()
        print(f"Initial balance - Left: {left_weight}, Right: {right_weight}")
        
        if is_balanced(left_weight, right_weight):
            return []
        
        movable = find_movable_containers()
        unused = find_unused_spaces()
        best_moves = None
        min_moves = float('inf')
        
        def try_moves(moves, current_grid):
            nonlocal best_moves, min_moves
            
            left_w, right_w = calculate_side_weights()
            if is_balanced(left_w, right_w):
                if len(moves) < min_moves:
                    min_moves = len(moves)
                    best_moves = moves.copy()
                return
            
            if len(moves) >= min_moves:
                return
                
            for src_row, src_col in movable:
                if current_grid[src_row][src_col] is None or \
                   (current_grid[src_row][src_col] is not None and \
                    (current_grid[src_row][src_col].IsNAN or current_grid[src_row][src_col].IsUNUSED)):
                    continue
                    
                for dst_row, dst_col in unused:
                    # Skip if destination is not UNUSED
                    if current_grid[dst_row][dst_col] is None or \
                       not current_grid[dst_row][dst_col].IsUNUSED:
                        continue
                    
                    # Try move
                    container = current_grid[src_row][src_col]
                    unused_container = current_grid[dst_row][dst_col]
                    
                    # Swap positions
                    current_grid[src_row][src_col] = unused_container
                    current_grid[dst_row][dst_col] = container
                    
                    # Update locations
                    old_container_loc = container.location
                    old_unused_loc = unused_container.location
                    
                    container.location = (dst_row+1, dst_col+1)
                    unused_container.location = (src_row+1, src_col+1)
                    
                    moves.append((
                        (src_row+1, src_col+1),
                        (dst_row+1, dst_col+1),
                        container
                    ))
                    
                    try_moves(moves, current_grid)
                    
                    # Undo move
                    moves.pop()
                    current_grid[dst_row][dst_col] = unused_container
                    current_grid[src_row][src_col] = container
                    container.location = old_container_loc
                    unused_container.location = old_unused_loc
        
        try_moves([], grid)
        return best_moves
    
    # Execute balancing
    moves = try_balance()
    
    if not moves:
        print("Ship is already balanced or cannot be balanced")
        return
    
    print(f"\nNumber of moves required: {len(moves)}")
    for src, dst, container in moves:
        print(f"Move container {container.description} from {src} to {dst}")
    
    # Calculate final weights
    final_left, final_right = calculate_side_weights()
    print(f"\nFinal balance - Left: {final_left}, Right: {final_right}")