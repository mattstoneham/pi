(function(ext) {
	
    var socket = null;
	var connected = false;

    // an array to hold possible digital input values for the reporter block
    var digital_inputs = new Array(32);
    var myStatus = 1; // initially yellow
    var myMsg = 'not_ready';
    var distance = 0.0
    
    
    
    // Cleanup function when the extension is unloaded
    ext._shutdown = function () {
        var msg = JSON.stringify({
            "command": "shutdown"
        });
        window.socket.send(msg);
    };

    // Status reporting code
    // Use this to report missing hardware, plugin or unsupported browser
    ext._getStatus = function() {
        return {status: 2, msg: 'Ready'};
    };



    ext.connect = function (callback) {
        window.socket = new WebSocket("ws://127.0.0.1:9000");
        window.socket.onopen = function () {
            var msg = JSON.stringify({
                "command": "ready"
            });
            window.socket.send(msg);
            myStatus = 2;

            // change status light from yellow to green
            myMsg = 'ready';
            connected = true;

            // initialize the reporter buffer
            digital_inputs.fill('0');

            // give the connection time establish
            window.setTimeout(function() {
            callback();
        }, 1000);

        };

        window.socket.onmessage = function (message) {
            var msg = JSON.parse(message.data);

            // handle the only reporter message from the server
            // for changes in digital input state
            var reporter = msg['report'];
            
            if(reporter === 'digital_input_change') {
                var pin = msg['pin'];
                digital_inputs[parseInt(pin)] = msg['level']
            }

            if(reporter === 'ultrasonicdistance') {
                //distance = msg['value'];
                distance = 54321
                console.log(msg)
            }

            console.log(message.data)
        };

        window.socket.onclose = function (e) {
            console.log("Connection closed.");
            socket = null;
            connected = false;
            myStatus = 1;
            myMsg = 'not_ready'
        };
    };

    // Function for sending data
    // Sen
    var socketQueueId = 0;
    var socketQueue = {};
    function sendData(data, onReturnFunction){
        socketQueueId++;
        if (typeof(returnFunc) == 'function'){
            // the 'i_' prefix is a good way to force string indices
            socketQueue['i_'+socketQueueId] = onReturnFunction;
        }
        msg = JSON.stringify({'cmd_id':socketQueueId, 'json_data':data});
        try{
            window.socket.send(msg);
            console.log('Sent');
        }catch(e){
            console.log('Sending failed ... .disconnected failed');
        }
    }

    ext.getdatatest = function () {
        //msg = JSON.stringify({
        //    "command": 'getdatatest'
        //});
        sendData('man whats 1+1', function(data){console.log('server response:');console.log(data);});
    }

        //d
	ext.getdistance = function () {
        // Return float value from distance sensor
        if (connected == false) {
            alert("Not Connected");
        }
        else {
            var msg = JSON.stringify({
                "command": 'getdistance'
            });
            console.log(msg);
            window.socket.send(msg);
            return distance
        }
	};



    // Block and block menu descriptions
    var descriptor = {
        blocks: [
        // Block type, block name, fnct name
        [" ", 'Connect to Python server', 'connect'],
        ["r", 'Distance from ultrasonic sensor ', 'getdistance']
        ]

    };

// Register the extension
ScratchExtensions.register('PiBot.js', descriptor, ext);
})({});
