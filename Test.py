def decode_lorawan_payload(payload):
    decoded_data = {}

    # Extracting data from payload
    alarm = int(payload[0:2], 16)
    battery_voltage = round(int(payload[2:6], 16) / 10000, 1)
    device_version = int(payload[6:8], 16) if payload[6:8] != "ff" else "n/a"
    humidity = int(payload[8:12], 16) / 100
    temperature = int(payload[12:16], 16) / 100

    # Assigning data to the decoded_data dictionary
    decoded_data["Alarm"] = alarm
    decoded_data["Battery voltage"] = battery_voltage
    decoded_data["Device version"] = device_version
    decoded_data["Humidity"] = humidity
    decoded_data["Temperature"] = temperature

    return decoded_data

# Raw uplink message
raw_uplink_message = "016f01240cfb1a85000000:6"

# Removing the port number from the raw uplink message
payload = raw_uplink_message.split(":")[0]

# Decoding the LoRaWAN payload
decoded_payload = decode_lorawan_payload(payload)

# Displaying the decoded data
for key, value in decoded_payload.items():
    print(key + ": " + str(value))
