# Copyright 2021 Charles-Henri Mousset
#
# License: BSD (see LICENSE)
#
# Verilator is a high performance Verilog simulator. It can be called by vcdsim directly.

import argparse

from vcdsim.vcd import VCDFile
from vcdsim.verilog import gen_verilog_tb
from vcdsim.verilator import gen_verilator_tb


def main():
    parser = argparse.ArgumentParser(description='Generate Verilog Testbench from VCD file')
    parser.add_argument('vcd', type=str, help="input VCD file")
    parser.add_argument('--verilog', type=str, help="generate verilog Testbench")
    parser.add_argument('--verilator', type=str, help="generate verilator c++ Testbench")
    parser.add_argument('--verilator-verilog', type=str,
                        help="generate verilator Verilog Testbench")
    parser.add_argument('--verilator-clock-freq', type=float, help="clock frequency")
    parser.add_argument('--ignore-invalid', action='store_true',
                        help="ignore invalid / unsupported values")
    parser.add_argument('--replace-invalid', default=-1, type=int, choices=[0, 1],
                        help="relace x and z with value")
    parser.add_argument('--name', default='vcdsim', type=str, help="Verilog module name")
    parser.add_argument('--tree', action='store_true',
                        help="display signals tree")

    args = parser.parse_args()
    vcd = VCDFile(
        args.vcd,
        {
            'timescale': '1ns',
        }
    )

    if args.verilog:
        gen_verilog_tb(vcd, args.verilog, args.name, args.ignore_invalid)
        print(f"generated {args.verilog}")
    if args.verilator:
        if not args.verilator_clock_freq:
            raise ValueError("please specify --verilator-clock-freq")

        gen_verilator_tb(
            vcd=vcd,
            file_path=args.verilator,
            modulename=args.name,
            clock_freq=args.verilator_clock_freq,
            ignore_invalid=args.ignore_invalid,
            replace_invalid=args.replace_invalid)

        print(f"generated {args.verilator}")
        if args.verilator_verilog:
            gen_verilog_tb(vcd, args.verilator_verilog, args.name, args.ignore_invalid, False)
            print(f"generated {args.verilator_verilog}")
    if args.tree:
        print(vcd.tree())


if __name__ == '__main__':
    main()
