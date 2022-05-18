import ncs
with ncs.maapi.single_read_trans('admin', 'python') as trans:
    root = ncs.maagic.get_root(trans)
    for device in root.devices.device:
        if device.device_type.netconf.ned_id == None:
            print(device.config.hostname, "- Address:", device.address,"- Port:",device.port,"- NED:",device.device_type.cli.ned_id)
        else:
            print(device.config.configuration.system.host_name, "- Address:", device.address,"- Port:",device.port,"- NED:",device.device_type.netconf.ned_id)