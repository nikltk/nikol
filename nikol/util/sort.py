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
