import sys
from xensesdk.omni.widgets import ExampleView
from xensesdk.xenseInterface.XenseSensor import Sensor


def main():
    sensor_0 = Sensor.create(0, config_path= r"/home/xuckham07/xense_dp/config_0.2.1/QJ-SW-093",check_serial=False)
    View = ExampleView(sensor_0)
    View2d = View.create2d(Sensor.OutputType.Rectify, Sensor.OutputType.MarkerUnorder)

    def callback():
        src, depth, marker_unordered= sensor_0.selectSensorInfo(Sensor.OutputType.Rectify, Sensor.OutputType.Depth, Sensor.OutputType.MarkerUnorder)
        marker_img = sensor_0.drawMarker(src, marker_unordered)
        View2d.setData(Sensor.OutputType.Rectify, src)
        View2d.setData(Sensor.OutputType.MarkerUnorder, marker_img)
        View.setDepth(depth)
        View.setMarkerUnorder(marker_unordered)

    View.setCallback(callback)
    View.show()
    sensor_0.release()
    sys.exit()

if __name__ == '__main__':
    main()