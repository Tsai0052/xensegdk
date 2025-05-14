import h5py

with h5py.File('/home/xuckham07/xense_dp/raw_data/test_xensegdk/batch_20250425_165203/sensor_4_stamped_data_2025_04_25_16_52_03.h5', 'r') as f:
    print("Keys:", list(f.keys()))  # 打印顶层 keys，应该会看到 ['marker_data', 'timestamps']
    
    marker_data = f['marker_data'][:]
    timestamps = f['timestamps'][:]
    
    print("marker_data shape:", marker_data.shape)
    print("marker_data sample:\n", marker_data[-1][0])
    
    print("timestamps shape:", timestamps.shape)
    print("timestamps sample:\n", timestamps[:5])
