function get_data(){
    var socket = io.connect('http://' + document.domain + ':' + location.port);
    socket.emit('channel_hosts_list_req', 'ready');

    socket.on('channel_hosts_list_resp', function (data) {
        //console.log(data);
        //var json = JSON.parse($.trim(data));
        console.log('Got container_id : ' + data);

        data = JSON.parse(data);

        $.each(data, function (index, value) {
          console.log(value.ip + " " + value.memory + " " + value.cpu );
          $('#table_hosts').append('<tr><td>' + index + '</td><td id = "id" onclick="host_info(\'' + value.ip + '\')"><a>' + value.ip + '</a></td></tr>');
          $('#id').mouseover(function () {
            console.log("Mouse Over");
          })
        });
    });
}

function host_info(id) {
    window.location.href = '/host/' + id;
}

function initialise(){
    get_data();
}

function show(id, value) {
    document.getElementById(id).style.display = value ? 'block' : 'none';
}

$(document).ready(initialise);