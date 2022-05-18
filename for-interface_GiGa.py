import ncs
pe1_name = ""    #device name on NSO devices list

with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
    root = ncs.maagic.get_root(rtrans)
    for interface in root.devices.device["vXR-01"].config.interface["cisco-ios-xr:GigabitEthernet"]: 
        print(interface.id)
