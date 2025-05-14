import sys
from xensesdk.omni.widgets import ExampleView
from xensesdk.xenseInterface.XenseSensor import Sensor


def main(data_path):
    sensor_0 = Sensor.create(
        data_path, 
        config_path= r"/home/xuckham07/xense_dp/config_0.2.1/QJ-SW-096"
    )

    View = ExampleView(sensor_0)
    View2d = View.create2d(Sensor.OutputType.Rectify, Sensor.OutputType.Depth)
    
    def callback():
        src, depth= sensor_0.selectSensorInfo(Sensor.OutputType.Rectify, Sensor.OutputType.Depth)
        View2d.setData(Sensor.OutputType.Rectify, src)
        View2d.setData(Sensor.OutputType.Depth, depth)
        View.setDepth(depth)
    View.setCallback(callback)

    View.show()
    sensor_0.release()
    sys.exit()

if __name__ == '__main__':
    data_path = r"/home/xuckham07/xense_dp/raw_data/test_xensegdk/batch_20250425_165203/sensor_4_rectify_video_2025_04_25_16_52_03.mp4"
    main(data_path)