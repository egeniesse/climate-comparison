import uuid

def data_point(location, date, data_type, data_value, version):
    identifier = f"{location}{date}{data_type}{data_value}{version}"
    guid = str(uuid.uuid5(uuid.NAMESPACE_X500, identifier))
    return {
        "guid": guid,
        "location": location,
        "date": date,
        "version": version,
        "data_type": data_type,
        "data_value": data_value,
    }

def mean(values):
    sorted_points = sorted(values)
    center = len(values) // 2
    if len(values) % 2 == 0:
        return round((sorted_points[center] + sorted_points[center]) / 2, 3)
    else:
        return sorted_points[center]
    