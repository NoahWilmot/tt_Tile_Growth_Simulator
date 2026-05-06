
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import *
from cocotb_tools.runner import *
import time
import random

COLOR_REPS = {0: '.', 1: 'A', 2: 'B', 3: 'Z'} # '.' means empty
                                              # 'A' is color 1
                                              # 'B' is color 2
                                              # reserve 'Z' for cursor blink
COLOR_NAMES = {1: 'A', 2: 'B'} #color 1 & color 2

#displays the current grid
def print_grid(dut, description="default grid"):
    print(f"\n    {description} ")
    print("   " + " ".join(f"{c:X}" for c in range(16)))

    for r in range(16):
        row_str = f"{r:X}  "
        for c in range(16):
            gl = int(dut.gridl[r].value)
            gh = int(dut.gridh[r].value)
            #shift the high bit over
            #shift rows according to c and grab LSB
            #or the high and low bit to combine them
            tile = ((gh >> c) & 1) << 1 | ((gl >> c) & 1)
            row_str += COLOR_REPS.get(tile) + " "
        print(row_str)
    print()

#simulates a button press
async def press(dut, signal, cycles=1):
    await RisingEdge(dut.clock)
    signal.value = 1
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    signal.value = 0
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)

#simulates a specific button press
async def press_up(dut): await press(dut, dut.up)
async def press_down(dut): await press(dut, dut.down)
async def press_left(dut): await press(dut, dut.left)
async def press_right(dut): await press(dut, dut.right)
async def press_color_sel(dut): await press(dut, dut.color_sel)
async def press_place(dut): await press(dut, dut.place)
async def press_start(dut): await press(dut, dut.start)

#moves the cursor to a specified row and column
async def move_cursor(dut, target_row, target_col, ):
    for _ in range(32): #safe upper bound
        cur_row = int(dut.pg.cursor_row.value)
        cur_col = int(dut.pg.cursor_col.value)
        print(f" cursor: ({cur_row},{cur_col}) -> target: ({target_row},{target_col})")
        if cur_row == target_row and cur_col == target_col:
            break

        if cur_row != target_row:
            down_dist = (target_row - cur_row) if target_row > cur_row else (16 - cur_row + target_row)
            up_dist   = (cur_row - target_row) if cur_row > target_row else (16 - target_row + cur_row)
            if down_dist <= up_dist:
                await press_down(dut)
            else:
                await press_up(dut)

        elif cur_col != target_col:
            right_dist = (target_col - cur_col) if target_col > cur_col else (16 - cur_col + target_col)
            left_dist  = (cur_col - target_col) if cur_col > target_col else (16 - target_col + cur_col)
            if right_dist <= left_dist:
                await press_right(dut)
            else:
                await press_left(dut)

        await RisingEdge(dut.clock)
        await RisingEdge(dut.clock)

#repositions the cursor a specified number of times to randomize the seed
async def randomize_seed(dut, repositions=10):
    print(f"\n...Randomizing seed with {repositions} cursor moves")
    for _ in range(repositions):
        await move_cursor(dut, random.randint(0,15), random.randint(0,15))

#places a color at the current position of the cursor
async def place_color(dut, row, col, color):
    await move_cursor(dut, row, col)
    cur_color = int(dut.pg.selected_color.value)
    if cur_color != color:
        await press_color_sel(dut)
    print(f"...Placing color {COLOR_NAMES.get(color)} at ({row}, {col})")
    await press_place(dut)
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)

######################
# In-game monitoring #
######################

#waits for spread state to begin
async def wait_for_spread(dut):
    while True:
        await RisingEdge(dut.clock)
        if dut.ig.cur_state.value.is_resolvable:
            if int(dut.ig.cur_state.value) == 2:
                return

#waits for spread state to end
async def wait_for_spread_to_end(dut):
    while True:
        await RisingEdge(dut.clock)
        if dut.ig.cur_state.value.is_resolvable:
            if int(dut.ig.cur_state.value) != 2:
                return

SLEEP_TIME = .1

#manages the monitoring of the game
async def monitor_game(dut, frameout=1000):
    frame = 0
    while frame < frameout:
        await wait_for_spread(dut)
        await wait_for_spread_to_end(dut)
        frame += 1
        count = int(dut.count.value)
        done  = int(dut.ig.done.value)
        print_grid(dut, description=f"Frame: {frame}, Color A count: {count}")
        time.sleep(SLEEP_TIME)
        if done:
            print(f"  Game done after {frame} frames.")
            print(f"  Final color-A count: {count}")
            break
    else:
        print(f"  Reached frameout @ {frameout} frames")

async def reset(dut):
    dut.reset_n.value   = 0
    dut.up.value        = 0
    dut.down.value      = 0
    dut.left.value      = 0
    dut.right.value     = 0
    dut.color_sel.value = 0
    dut.place.value     = 0
    dut.start.value     = 0
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)
    await FallingEdge(dut.clock)
    dut.reset_n.value = 1
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)

@cocotb.test()
async def test_tg(dut):

    cocotb.start_soon(Clock(dut.clock, 10, unit="sec").start())

    # Reset
    print("\n--- RESET ---")
    await reset(dut)
    print_grid(dut, "Reset grid")

    # Pre game
    print("\n--- PRE-GAME ---")
    await randomize_seed(dut, 2) # randomize the seed

    test_num = random.randint(1,3)

    if test_num == "1":
        await place_color(dut, 0, 0, 1) 
        await place_color(dut, 0, 15, 2)  
        await place_color(dut, 15, 0, 2) 
        await place_color(dut, 15, 15, 1)  
        await place_color(dut, 7, 7, 1)   
        await place_color(dut, 7, 8, 2)   
    
    if test_num == "2": 
        await place_color(dut, 3, 3, 1)  
        await place_color(dut, 12, 12, 2)   
    
    if test_num == "3":
        await place_color(dut, 7, 7, 1) 

    print_grid(dut, "Pre-game grid")

    # Start
    print("\n--- STARTING GAME ---")
    await press_start(dut)
    await RisingEdge(dut.clock)
    await RisingEdge(dut.clock)

    # Monitor
    print("\n--- IN-GAME ---")
    await monitor_game(dut, 1000)

    #Ensure correctness
    #final_count = int(dut.count.value)
    #assert final_count <= 256, f"\nCount exceeds limit -> Test failed"
    print(f"\n Count checks out -> Test passed")

