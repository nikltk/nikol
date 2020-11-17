from itertools import groupby

def sort(data, keys=[]):
    """sort(data, keys=[])

data를 keys에 나타난 기준대로 정렬된 값을 반환하는 함수입니다.

data는 list의 list 형태여야 합니다.

keys는 dict의 list 형태여야 하며, 각 dict는 "key", "number", "reverse" 키에 해당하는 값을 가집니다. 각 dict 원소에서 "key"에 해당하는 값이 N이라면 data에서 각각의 리스트의 N번째 항목의 값을 기준으로 리스트들을 정렬하게 됩니다. 각 dict에서 "type"이 "int"인 경우 정수라는 가정하에서, "float"인 경우 실수라는 가정하에서 정렬하게 되고 "string"인 경우 문자열이라는 가정 하에서 정렬하게 됩니다. 각 dict 원소에서 "reverse" 값은 정렬 순서를 정방향으로 할지 역방향으로 할지 결정해주는 True 혹은 False 값입니다.

keys에 여러 dict 원소가 있을 경우 첫번째 원소를 기준으로 먼저 정렬한 뒤 그 정렬된 하위 그룹 안에서 그 다음 dict 값을 기준으로 정렬하는 식으로 각 원소에 대해 차례대로 정렬합니다. 

반환 값도 list의 list 형태입니다. 
"""
    if keys == []:
        return data
    else:
        field_num = int(keys[0]["key"])-1
        field_type = keys[0].get("type", "string")
        is_reverse = keys[0].get("reverse", False)

        if field_type == "int":
            projection = lambda x: int(x[field_num])
        if field_type == "float":
            projection = lambda x: float(x[field_num])
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
