from ..core.data import DNPData
import warnings
import numpy as _np
import h5py

None_alias = "__PYTHON_NONE__"  # h5 does not have Null type


python_types = [None]
replace_types = [None_alias]


def load_h5(path):
    """Returns Dictionary of dnpDataObjects

    Args:
        path (str): Path to h5 file

    Returns:
        dnpdata_collection: workspace object with data
    """

    f = h5py.File(path, "r")
    keys_list = f.keys()

    if list(keys_list) == [
        "__DNPDATA__"
    ]:  # If Only DNPData object in h5 file, return DNPData object, not dictionary
        data = read_dnpdata(f["__DNPDATA__"])
        return data

    dnp_dict = {}

    for key in keys_list:
        if f[key].attrs["dnplab_data_type"] == "dnpdata":
            data = read_dnpdata(f[key])
        elif f[key].attrs["dnplab_data_type"] == "dict":
            data = read_dict(f[key])
        else:
            warnings.warn("could not import key: %s" % str(key))

        dnp_dict[key] = data
    return dnp_dict


def read_dnpdata(dnpdata_group):
    coords = []
    dims = []
    attrs = {}
    dnplab_attrs = {}
    proc_attrs = {}
    values = dnpdata_group["values"][:]
    version = dnpdata_group.attrs["dnplab_version"]

    for index in range(len(_np.shape(values))):
        dim_key = dnpdata_group["values"].dims[index].keys()[0]  # assumes 1 key only
        coords.append(dnpdata_group["values"].dims[index][dim_key][:])
        dims.append(dim_key)

    for k in dnpdata_group["attrs"].attrs.keys():
        v = dnpdata_group["attrs"].attrs[k]
        if v in replace_types:
            ix = replace_types.index(v)
            v = python_types[ix]
        attrs[k] = v
    for k in dnpdata_group["attrs"]:
        v = dnpdata_group["attrs"][k][:]
        attrs[k] = v

    if "dnplab_attrs" in dnpdata_group.keys():
        for k in dnpdata_group["dnplab_attrs"].attrs.keys():
            v = dnpdata_group["dnplab_attrs"].attrs[k]
            if v in replace_types:
                ix = replace_types.index(v)
                v = python_types[ix]
            dnplab_attrs[k] = v
        for k in dnpdata_group["dnplab_attrs"]:
            v = dnpdata_group["dnplab_attrs"][k][:]
            dnplab_attrs[k] = v
            
    if "proc_attrs" in dnpdata_group.keys():
        for step in dnpdata_group["proc_attrs"].keys():
            args_dict = {}
            for arg in dnpdata_group["proc_attrs"][step].attrs.keys():
                v = dnpdata_group["proc_attrs"][step].attrs[arg]
                if v in replace_types:
                    ix = replace_types.index(v)
                    v = python_types[ix]
                args_dict[arg] = v
            proc_attrs[step] = args_dict
            
    data = DNPData(values, dims, coords, attrs, dnplab_attrs, proc_attrs)
    return data


def read_dict(dnpdata_group):
    data = dict(dnpdata_group["attrs"].attrs)
    return data


def save_h5(dataDict, path, overwrite=False):
    """Save workspace in .h5 format

    Args:
        dataDict (dict): dnpdata_collection object to save.
        path (str): Path to save data
        overwrite (bool): If True, h5 file can be overwritten. Otherwise, h5 file cannot be overwritten
    """

    if overwrite:
        mode = "w"
    else:
        mode = "w-"

    keysList = dataDict.keys()

    f = h5py.File(path, mode)

    for key in keysList:
        dnpDataObject = dataDict[key]
        
        dnpDataGroup = f.create_group(key, track_order=True)
        if isinstance(dnpDataObject, DNPData):
            write_dnpdata(dnpDataGroup, dnpDataObject)
        elif isinstance(dnpDataObject, dict):
            write_dict(dnpDataGroup, dnpDataObject)
        else:
            warnings.warn("Could not write key: %s" % str(key))

    f.close()


def write_dnpdata(dnpDataGroup, dnpDataObject):
    """Takes file/group and writes dnpData object to it

    Args:
        dnpDataGroup: h5 group to save data to
        dnpDataObject: dnpdata object to save in h5 format
    """
    dnpDataGroup.attrs["dnplab_version"] = dnpDataObject.version
    dnpDataGroup.attrs["dnplab_data_type"] = "dnpdata"
    dims_group = dnpDataGroup.create_group("dims")  # dimension names e.g. x,y,z
    attrs_group = dnpDataGroup.create_group("attrs")  # dictionary information
    dnp_dataset = dnpDataGroup.create_dataset("values", data=dnpDataObject.values)

    # Save axes information
    for ix in range(len(dnpDataObject.coords)):
        label = dnpDataObject.dims[ix]
        this_axes = dnpDataObject.coords[ix]
        dims_group.create_dataset(label, data=this_axes)
        dims_group[label].make_scale(label)

        dnp_dataset.dims[ix].attach_scale(dims_group[label])

    # Save Experiment Attributes
    for key in dnpDataObject.attrs:
        value = dnpDataObject.attrs[key]

        if isinstance(value, _np.ndarray):
            attrs_group.create_dataset(key, data=value)
        else:
            if value in python_types:
                ix = python_types.index(value)
                value = replace_types[ix]
            attrs_group.attrs[key] = value

    # Save DNPLab Attributes
    if hasattr(dnpDataObject, "dnplab_attrs"):
        dnplab_attrs_group = dnpDataGroup.create_group("dnplab_attrs", track_order=True)
        
        for key in dnpDataObject.dnplab_attrs:
            value = dnpDataObject.dnplab_attrs[key]

            if isinstance(value, _np.ndarray):
                dnplab_attrs_group.create_dataset(key, data=value)
            else:
                if value in python_types:
                    ix = python_types.index(value)
                    value = replace_types[ix]
                dnplab_attrs_group.attrs[key] = value

    # Save proc_steps
    if hasattr(dnpDataObject, "proc_attrs"):
        proc_attrs_group = dnpDataGroup.create_group("proc_attrs", track_order=True)
        for step in dnpDataObject.proc_attrs:
            proc_attrs_args_group = proc_attrs_group.create_group(step, track_order = True)
            for args in dnpDataObject.proc_attrs[step].keys():
                value = dnpDataObject.proc_attrs[step][args]

                if isinstance(value, _np.ndarray):
                    proc_attrs_args_group.create_dataset(args, data = value)
                else:
                    if value in python_types:
                        ix = python_types.index(value)
                        value = replace_types[ix]
                proc_attrs_args_group.attrs[args] = value


def write_dict(dnpDataGroup, dnpDataObject):
    """Writes dictionary to h5 file

    Args:
        dnpDataGroup (h5py.Group): h5 group to write attrs dictionary
        dnpDataObject (DNPData): DNPData object to write
    """
    #    dnpDataGroup.attrs['dnplab_version'] = dnpDataObject.version
    dnpDataGroup.attrs["dnplab_data_type"] = "dict"
    #    dnpDataGroup.attrs['dnplab_version'] = dnpDataObject.version
    attrs_group = dnpDataGroup.create_group("attrs")

    for key in dnpDataObject.keys():
        attrs_group.attrs[key] = dnpDataObject[key]
