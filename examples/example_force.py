import sys
from xensesdk.omni.widgets import ExampleView
from xensesdk.xenseInterface.XenseSensor import Sensor


def main():
    sensor_0 = Sensor.create(4, config_path= r"/home/xuckham07/xense_dp/config_0.2.1/QJ-SW-096",check_serial=False)
    View = ExampleView(sensor_0)
    View2d = View.create2d(Sensor.OutputType.Rectify, Sensor.OutputType.Depth, Sensor.OutputType.Marker2D)

    def callback():
        force, mesh_init, src, depth = sensor_0.selectSensorInfo(
            Sensor.OutputType.ForceNorm, 
            Sensor.OutputType.Mesh3DInit,
            Sensor.OutputType.Rectify, 
            Sensor.OutputType.Depth,
        )
        marker_img = sensor_0.drawMarkerMove(src)
        View2d.setData(Sensor.OutputType.Marker2D, marker_img)
        View2d.setData(Sensor.OutputType.Rectify, src)
        View2d.setData(Sensor.OutputType.Depth, depth)
        View.setForceFlow(mesh_init, force)
        View.setDepth(depth)

    View.setCallback(callback)
    View.show()
    sensor_0.release()
    sys.exit()

if __name__ == '__main__':
    main()