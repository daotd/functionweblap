var type={
    GigabitEthernet:device_id_interface,
    TenGigE:device_id_interface,
    HundredGigE:device_id_interface

}
var main = document.getElementById('type_interface');
var sub = document.getElementById('id_interface');

main.addEventListener('change',function(){
    var selected_option = type[this.value];
    while(sub.options.length > 0){
        sub.options.remove(0);
    }
    Array.from(selected_option).forEach(function(el){
        let option = new Option(el,el);
        sub.appendChild(option);
    });
});