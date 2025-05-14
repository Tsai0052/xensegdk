from xensesdk.omni.widgets import ExampleView
from xensesdk.xenseInterface.XenseSensor import Sensor
import sys


def main():
    sensor_0 = Sensor.create(4, config_path= r"/home/xuckham07/xense_dp/config_0.2.1/QJ-SW-096")
    View = ExampleView(sensor_0)
    View2d = View.create2d(Sensor.OutputType.Rectify, Sensor.OutputType.Difference, Sensor.OutputType.Depth)
    
    def callback():
        src, diff, depth = sensor_0.selectSensorInfo(Sensor.OutputType.Rectify, Sensor.OutputType.Difference, Sensor.OutputType.Depth)
        View2d.setData(Sensor.OutputType.Rectify, src)
        View2d.setData(Sensor.OutputType.Difference, diff)
        View2d.setData(Sensor.OutputType.Depth, depth)
        View.setDepth(depth)
    View.setCallback(callback)

    View.show()
    sensor_0.release()
    sys.exit()


if __name__ == '__main__':
    main()