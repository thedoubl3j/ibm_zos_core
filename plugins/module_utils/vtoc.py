# Copyright (c) IBM Corporation 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

import re


class VolumeTableOfContents(object):
    def __init__(self, module):
        self.module = module

    def get_volume_entry(self, volume):
        try:
            stdin = "  LISTVTOC FORMAT,VOL=3390={0}".format(volume.upper())
            dd = "SYS1.VVDS.V{0}".format(volume.upper())
            stdout = self._iehlist(dd, stdin)
            if stdout is None:
                return None
            data_sets = self._process_output(stdout)
        except Exception as e:
            raise VolumeTableOfContentsError(repr(e))
        return data_sets

    def get_data_set_entry(self, data_set_name, volume):
        data_set = None
        data_sets = self.get_volume_entry(volume)
        for ds in data_sets:
            if ds.get("data_set_name") == data_set_name.upper():
                data_set = ds
                break
        return data_set

    def _iehlist(self, dd, stdin):
        response = None
        rc, stdout, stderr = self.module.run_command(
            "mvscmd --pgm=iehlist --sysprint=* --dd={0} --sysin=stdin ".format(dd),
            data=stdin,
        )
        if rc == 0:
            response = stdout
        return response

    def _process_output(self, stdout):
        data_sets = []
        data_set_strings = self._separate_data_set_sections(stdout)
        for data_set_string in data_set_strings:
            data_sets.append(self._parse_data_set_info(data_set_string))
        return data_sets

    def _separate_data_set_sections(self, contents):
        delimeter = "0---------------DATA SET NAME----------------"
        data_sets = re.split(delimeter, contents)
        fixed_ds = [delimeter + x for x in data_sets[1:]]
        return fixed_ds

    def _parse_data_set_info(self, data_set_string):
        lines = data_set_string.split("\n")
        data_set_info = {}
        regex_for_rows = [
            r"(0-*DATA SET NAME-*\s+)(SER NO\s+)(SEQNO\s+)(DATE.CRE\s+)(DATE.EXP\s+)(DATE.REF\s+)(EXT\s+)(DSORG\s+)(RECFM\s+)(OPTCD\s+)(BLKSIZE[ ]*)",
            r"(0SMS.IND\s+)(LRECL\s+)(KEYLEN\s+)(INITIAL ALLOC\s+)(2ND ALLOC\s+)(EXTEND\s+)(LAST BLK\(T-R-L\)\s+)(DIR.REM\s+)(F2 OR F3\(C-H-R\)\s+)(DSCB\(C-H-R\)[ ]*)",
            r"([ ]*EATTR[ ]*)",
        ]
        data_set_info.update(
            self._parse_table_row(regex_for_rows[0], lines[0], lines[1])
        )
        data_set_info.update(
            self._parse_table_row(regex_for_rows[1], lines[2], lines[3])
        )
        data_set_info.update(
            self._parse_table_row(regex_for_rows[2], lines[4], lines[5])
        )
        data_set_info.update(self._parse_extents(lines[6:]))
        return data_set_info

    def _parse_table_row(self, regex, header_row, data_row):
        table_data = {}
        fields = re.findall(regex, header_row)

        if len(fields) > 0:
            if isinstance(fields[0], str):
                fields = [[fields[0]]]
            count = 0
            for field in fields[0]:
                table_data[field.strip(" -0")] = data_row[
                    count : count + len(field)
                ].strip()
                count += len(field)
        table_data = self._format_table_data(table_data)
        return table_data

    def _format_table_data(self, table_data):
        handlers = {
            "DATA SET NAME": "data_set_name",
            "SER NO": "volume",
            "SEQNO": "sequence",
            "DATE.CRE": "creation_date",
            "DATE.EXP": "expiration_date",
            "DATE.REF": "last_referenced_date",
            "EXT": "number_of_extents",
            "DSORG": "data_set_organization",
            "RECFM": "record_format",
            "OPTCD": "option_code",
            "BLKSIZE": "block_size",
            "SMS.IND": "sms_attributes",
            "LRECL": "record_length",
            "KEYLEN": "key_length",
            "INITIAL ALLOC": "space_type",
            "2ND ALLOC": "space_secondary",
            "EXTEND": self._format_extend,
            "LAST BLK(T-R-L)": {
                "name": "last_block_pointer",
                "func": self._format_last_blk,
            },
            "DIR.REM": "last_directory_block_bytes_used",
            "F2 OR F3(C-H-R)": {
                "name": "dscb_format_2_or_3",
                "func": self._format_f2_or_f3,
            },
            "DSCB(C-H-R)": {"name": "dscb_format_1_or_8", "func": self._format_dscb},
            "EATTR": "extended_attributes",
        }
        formatted_table_data = {}
        for key, value in table_data.items():
            if not value:
                continue
            updated_data_item = handlers.get(key, key)
            if isinstance(updated_data_item, str):  # only need to update name
                formatted_table_data[updated_data_item] = value
            elif isinstance(
                updated_data_item, dict
            ):  # need to update value, name defined
                updated_value = updated_data_item.get("func")(value)
                if not updated_value:
                    continue
                formatted_table_data[updated_data_item.get("name")] = updated_value
            else:  # need to determine name and value
                formatted_table_data = updated_data_item(value, formatted_table_data)
        return formatted_table_data

    def _format_extend(self, contents, formatted_table_data):
        matches = re.search(r"([0-9]+)(AV|BY|KB|MB)", contents)
        original_space_secondary = ""
        average_block_size = ""
        if matches:
            if matches.group(2) == "AV":
                average_block_size = matches.group(1)
            elif matches.group(2) == "BY":
                original_space_secondary = matches.group(1) + "B"
            elif matches.group(2) == "KB":
                original_space_secondary = matches.group(1) + "KB"
            elif matches.group(2) == "MB":
                original_space_secondary = matches.group(1) + "MB"
        if original_space_secondary:
            formatted_table_data["original_space_secondary"] = original_space_secondary
        if average_block_size:
            formatted_table_data["average_block_size"] = average_block_size
        return formatted_table_data

    def _format_last_blk(self, contents):
        result = None
        matches = re.search(r"[ ]*([0-9]+)[ ]+([0-9]+)[ ]+([0-9]+)?", contents)
        if matches:
            result = {}
            result["track"] = matches.group(1)
            result["block"] = matches.group(2)
            if matches.group(3):
                result["bytes_remaining"] = matches.group(3)
        return result

    def _format_f2_or_f3(self, contents):
        result = None
        matches = re.search(r"[ ]*([0-9]+)[ ]+([0-9]+)[ ]+([0-9]+)", contents)
        if matches:
            result = {}
            result["cylinder"] = matches.group(1)
            result["track"] = matches.group(2)
            result["record"] = matches.group(3)
        return result

    def _format_dscb(self, contents):
        result = None
        matches = re.search(r"[ ]*([0-9]+)[ ]+([0-9]+)[ ]+([0-9]+)", contents)
        if matches:
            result = {}
            result["cylinder"] = matches.group(1)
            result["track"] = matches.group(2)
            result["record"] = matches.group(3)
        return result

    def _parse_extents(self, lines):
        extents = []
        if re.search(r"THE\sABOVE\sDATASET\sHAS\sNO\sEXTENTS", "".join(lines)):
            return {}
        regex_for_extents_indent = (
            r"(0\s*EXTENTS\s+)(?:(NO\s+)(LOW\(C-H\)\s+)(HIGH\(C-H\)[ ]*))"
        )
        regex_for_header_row = r"(NO\s+)(LOW\(C-H\)\s+)(HIGH\(C-H\)[ ]*)"
        indent_group = re.findall(regex_for_extents_indent, lines[0])
        indent_length = len(indent_group[0][0])
        header_groups = re.findall(regex_for_header_row, lines[0])
        regex_for_extents_data = self._extent_regex_builder(
            indent_length, header_groups
        )
        extent_data = re.findall(regex_for_extents_data, "\n".join(lines), re.MULTILINE)
        if len(extent_data) > 0:
            extents = self._format_extent_data(extent_data)
        return {"extents": extents}

    def _extent_regex_builder(self, indent_length, header_groups):
        extent_regex = "^[ ]{{{0}}}".format(str(indent_length))
        for index, header_group in enumerate(header_groups):
            group_regex = "([ 0-9]{{{0}}})([ 0-9]{{{1}}})([ 0-9]{{{2}}})".format(
                *[str(len(x)) for x in header_group]
            )
            if index > 0:
                group_regex = "(?:{}){{0,1}}".format(group_regex)
            extent_regex += group_regex
        extent_regex += "$"
        return extent_regex

    def _format_extent_data(self, extent_data):
        extents = []
        flattened_extent_data = []
        for extent in extent_data:
            reduced_extent = [x.strip() for x in extent if x.strip() != ""]
            flattened_extent_data = flattened_extent_data + reduced_extent
        for index in range(int(len(flattened_extent_data) / 3)):
            position = index * 3
            extent = {}
            extent["number"] = flattened_extent_data[position]
            low = re.search(
                r"[ ]*([0-9]+)[ ]+([0-9]+)", flattened_extent_data[position + 1]
            )
            extent["low"] = {"cylinder": low.group(1), "track": low.group(2)}
            high = re.search(
                r"[ ]*([0-9]+)[ ]+([0-9]+)", flattened_extent_data[position + 2]
            )
            extent["high"] = {"cylinder": high.group(1), "track": high.group(2)}
            extents.append(extent)
        return extents


class VolumeTableOfContentsError(Exception):
    def __init__(self, msg=""):
        self.msg = "An error occurred during VTOC parsing or retrieval. {0}".format(msg)

