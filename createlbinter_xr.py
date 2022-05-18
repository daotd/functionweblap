import ncs
import main

with ncs.maapi.single_write_trans('admin', 'python') as t:
    root = ncs.maagic.get_root(t)
    #make a change
    device_cdb = root.devices.device[main.loopback()]
    device_cdb.config.interface["Loopback"].create(main.loopback())
    # device_cdb.config.interface["Loopback"].create(loopback_id).ipv4.address.ip = ip_addresss
    # device_cdb.config.interface["Loopback"].create(loopback_id).ipv4.address.mask = netmask
    t.apply()
    print(t)