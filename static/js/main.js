let aliveSecond = 0;
let heartbeatRate = 5000;
let myChannel = "johns_sd3b_pi";

let pubnub;

const setupPubNub = () => {
    // Update this block with your publish/subscribe keys
    pubnub = new PubNub({
        publishKey : "pub-c-6ce775ac-3b15-47e0-937b-e5bd7cf6c79d",
        subscribeKey : "sub-c-6eb23377-44fd-4c6e-b456-974c422b6cc7",
        userId: "115286914554441662160" // Get device name
    });

    // add listener
    const listener = {
        status: (statusEvent) => {
            if (statusEvent.category === "PNConnectedCategory") {
                console.log("Connected");
            }
        },
        message: (messageEvent) => {
            console.log(messageEvent.message);
            received = messageEvent.message;
            if(received["motion"])
            {
                if(received["motion"] == "Motion Detected")
                {
                    document.getElementById("motion_id").innerHTML = "Motion Detected";
                }
                else
                {
                    document.getElementById("motion_id").innerHTML = "No Motion Detected";
                }
            }
        },
        presence: (presenceEvent) => {
            // handle presence
        }
    };
    pubnub.addListener(listener);

    // subscribe to a channel
    pubnub.subscribe({
        channels: [myChannel]
    });
};

function publishUpdate(channel, message)
{
    pubnub.publish({
        channel: channel,
        message: message
    });
}


function time()
{
        let d = new Date();
        let currentSecond = d.getTime();
        if(currentSecond - aliveSecond > heartbeatRate + 1000)
        {
                document.getElementById("connection_id").innerHTML = "DEAD!!!!";
        }
        else
        {
                document.getElementById("connection_id").innerHTML = "Alive";
        }
        setTimeout('time()', 1000);
}


function keepAlive()
{
        fetch('/keep_alive')
        .then(response => {
                if(response.ok){
                        let date = new Date();
                        aliveSecond = date.getTime();
                        return response.json();
                }
                throw new Error('Server offline');
        })
        .then(responseJson=>{
                if(responseJson.motion == 1){
                        document.getElementById("motion_id").innerHTML = "Motion Detected";
                }
                else{
                        document.getElementById("motion_id").innerHTML = "No Motion Detected";
                }
        })
        .catch(error => console.log(error));
        setTimeout('keepAlive()', heartbeatRate);
}


function handleClick(cb)
{
        if(cb.checked)
        {
                value = "on";
        }
        else
        {
                value="off";
        }
        publishUpdate(myChannel, {"buzzer" : value});
}

function logout()
{
    console.log("Logging out and unsubscribing");
    pubnub.unsubscribe({
        channels : [myChannel]
    })
    location.replace("/logout");
}

function grantAccess(ab)
{
    let userId = ab.id.split("-")[2];
    let readState = document.getElementById("read-user-"+userId).checked;
    let writeState = document.getElementById("write-user-"+userId).checked;
    console.log("grant-"+userId+"-"+readState+"-"+writeState);
    sendEvent("grant-"+userId+"-"+readState+"-"+writeState);
}

function sendEvent(value)
{
    fetch(value,
    {
        method:"POST",
    })
    .then(response => response.json())
    .then(responseJson => {
	    console.log(responseJson);
        if(responseJson.hasOwnProperty('token'))
        {
            pubnub.setToken(responseJson.token);
            console.log(responseJson.token);
            pubnub.setCipherKey(responseJson.cipher_key);
            console.log(responseJson.cipher_key);
            subscribe();
        }
    });
}

function subscribe()
{
    pubnub.subscribe({channels: [myChannel],},
    function(status, response)
    {
        if(status.error)
        {
            console.log("Subscribe failed ", status)
        }
        else
        {
            console.log("Subscribe success", status)
        }
    }
    );
}
