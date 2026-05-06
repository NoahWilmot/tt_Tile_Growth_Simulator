# Tile Growth Simulator Testbench

The testbench uses cocotb to simulate the full game flow. It drives the directional and control inputs to move the cursor, place colored cells, and start the simulation. It then monitors the InGameFSM state to detect each spread round and prints the grid to the console after each one, allowing visual verification of correct spreading behavior. Three starting configurations are tested in sequence.

# Test Configurations

## Configuration 1: Corner and Center Seeds
Four cells are placed at the corners of the grid (two color A, two color B) and two cells are placed in the center (one of each color). This configuration tests how two colors compete when starting from opposite ends of the grid as well as from the center simultaneously. The expectation is a roughly even split with complex, irregular boundaries between the two colors.

## Configuration 2: Diagonal Pair
One color A cell is placed at (3, 3) and one color B cell is placed at (12, 12), placing the two colors in diagonally opposite quadrants of the grid. This configuration tests long-range competition between two isolated seeds with no center influence. The color that spreads more aggressively due to the random LFSR outcomes will claim the majority of the grid.

## Configuration 3: Single Center Seed
A single color A cell is placed at the center of the grid (7, 7). This configuration tests single-color growth from a single starting point, with color A expected to fill the entire grid. It serves as a simple sanity check that the spread mechanic is working correctly from a known starting state.
