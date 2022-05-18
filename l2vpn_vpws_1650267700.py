import ncs
pe1_found = 0
pe1_name = ""    #device name on NSO devices list
pe1_router_id = ""
pe1_interface_type = ""
pe1_interface_id = ""
pe1_interface_type_found = 0
pe1_interface_id_found = 0
pe1_vlan = 0
pe1_vlan_used = 1

pe2_found = 0
pe2_name = ""
pe2_router_id = ""
pe2_interface_type = ""
pe2_interface = ""
pe2_interface_type_found = 0
pe2_interface_id_found = 0
pe2_vlan = 0
pe2_vlan_used = 1

pwid = 0
pwid_used = 1


#---Choose PE Router (PE-1 & PE-2)
try:
    while (pe1_found == 0):
        pe1_name = input("Enter PE-1 (Ctrl+D to exit):")
        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            for device in root.devices.device:
                if (pe1_name == device.name):
                    pe1_found = 1
                    pe1_router_id = root.devices.device[pe1_name].config.interface.Loopback['0'].ipv4.address['ip']
                    print("PE-1:",pe1_name,"; Router ID:",pe1_router_id)
                    break
            else:
                print("Device not found !")
except EOFError:
    exit()    

try:
    while (pe2_found == 0):
        pe2_name = input("Enter PE-2 (Ctrl+D to exit):")
        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            for device in root.devices.device:
                if (pe2_name == device.name):
                    pe2_found = 1
                    pe2_router_id = root.devices.device[pe2_name].config.interface.Loopback['0'].ipv4.address['ip']                    
                    print("PE-2:",pe2_name,"; Router ID:",pe2_router_id)                    
                    break
            else:
                print("Device not found !")
except EOFError:
    exit()    
#
#---Enter PWID for VPWS VPN, warning if used

try:
    while (pwid_used == 1):
        while True:
            pwid_str = input("L2VPN VPWS Pseudowire ID (PWID) (Ctrl+D to exit):")
            if pwid_str.isdigit() and int(pwid_str) > 0:
                pwid = int(pwid_str)
                break
            else:
                print("Please input an integer for PWID")

        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            found1 = 0
            for group in root.devices.device[pe1_name].config.l2vpn.xconnect.group:
                for p2p in root.devices.device[pe1_name].config.l2vpn.xconnect.group[group['name']].p2p:
                    for p2p_neighbor in root.devices.device[pe1_name].config.l2vpn.xconnect.group[group['name']].p2p[p2p['name']].neighbor:
                        if (pwid == p2p_neighbor['pw-id']):
                            found1 = 1
                            print("Pseudowire is in use on device["+pe1_name+"]. Please choose another pwid")
                            break
                    if found1 == 1: break
                if found1 == 1: break        

            else:               #same as: if found1 == 0
                found2 = 0
                for group in root.devices.device[pe2_name].config.l2vpn.xconnect.group:
                    for p2p in root.devices.device[pe2_name].config.l2vpn.xconnect.group[group['name']].p2p:
                        for p2p_neighbor in root.devices.device[pe2_name].config.l2vpn.xconnect.group[group['name']].p2p[p2p['name']].neighbor:
                            if (pwid == p2p_neighbor['pw-id']):
                                found2 = 1
                                print("Pseudowire is in use on device[",pe2_name,"]. Please choose another pwid")
                                break
                        if found2 == 1: break
                    if found2 == 1: break
                else:
                    print("PWID:",pwid)
                found1 = found2
            pwid_used = found1
except EOFError:
    exit()    
#
#---Choose PE-1 Interface connect to CE-1
try:
    while (pe1_interface_type_found == 0):
        pe1_interface_type = input("Enter PE-1 Interface Type, default: GigabitEthernet (Ctrl+D to exit):") or "GigabitEthernet"
        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            for interface in root.devices.device[pe1_name].config.interface:
                if ("cisco-ios-xr:"+pe1_interface_type == interface):
                    pe1_interface_type_found = 1
                    print("PE-1 Interface type:",pe1_interface_type)
                    break
            else:
                print("PE-1 Interface Type not found !")
except EOFError:
    exit()         

try:
    while (pe1_interface_id_found == 0):
        pe1_interface_id = input("Enter PE-1 Interface ID, exp: 0/0/0/x (Ctrl+D to exit):")
        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            for interface in root.devices.device[pe1_name].config.interface["cisco-ios-xr:"+pe1_interface_type]:
                if (pe1_interface_id == interface['id']):
                    pe1_interface_id_found = 1
                    print("PE-1 interface:",pe1_interface_type,pe1_interface_id)
                    break
            else:
                print("PE-1",pe1_interface_type,"Interface ID not found !")
except EOFError:
    exit()         

#
#PE-1 VLAN to CE-1 (equal to sub-interface), warning if used
#
try:
    while (pe1_vlan_used == 1):
        while True:
            pe1_vlan_str = input("PE-1 VLAN to CE (0-4094) (Ctrl+D to exit):")
            if pe1_vlan_str.isdigit() and int(pe1_vlan_str) > 0 and int(pe1_vlan_str) < 4095:
                pe1_vlan = int(pe1_vlan_str)
                break
            else:
                print("Please input a valid PE-1 VLAN")        

        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            found = 0
            #this code for GigabitEthernet only, must state "if pe1_interface_type == 'GigabitEthernet', elseif: ..."
            for interface in root.devices.device[pe1_name].config.interface['cisco-ios-xr:GigabitEthernet-subinterface']:
                for subinterface in root.devices.device[pe1_name].config.interface['cisco-ios-xr:GigabitEthernet-subinterface'].GigabitEthernet:
                    if (subinterface['id'] == pe1_interface_id + '.' + str(pe1_vlan)):
                        found = 1
                        print("The VLAN",str(pe1_vlan),"is already used on device ["+pe1_name+"] Port ["+pe1_interface_type+pe1_interface_id+"]. Please choose another VLAN")
                        break
                if found == 1: break        
            else:
                print("PE-1 VLAN to CE-1:",pe1_vlan)
                print("PE-1 connect to CE-1 on interface:",pe1_interface_type+pe1_interface_id+"."+str(pe1_vlan))        
            pe1_vlan_used = found

except EOFError:
    exit()
#
#---Choose PE-2 Interface connect to CE-2    
try:
    while (pe2_interface_type_found == 0):
        pe2_interface_type = input("Enter PE-2 Interface Type, default: GigabitEthernet (Ctrl+D to exit):") or "GigabitEthernet"
        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            for interface in root.devices.device[pe2_name].config.interface:
                if ("cisco-ios-xr:"+pe2_interface_type == interface):
                    pe2_interface_type_found = 1
                    print("PE-2 Interface type:",pe2_interface_type)                    
                    break
            else:
                print("PE-2 Interface Type not found !")
except EOFError:
    exit()         

try:
    while (pe2_interface_id_found == 0):
        pe2_interface_id = input("Enter PE-2 Interface ID, exp: 0/0/0/x (Ctrl+D to exit):")
        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            for interface in root.devices.device[pe2_name].config.interface["cisco-ios-xr:"+pe2_interface_type]:
                if (pe2_interface_id == interface['id']):
                    pe2_interface_id_found = 1
                    print("PE-2 interface:",pe2_interface_type,pe2_interface_id)                                        
                    break
            else:
                print("PE-2",pe2_interface_type,"Interface ID not found !")
except EOFError:
    exit()         
#
#PE-2 VLAN to CE-2 (equal to sub-interface), warning if used
#
try:
    while (pe2_vlan_used == 1):
        while True:
            pe2_vlan_str = input("PE-2 VLAN to CE-2 (0-4094) (Ctrl+D to exit):")
            if pe2_vlan_str.isdigit() and int(pe2_vlan_str) > 0 and int(pe2_vlan_str) < 4095:
                pe2_vlan = int(pe2_vlan_str)
                break
            else:
                print("Please input a valid PE-2 VLAN")        

        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            found = 0
            #this code for GigabitEthernet only, must state "if pe2_interface_type == 'GigabitEthernet', elseif: ..."
            for interface in root.devices.device[pe2_name].config.interface['cisco-ios-xr:GigabitEthernet-subinterface']:
                for subinterface in root.devices.device[pe2_name].config.interface['cisco-ios-xr:GigabitEthernet-subinterface'].GigabitEthernet:
                    if (subinterface['id'] == pe2_interface_id + '.' + str(pe2_vlan)):
                        found = 1
                        print("The VLAN",str(pe2_vlan),"is already used on device ["+pe2_name+"] Port ["+pe2_interface_type+pe2_interface_id+"]. Please choose another VLAN")
                        break
                if found == 1: break        
            else:
                print("PE-2 VLAN to CE-2:",pe2_vlan)                   
                print("PE-2 connect to CE-2 on interface:",pe2_interface_type+pe2_interface_id+"."+str(pe2_vlan))        
            pe2_vlan_used = found

except EOFError:
    exit()
#
#---Verify configuration before applying
#
print("L2VPN VPWS (E-Line) Service will be applied on 2 devices: "+pe1_name+" and "+pe2_name+".")
print("Please verify the configuration below:")
#
le = "\n"
print(  "!" + le +
        "!" + le +
        "!" + le +               
        "PE-1 Router: "+pe1_name + le +
        "l2vpn" + le +
        "   xconnect group vpws" + str(pwid) + le +
        "   p2p " + str(pwid) + le +
        "   interface "+ pe1_interface_type + pe1_interface_id + "." + str(pe1_vlan) + le +
        "   neighbor ipv4 " + pe2_router_id + " pw-id " + str(pwid) + le +
        "!" + le +
        "interface " + pe1_interface_type + pe1_interface_id + "." + str(pe1_vlan) + " l2transport" + le +
        "   encapsulation dot1q " + str(pe1_vlan) + le +
        "   rewrite ingress tag pop 1 symmetric" + le +
        "   no shutdown" + le +
        "!" + le +
        "!" + le +
        "!" + le +               
        "PE-2 Router: "+pe2_name + le +
        "l2vpn" + le +
        "   xconnect group vpws" + str(pwid) + le +
        "   p2p " + str(pwid) + le +
        "   interface "+ pe2_interface_type + pe2_interface_id + "." + str(pe2_vlan) + le +
        "   neighbor ipv4 " + pe1_router_id + " pw-id " + str(pwid) + le +
        "!" + le +
        "interface " + pe2_interface_type + pe2_interface_id + "." + str(pe2_vlan) + " l2transport" + le +
        "   encapsulation dot1q " + str(pe2_vlan) + le +
        "   rewrite ingress tag pop 1 symmetric" + le +
        "   no shutdown" + le +
        "!" + le +
        "!" + le +
        "!" + le             
    )
#
try:
    answer = ""
    while (answer != 'y' and answer != 'n'):
        answer = input("Would you like to apply configuration to devices (Ctrl+D to exit) ? (y/n):")
        if (answer == 'y'):
            break
        elif (answer == 'n'):
            print('Abort !')
            exit()            
except EOFError:
    exit()   
#
print("Process applying configuration to devices. Please wait ...")
#
#---Write configuration to devices
#
with ncs.maapi.single_write_trans('admin', 'python') as wtrans:
    root = ncs.maagic.get_root(wtrans)
    if root.devices.device[pe1_name].device_type.netconf.ned_id == None:       #---Cisco CLI NED devices
        group = root.devices.device[pe1_name].config.l2vpn.xconnect.group.create('vpws'+str(pwid))
        p2p = root.devices.device[pe1_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p.create(str(pwid))
        interface = root.devices.device[pe1_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p[str(pwid)].interface.create(pe1_interface_type+pe1_interface_id+'.'+str(pe1_vlan))
        neighbor = root.devices.device[pe1_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p[str(pwid)].neighbor.create(pe2_router_id,pwid)
        subinterface = root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet.create(pe1_interface_id+'.'+str(pe1_vlan))
        root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe1_interface_id+'.'+str(pe1_vlan)].mode = 'l2transport'
        root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe1_interface_id+'.'+str(pe1_vlan)].encapsulation.dot1q.vlan_id = [pe1_vlan]
        root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe1_interface_id+'.'+str(pe1_vlan)].rewrite.ingress.tag.pop = '1'
        root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe1_interface_id+'.'+str(pe1_vlan)].rewrite.ingress.tag.mode = 'symmetric'
        
        
    else:
        print('PE-1 JunOS will be added later !')         
    #
    if root.devices.device[pe2_name].device_type.netconf.ned_id == None:       #---Cisco CLI NED devices
        group = root.devices.device[pe2_name].config.l2vpn.xconnect.group.create('vpws'+str(pwid))
        p2p = root.devices.device[pe2_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p.create(str(pwid))
        interface = root.devices.device[pe2_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p[str(pwid)].interface.create(pe2_interface_type+pe2_interface_id+'.'+str(pe2_vlan))
        neighbor = root.devices.device[pe2_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p[str(pwid)].neighbor.create(pe1_router_id,pwid)
        subinterface = root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet.create(pe2_interface_id+'.'+str(pe2_vlan))
        root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe2_interface_id+'.'+str(pe2_vlan)].mode = 'l2transport'
        root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe2_interface_id+'.'+str(pe2_vlan)].encapsulation.dot1q.vlan_id = [pe2_vlan]
        root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe2_interface_id+'.'+str(pe2_vlan)].rewrite.ingress.tag.pop = '1'
        root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe2_interface_id+'.'+str(pe2_vlan)].rewrite.ingress.tag.mode = 'symmetric'
        
        wtrans.apply()
        
        print("Congratulation !!! L2VPN VPWS Service Configuration was Applied on PE-1 ["+pe1_name+"] and PE-2 ["+pe2_name+"]")
        
    else:
        print('PE-2 JunOS will be added later !')   
#
#---Show l2vpn pseudowire status
#    
try:
    answer = ""
    while (answer != 'y' and answer != 'n'):
        answer = input("Would you like to verify the L2VPN status (Ctrl+D to exit) ? (y/n):")
        if (answer == 'y'):
            break
        elif (answer == 'n'):
            print('Abort !')
            exit()            
except EOFError:
    exit()   
#
show_l2vpn = 'show l2vpn xconnect pwid ' + str(pwid)
ping_mpls = 'ping mpls pseudowire ' + pe2_router_id + ' ' + str(pwid)

for cmd in [show_l2vpn,ping_mpls]:
    with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
        root = ncs.maagic.get_root(rtrans)
        input = root.devices.device[pe1_name].live_status.exec['any'].get_input()
        input.args = cmd.split(' ')
        output = root.devices.device[pe1_name].live_status.exec['any'](input)
        print('!')
        print(cmd)
        print(output.result)
        print('!')
        print('!')
        print('!')