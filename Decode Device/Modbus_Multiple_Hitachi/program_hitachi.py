import pymongo
from pymodbus.client import ModbusTcpClient
from pymodbus.exceptions import ModbusException, ConnectionException
from datetime import datetime, timedelta
import struct
from threading import Thread

def connect_device(ipaddress, slave_id, min, offset, float_data, schema_data):
    client_modbus = ModbusTcpClient(
        ipaddress,
        port=8899,
        timeout=10,
        retries=3,
        retry_on_empty=False
    )

    result = client_modbus.read_holding_registers(min, offset, slave=slave_id)
    
    array_data = []
    if hasattr(result, 'registers'):
        array_data.extend(result.registers)
    if len(array_data) % 2 != 0:
        array_data.append(0) 

    for key, values_doc in schema_data['sensordata'].items():
            register_list = values_doc['register']
            first_index = register_list[0]
            lsat_index = register_list[-1] if len(register_list) > 1 else first_index        
             
            register_0 = first_index - min
            register_1 = lsat_index - min

            raw_value = array_data[register_1] + (array_data[register_0] << 16)
            float_value = struct.unpack('f', struct.pack('I', raw_value))[0]
            formatted_float = float(format(float_value, ".4f"))
            float_data.append(formatted_float)
    
    client_modbus.close()
    return float_data

def next_hour():
    now = datetime.now()
    # next_hour = (now + timedelta(hours=1)).replace(minute=0,second=0, microsecond=0)
    next_hour = (now + timedelta(minutes=2)).replace(second=0, microsecond=0)
    return next_hour

def next_second():
    now = datetime.now()
    next_second = (now + timedelta(seconds=5)).replace(microsecond=0)
    return next_second

def find_register(schema_collection, device_data,value_device,slave_id,first_run,last_sent_time):
    current_time = datetime.now()
    float_data = []
    ip_address = device_data['ip_address']
    schema_cursor = schema_collection.find({'slaveid': slave_id})
    schema_data = next(schema_cursor, None)
    min = 10000
    max = 0
    for key, value in schema_data['sensordata'].items():
        register_list = value['register']
        if len(register_list) > 1:
            first_register = register_list[0]
            lsat_register = register_list[1]
        else:
            first_register = register_list[0]
            lsat_register = register_list[0]

        if first_register > max :
            max = first_register
        if lsat_register > max :
            max = lsat_register
        if first_register < min :
            min = first_register
        if lsat_register < min :
            min = lsat_register
    offset = max - min
    if offset == 0 :
        offset = 1

    sensor_names = [key for key, _ in schema_data['sensordata'].items()]
    value_sensor = connect_device(ip_address, slave_id, min, offset, float_data,schema_data)

    sensordata_dict = dict(zip(sensor_names, value_sensor))
    json_type = {
        "date": current_time,
        "ipaddress": ip_address,
        "sensordata": sensordata_dict,
        "slaveid": slave_id
    }

    # if first_run or current_time >= last_sent_time:
    #     json_type = {
    #         "date": current_time,
    #         "ipaddress": ip_address,
    #         "sensordata": sensordata_dict,
    #         "slaveid": slave_id
    #     }
    #     # value_device.insert_one(json_type)
    #     # print(json_type)
    #     last_sent_time = next_hour()
    #     first_run = False
    return json_type,value_sensor

def process_sensor_data(doc):
    result = []
    for i in range(0, len(doc), 3):
        slice = doc[i:i+3]
        slice_sum = sum(slice)
        non_zero_count = sum(1 for x in slice if x != 0)
        if non_zero_count > 0:
            average = slice_sum / non_zero_count
        else:
            average = 0
        result.append(average)
    return result

def calculate_average(sensordata_dict, keys_of_interest):
    total = 0
    count_non_zero = 0

    for key in keys_of_interest:
        if key in sensordata_dict:
            value = sensordata_dict[key]
            if value != 0:
                total += value
                count_non_zero += 1

    if count_non_zero > 0:
        average = total / count_non_zero
    else:
        average = 0

    return average

def run_thread(schema_collection, device_data, value_device,device_collection,get_id_device):
    last_sent_time = datetime.now()
    last_check_time = datetime.now()
    first_run = True 
    first_run2 = True
    print("Connect success!\n")
    while True:
        slave_id = device_data['slaveid']
        current_time = datetime.now()

        try:
            doc,val = find_register(schema_collection, device_data,value_device,slave_id,first_run,last_sent_time)
            avg_value_dict = process_sensor_data(val)
            sensor_name =["current_average","active_power_average","power_factor_average","voltage_average",]
            
            if slave_id == 3:
                if first_run or current_time >= last_sent_time:
                    sensordata_dict = dict(zip(sensor_name,avg_value_dict))
                    doc['sensordata'].update(sensordata_dict)
                    value_device.insert_one(doc)
                    last_sent_time = next_hour()
                    first_run = False
            else:
                if first_run or current_time >= last_sent_time:
                    value_device.insert_one(doc)
                    last_sent_time = next_hour()
                    first_run = False

        except (IndexError,ModbusException, ConnectionException) as e:
            print(f'Error: {e}\n')
            
        try: 
            if first_run2 or current_time >= last_check_time:
                find_register(schema_collection, device_data,value_device,slave_id,first_run,last_sent_time)
                device_collection.update_one({"_id": get_id_device, "device_data.slaveid": slave_id},{"$set": {"device_data.$.status": 1}})
                last_check_time = next_second()
                first_run2 = False
                # print("Update status 1!\n")

        except (IndexError,ModbusException, ConnectionException) as e:
            device_collection.update_one({"_id": get_id_device, "device_data.slaveid": slave_id},{"$set": {"device_data.$.status": 0}})
            # print("Update status 0!\n")
            print(f'Error: {e}\n')   

def main():
    client = pymongo.MongoClient("mongodb://localhost:27017")
    db = client['metadata']
    schema_collection = db['device_schema']
    device_collection = db['device']
    value_device = db['device_value']
    for device_doc in device_collection.find({}):
        for device_data in device_doc['device_data']:
            get_id_device = device_doc['_id']
            device_id = device_data['deviceid']
            thr = Thread(target=run_thread, args=(schema_collection, device_data, value_device,device_collection,get_id_device))
            thr.start()

if __name__ == "__main__":
    main()
