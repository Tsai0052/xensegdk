from xensesdk.xenseInterface.XenseSensor import Sensor
import time 

if __name__ == '__main__':
    sensor = Sensor.create(4, config_path= r"/home/xuckham07/xense_dp/config_0.2.1/QJ-SW-096",check_serial=False)

    sensor.startSaveSensorInfo(r"/home/xuckham07/xense_dp/raw_data/test_record_script", [Sensor.OutputType.Rectify])
    time.sleep(5)
    sensor.stopSaveSensorInfo()
    print("save ok")
    
    sensor.release()
