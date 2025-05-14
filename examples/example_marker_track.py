import sys
from xensesdk.omni.widgets import ExampleView
from xensesdk.xenseInterface.XenseSensor import Sensor

def main():
    config_num=93
    sensor_0 = Sensor.create(4, config_path= f"/home/xuckham07/xense_dp/config_0.2.1/QJ-SW-0{config_num}",check_serial=False)
    View = ExampleView(sensor_0)
    View2d = View.create2d(Sensor.OutputType.Rectify, Sensor.OutputType.Depth, Sensor.OutputType.Marker2D)

    def callback():
        src, depth, marker3DInit, marker3D = sensor_0.selectSensorInfo(
            Sensor.OutputType.Rectify, 
            Sensor.OutputType.Depth,
            Sensor.OutputType.Marker3DInit, 
            Sensor.OutputType.Marker3D
        )
        marker_img = sensor_0.drawMarkerMove(src)
        View2d.setData(Sensor.OutputType.Marker2D, marker_img)
        View2d.setData(Sensor.OutputType.Rectify, src)
        View2d.setData(Sensor.OutputType.Depth, depth)
        View.setMarker(marker3D)
        View.setMarkerFlow(marker3DInit, marker3D)
        View.setDepth(depth)

    View.setCallback(callback)
    View.show()
    sensor_0.release()
    sys.exit()


if __name__ == '__main__':
    main()