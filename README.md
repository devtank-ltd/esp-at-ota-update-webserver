# ESP-AT OTA Update Webserver

Devtank's ESP-AT over the air update webserver. Used on OSM WiFi and POE
Communications Modules.

## Usage

### Authorisation Keys

First you will need authorisation keys. You can generate them with the
tool included:

    ./authorisation_key_gen.py [NAME]
    ./authorisation_key_gen.py "my_new_key"

And then save that to a file:

    ./authorisation_key_gen.py "my_new_key" > ./authorisation_keys.json

To add a new key:

    cat ./authorisation_keys.json | ./authorisation_key_gen.py "my_new_key" > ./authorisation_keys.json

### Providing the Binary Files

Currently the server looks in `partitions/{version}/` for binary files
to serve to the client. `version` here depends on the one requested by the
client's 'query', and the name of the binary file is also dependent on
the `filename` in the query section of the URL.

An example layout would be:

    webserver.py
    partitions/v1/ota.bin
    partitions/v1/mfg_nvs.bin

### Starting the Server

The server can be started with:

    ./webserver.py ./authorisation_keys.json

To see the full list of arguments use:

    ./webserver.py --help

### Connecting to the Server

An example client usage of the server with the partiton binary files
layout above would be:

    curl -H "Authorization: token [MYTOKEN]" '[URL]/v1/device/rom/?action=download_rom&version=v1&filename=mfg_nvs.bin'

Firstly, in the headers, you must include the 'Authorization' key with
the token as the value formatted with a space between token and your
token. Otherwise represented by: `{"Authorization": "token [MYTOKEN]"}`.

The URL is where you are hosting the webserver. The default port is
8000. Currently the first 'v1' is unused and device and rom is static.
The query section requires the action to be `download_rom` as there are
currently no other actions. The version in the query dicates what
directory the server will look for binaries. And filename dicates the
file to be retrieved.

Connecting to the server on the ESP requires you use a custom ESP-AT
firmware, example located [here](../osm_at_wifi_fw), and setting the OTA
parameters to match your server. Then using the command `AT+CIUPDATE`,
see [reference](https://docs.espressif.com/projects/esp-at/en/latest/esp32/AT_Command_Set/TCP-IP_AT_Commands.html#at-ciupdate-upgrade-firmware-through-wi-fi),
the requesting binary _should_ update.

### Systemd

This package comes with a systemd unit file, you can install it to your
system with:

    cp esp-at-ota-update-webserver.service /etc/systemd/system/
    systemctl reload-daemon
    systemctl enable --now esp-at-ota-update-webserver.service

If you aren't using systemd, I'm sorry :(.

