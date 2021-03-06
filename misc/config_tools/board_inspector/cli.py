#!/usr/bin/env python3
#
# Copyright (C) 2021 Intel Corporation. All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

import sys, os
import logging
import subprocess
import lxml.etree
import argparse
from importlib import import_module

script_dir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(os.path.join(script_dir))

def main(board_name, board_xml, args):
    try:
        # First invoke the legacy board parser to create the board XML ...
        legacy_parser = os.path.join(script_dir, "legacy", "board_parser.py")
        env = { "PYTHONPATH": script_dir }
        subprocess.run([sys.executable, legacy_parser, args.board_name, "--out", board_xml], check=True, env=env)

        # ... then load the created board XML and append it with additional data by invoking the extractors.
        board_etree = lxml.etree.parse(board_xml)
        root_node = board_etree.getroot()

        # Clear the whitespaces between adjacent children under the root node
        root_node.text = None
        for elem in root_node:
            elem.tail = None

        # Create nodes for each kind of resource
        root_node.append(lxml.etree.Element("processors"))
        root_node.append(lxml.etree.Element("caches"))
        root_node.append(lxml.etree.Element("memory"))
        root_node.append(lxml.etree.Element("devices"))

        extractors_path = os.path.join(script_dir, "extractors")
        extractors = [f for f in os.listdir(extractors_path) if f[:2].isdigit()]
        for extractor in sorted(extractors):
            module_name = os.path.splitext(extractor)[0]
            module = import_module(f"extractors.{module_name}")
            if not args.advanced and getattr(module, "advanced", False):
                continue
            module.extract(board_etree)

        # Finally overwrite the output with the updated XML
        board_etree.write(board_xml, pretty_print=True)

    except subprocess.CalledProcessError as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser()
    parser.add_argument("board_name", help="the name of the board that runs the ACRN hypervisor")
    parser.add_argument("--out", help="the name of board info file")
    parser.add_argument("--advanced", action="store_true", default=False, help="extract advanced information such as ACPI namespace")
    args = parser.parse_args()

    board_xml = args.out if args.out else f"{args.board_name}.xml"
    main(args.board_name, board_xml, args)
