from xensesdk.xenseInterface.XenseSensor import Sensor
import time 

if __name__ == '__main__':
    sensor  = Sensor.create(0, config_path="/home/xuckham07/xense_dp/config_0.2.1/QJ-SW-093", check_serial=False)

    sensor.startSaveSensorInfo(r"/home/xuckham07/xense_dp/raw_data/test_example_script", [Sensor.OutputType.Rectify, Sensor.OutputType.Difference])
    time.sleep(10)
    sensor.stopSaveSensorInfo()
    print("save ok")
    
    sensor.release()
