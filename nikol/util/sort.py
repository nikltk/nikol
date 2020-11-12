import re, sys
from itertools import groupby

def sort(data, keys=[]):
    if keys == []:
        return data
    else:
        field_num = int(keys[0]["key"])-1
        is_num_ord = "n" == keys[0].get("number", "s")
        is_reverse = keys[0].get("reverse", is_num_ord)

        if is_num_ord:
            projection = lambda x: int(x[field_num])
        else:
            projection = lambda x: x[field_num]

        data_sorted = sorted(data, key=projection, reverse=is_reverse)
        data_grouped = [list(i) for k, i in groupby(data_sorted, projection)]
        data_to_be_returned = [] 

        for subgroup in data_grouped:
            subgroup_sorted = sort(subgroup, keys=keys[1:])
            for item in subgroup_sorted:
                data_to_be_returned.append(item)
        return data_to_be_returned

def print_help():
    print("use: {}")

if __name__ == "__main__":
    key_list = []
    for arg in sys.argv:
        print("arg:", arg)
        rs = re.findall("r", arg)
        ns = re.findall("n", arg)
        if not re.match("-?r?n?r?k?[0-9]+n?r?n?", arg):
            well_formed_command = False
            break
        elif len(rs) > 1:
            well_formed_command = False
            break
        elif len(ns) > 1:
            well_formed_command = False
            break
        else:
            well_formed_command = True
            key_num = re.findall("[0-9]+", arg)
            is_num = ["s","n"][ns==[]]
            is_rev = rs != []
            key_list.append({"key":key_num, "number":is_num, "reverse":is_rev})
                
    print(key_list)
    if not well_formed_command:
        print_help()
    else:
        parsed_data = []
        for line in sys.stdin:
            parsed_data.append(line.strip().split("\t"))
        parsed_data_sorted = sort(parsed_data, keys=key_list)

        for line in parsed_data_sorted:
            sys.stdout.write('\t'.join(line)+"\n")

