/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_tile_growth_simulator_NoahW (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  wire data;

  tile_growth_simulator TGS (
    .clock(clk),
    .reset_n(rst_n),
    .up(ui_in[0]),
    .down(ui_in[1]),
    .left(ui_in[2]),
    .right(ui_in[3]),
    .color_sel(ui_in[4]),
    .place(ui_in[5]),
    .start(ui_in[6]),
    .data(data)
  );

  assign uo_out[0] = data;
  assign uo_out[7:1] = 7'b000_0000;

  assign uio_out[7:0] = 8'b0000_0000;

  assign uio_oe = 8'b1111_1111;

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, uio_in, ui_in[7], 1'b0};

endmodule
