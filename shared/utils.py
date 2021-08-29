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
    