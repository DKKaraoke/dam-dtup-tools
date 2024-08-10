import fire

from . import DamDtupFile, DamSprcHeader


class DamDtupTools:
    def dtup2bin(self, dtup_file_path: str, bin_file_path: str):
        """DAM DTUP to BIN

        Args:
            dtup_file_path (str): Source DAM DTUP file path
            bin_file_path (str): Destination BIN file path

        Raises:
            ValueError: Invalid DAM DTUP file
        """
        with open(dtup_file_path, "rb") as dtup_file:
            if DamSprcHeader.has_sprc_header(dtup_file):
                sprc_header = DamSprcHeader.read(dtup_file)
                # Validate file by the SPRC header
                if not sprc_header.validate_crc(dtup_file):
                    raise ValueError("SPRC Header CRC validation failed.")
                dtup_file.seek(16)

            dtup = DamDtupFile.read(dtup_file)
            with open(bin_file_path, "wb") as bin_file:
                bin_file.write(dtup.get_payload())


def main():
    fire.Fire(DamDtupTools)


if __name__ == "__main__":
    main()
