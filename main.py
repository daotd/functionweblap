from unicodedata import name
import click
from flask import Flask, render_template, request, url_for, redirect
import ncs




tam = []
tam_l2vpn = []
device_name = []
device_name_l2vpn = []
device_type_interface = []
device_id_interface = []
app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

# Creat Loopback Service
@app.route('/loopback', methods=['POST','GET'])
def loopback():
    # session.clear()
    with ncs.maapi.single_read_trans('admin', 'python') as trans:
        root = ncs.maagic.get_root(trans)
        device_name.clear()
        for device in root.devices.device:
            device_name.append(device.name)


    if request.method == 'POST':
        user = request.form.get('username')
        loop_id = request.form.get('id_loop')
        ip_add = request.form.get('add_ip')
        netmask = request.form.get('netmask')
        tam.append(f"{user}{loop_id}{ip_add}{netmask}")

        if not user or not loop_id or not ip_add or not netmask:
            error_statement = "Moi ban nhap thong tin vao o trong"
            return render_template("fail.html",
            error_statement = error_statement,
            device_name = device_name,
            user = user,
            loop_id = loop_id,
            ip_add = ip_add,
            netmask = netmask)

        with ncs.maapi.single_write_trans('admin', 'python') as t:
            root = ncs.maagic.get_root(t)
            #make a change
            t.device_cdb = root.devices.device[user]
            t.device_cdb.config.interface["Loopback"].create(loop_id)
            t.device_cdb.config.interface["Loopback"].create(loop_id).ipv4.address.ip = ip_add
            t.device_cdb.config.interface["Loopback"].create(loop_id).ipv4.address.mask = netmask
            t.apply()
            # print(t)
        succes = "Apply Complete"
        # device_name.clear()
        # return redirect(url_for('succes.html', tam = tam), succes = succes)
        return render_template('succes.html', tam = tam, succes = succes, device_name = device_name)
    return render_template('loopback.html',device_name = device_name)



# Creat L2VPN Service
@app.route('/l2vpn', methods=['POST','GET'])
def l2vpn():

    # with ncs.maapi.single_read_trans('admin', 'python') as trans:
    #     root = ncs.maagic.get_root(trans)
    #     device_name_l2vpn.clear()
    #     for device in root.devices.device:
    #         device.name
    #         device_name_l2vpn.append(device.name)

    #     for i in device_name_l2vpn:
    #         print(i)    
    #     device_type_interface.clear()
    #     for interface in root.devices.device[i].config.interface:

    #         if interface == "cisco-ios-xr:GigabitEthernet":
    #             device_type_interface.append(str("GigabitEthernet"))
    #         elif interface == "cisco-ios-xr:TenGigE": 
    #             device_type_interface.append(str("TenGigE"))
    #         elif interface == "cisco-ios-xr:HundredGigE": 
    #             device_type_interface.append(str("HundredGigE"))

    #     for o in device_type_interface:
    #         print(o)
        
    #     device_id_interface.clear()          
    #     for interfaces in root.devices.device[i].config.interface["cisco-ios-xr:"+o]:
    #         device_id_interface.append(interfaces.id)

    getname()
    gettype()
    getid()

    if request.method == 'POST':
        pe1_name = request.form.get('pe1_name')
        pe1_interface_type = request.form.get('pe1_interface_type')
        pe1_interface_id = request.form.get('pe1_interface_id')
        pe1_vlan = request.form.get('pe1_vlan')

        pe2_name = request.form.get('pe2_name')
        pe2_interface_type = request.form.get('pe2_interface_type')
        pe2_interface_id = request.form.get('pe2_interface_id')
        pe2_vlan = request.form.get('pe2_vlan')

        pwid = request.form.get('pwid')
        tam_l2vpn.append(f"{pe1_name}{pe1_interface_type}{pe1_interface_id}{pe1_vlan}{pe2_name}{pe2_interface_type}{pe2_interface_id}{pe2_vlan}{pwid}")

        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            for device in root.devices.device:
                if (pe2_name == device.name):
                    pe2_router_id = root.devices.device[pe2_name].config.interface.Loopback['0'].ipv4.address['ip']                    
                    print("PE-2:",pe2_name,"; Router ID:",pe2_router_id)

        with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
            root = ncs.maagic.get_root(rtrans)
            for device in root.devices.device:
                if (pe1_name == device.name):
                    pe1_router_id = root.devices.device[pe1_name].config.interface.Loopback['0'].ipv4.address['ip']
                    print("PE-1:",pe1_name,"; Router ID:",pe1_router_id)
                      

        with ncs.maapi.single_write_trans('admin', 'python') as wtrans:
            root = ncs.maagic.get_root(wtrans)
            #if root.devices.device[pe1_name].device_type.netconf.ned_id == None:       #---Cisco CLI NED devices
                # pe2_router_id = root.devices.device[pe2_name].config.interface.Loopback['0'].ipv4.address['ip']
            wtrans.group = root.devices.device[pe1_name].config.l2vpn.xconnect.group.create('vpws'+str(pwid))
            wtrans.p2p = root.devices.device[pe1_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p.create(str(pwid))
            wtrans.interface = root.devices.device[pe1_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p[str(pwid)].interface.create(pe1_interface_type+pe1_interface_id+'.'+str(pe1_vlan))
            wtrans.neighbor = root.devices.device[pe1_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p[str(pwid)].neighbor.create(pe2_router_id,pwid)
            wtrans.subinterface = root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet.create(pe1_interface_id+'.'+str(pe1_vlan))
            root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe1_interface_id+'.'+str(pe1_vlan)].mode = 'l2transport'
            root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe1_interface_id+'.'+str(pe1_vlan)].encapsulation.dot1q.vlan_id = [pe1_vlan]
            root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe1_interface_id+'.'+str(pe1_vlan)].rewrite.ingress.tag.pop = '1'
            root.devices.device[pe1_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe1_interface_id+'.'+str(pe1_vlan)].rewrite.ingress.tag.mode = 'symmetric'      
            
            # if root.devices.device[pe2_name].device_type.netconf.ned_id == None:       #---Cisco CLI NED devices
            wtrans.group = root.devices.device[pe2_name].config.l2vpn.xconnect.group.create('vpws'+str(pwid))
            wtrans.p2p = root.devices.device[pe2_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p.create(str(pwid))
            wtrans.interface = root.devices.device[pe2_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p[str(pwid)].interface.create(pe2_interface_type+pe2_interface_id+'.'+str(pe2_vlan))
            wtrans.neighbor = root.devices.device[pe2_name].config.l2vpn.xconnect.group['vpws'+str(pwid)].p2p[str(pwid)].neighbor.create(pe1_router_id,pwid)
            wtrans.subinterface = root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet.create(pe2_interface_id+'.'+str(pe2_vlan))
            root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe2_interface_id+'.'+str(pe2_vlan)].mode = 'l2transport'
            root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe2_interface_id+'.'+str(pe2_vlan)].encapsulation.dot1q.vlan_id = [pe2_vlan]
            root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe2_interface_id+'.'+str(pe2_vlan)].rewrite.ingress.tag.pop = '1'
            root.devices.device[pe2_name].config.interface.GigabitEthernet_subinterface.GigabitEthernet[pe2_interface_id+'.'+str(pe2_vlan)].rewrite.ingress.tag.mode = 'symmetric'
                
            wtrans.apply()
        succes_l2vpn = "Apply Complete"
        # return redirect(url_for('l2vpn',name = user,loop = loop_id,ip = ip_add,mask = netmask,name1 = user1,loop1 = loop_id1,ip1=ip_add1,mask1 = netmask1))
        return render_template('succes_l2vpn.html',tam_l2vpn = tam_l2vpn, succes_l2vpn = succes_l2vpn)
    return render_template('l2vpn.html', device_name_l2vpn = device_name_l2vpn, device_type_interface = device_type_interface, device_id_interface = device_id_interface)


@app.route('/getname', methods=['POST','GET'])
def getname():
    with ncs.maapi.single_read_trans('admin', 'python') as trans:
        root = ncs.maagic.get_root(trans)
        device_name_l2vpn.clear()
        for device in root.devices.device:
            device_name_l2vpn.append(device.name)
    return render_template('l2vpn.html', device_name_l2vpn = device_name_l2vpn, device_type_interface = device_type_interface,device_id_interface = device_id_interface)


@app.route('/gettype', methods=['POST','GET'])
def gettype():
    with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
        root = ncs.maagic.get_root(rtrans)
        for i in device_name_l2vpn:
            print(i)
        device_type_interface.clear()
        for interface in root.devices.device[i].config.interface:
            if interface == "cisco-ios-xr:GigabitEthernet":
                device_type_interface.append(str("GigabitEthernet"))
            elif interface == "cisco-ios-xr:TenGigE": 
                device_type_interface.append(str("TenGigE"))
            elif interface == "cisco-ios-xr:HundredGigE": 
                device_type_interface.append(str("HundredGigE"))   
            #device_type_interface.append(interface)
    return render_template('l2vpn.html',device_name_l2vpn = device_name_l2vpn, device_type_interface = device_type_interface,device_id_interface = device_id_interface)


@app.route('/getid', methods=['POST','GET'])
def getid():
    with ncs.maapi.single_read_trans('admin', 'python') as rtrans:
        root = ncs.maagic.get_root(rtrans)
        for i in device_name_l2vpn:
            print("Test: "+i)
        for o in device_type_interface:
            print("Test1: "+o)
        device_id_interface.clear()
    
        for interface in root.devices.device[i].config.interface["cisco-ios-xr:"+o]:
            device_id_interface.append(interface.id)
            print(device_id_interface)
        #device_id_interface.clear()          
        #for interfaces in root.devices.device["vXR-01"].config.interface["cisco-ios-xr:GigabitEthernet"]:
         #   device_id_interface.append(interfaces.id)

    return render_template('l2vpn.html',device_name_l2vpn = device_name_l2vpn, device_type_interface = device_type_interface,device_id_interface = device_id_interface)




if __name__ == '__main__':
    app.run(port = 3000)






















    

