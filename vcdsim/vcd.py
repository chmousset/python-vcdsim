# Copyright 2021 Charles-Henri Mousset
#
# License: BSD (see LICENSE)
#
# Value Change Dump read/write
# VCD is an ASCII-based format for dumpfiles, describing signal changes across time.
# This can be used to feed simulations as stimuli

import pathlib
import re


class VCDFile:
    def __init__(self, file=None, default_keywords={}):
        self.keywords = default_keywords
        self.path = file
        extension = pathlib.Path(file).suffix.lower()
        if extension == '.vcd':
            self.read_vcd(file)
        elif extension == '.csv':
            self.read_logica_csv(file)
        elif extension == '.bin':
            self.read_logica_bin(file)

    def read_vcd(self, vcd_file):
        changes = []
        header = []
        # seperate header an value changes
        with open(vcd_file, 'r') as f:
            line = f.readline()
            while '$dumpvars' not in line:
                header.append(line.strip())
                line = f.readline()
            while line != "":
                line = f.readline()
                if '$end' not in line:
                    line = line.strip()
                    if len(line):
                        changes.append(line)

        # parse header
        re_header = re.compile(r"\$([a-z]+)[ \n]?(.*?) \$end", re.MULTILINE | re.DOTALL)
        header = "\n".join(header)
        signals_symbols = {}
        hierarchy = []
        for match in re_header.finditer(header):
            keyword, content = match.group(1), match.group(2)
            if keyword == 'scope':
                if content.startswith('module'):
                    hierarchy.append(content.split()[1])
            elif keyword == 'upscope':
                hierarchy.pop()
            if keyword == 'var':
                wire, lenght, symbol, name = content.split(' ')
                signals_symbols[symbol] = hierarchy + [name]
            else:
                self.keywords[keyword] = content
        self.changes_raw = changes
        self.signals_symbols = signals_symbols


    def create_migen_sim(self, step_time_timescale):
        self.step_time_timescale = step_time_timescale
        self.migen_signals = {}
        from migen import Module, Signal
        top = Module()
        for tok in self.signals_symbols:
            hierarchy = self.signals_symbols[tok]
            module = top
            for module_name in hierarchy[:-1]:
                if not getattr(module, module_name, None):
                    module = Module()
                    setattr(module.submodules, module_name, module)  # create submodule
                else:
                    module = getattr(module, module_name, None)  # dig down existing hierarchy
            signal_name = hierarchy[-1]
            signal = Signal()
            setattr(module, signal_name, signal)
            self.migen_signals[tok] = signal
        return top

    def sim_migen_step(self, ignore_invalid=False):
        sigs = self.migen_signals
        ts = self.step_time_timescale
        vcd_t = 0
        sim_t = 0
        for chg in self.changes_raw:
            firstc = chg[0]
            if firstc in ('0', '1', 'x', 'X', 'z', 'Z'):
                yield sigs[chg[1:]].eq(int(firstc))
            elif firstc in ('b', 'B'):
                yield sigs[chg.split[1]].eq(int(chg[1:].split[0], 2))
            elif firstc == '#':  # Time marker
                vcd_t = int(chg[1:])
                while sim_t <= vcd_t:
                    yield
                    sim_t += ts
            elif ignore_invalid:
                pass
            else:
                raise ValueError(f"'{chg}' is not a value supported by migen simulator")

    def branch(self, name, hierarchy, level=0):
        if isinstance(hierarchy[name], dict):
            out = "    " * level + '.' + name + '\n'
        else:
            out = "    " * level + '.' + name + ' = Signal()\n'

        for k in hierarchy[name]:
            if isinstance(k, str):
                out += self.branch(k, hierarchy[name], level+1)
        return out
        

    def tree(self):
        def drill_dict(dict_in, drill, tail=None):
            dict_node = dict_in
            for d in drill[:-1]:
                if d not in dict_node:
                    dict_node[d] = {}
                dict_node = dict_node[d]
            if tail is not None:
                dict_node[drill[-1]] = tail
            return dict_in

        self.create_migen_sim(10)
        hierarchy = {}
        for k in self.signals_symbols:
            hierarchy = drill_dict(hierarchy, self.signals_symbols[k], self.migen_signals[k])

        return "\n".join([self.branch(k, hierarchy) for k in hierarchy])
