def intersection(lst1, lst2):
    # Return intersectionn of two lists
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    return lst3


def union_without_duplicates(lst1, lst2):
    return list(set(lst1).union(set(lst2)))