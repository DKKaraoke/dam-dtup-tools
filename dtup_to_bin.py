#!/usr/bin/env python
# coding: utf-8

import argparse

from dam_dtup_tools import DamDtupFile, DamSprcHeader


def main(argv=None):
    parser = argparse.ArgumentParser(description="DAM DTUP to BIN")
    parser.add_argument("source_path", help="Source DAM DTUP file path")
    parser.add_argument("destination_path", help="Destination BIN file path")
    args = parser.parse_args()

    with open(args.source_path, "rb") as dtup_file:
        if DamSprcHeader.has_sprc_header(dtup_file):
            sprc_header = DamSprcHeader.read(dtup_file)
            if not sprc_header.validate_crc(dtup_file):
                raise ValueError("SPRC Header CRC validation failed.")
            dtup_file.seek(16)

        dtup = DamDtupFile.read(dtup_file)
        with open(args.destination_path, "wb") as bin_file:
            bin_file.write(dtup.get_payload())


if __name__ == "__main__":
    main()
