
fire_Detection
=============
```
cd ~/(workspace)/src
```
```
git clone https://github.com/KYH04444/fire_Detection.git
```
```
catkin_make
```
```
roscd mavros_off_board && cp quad_f450_camera ~/PX4-Autopilot/Tools/simulation/gazebo-classic/sitl_gazebo-classic/models
```
```
cd ~/(workspace)/src/fire_Detection/world && cp * ~/PX4-Autopilot/Tools/simulation/gazebo-classic/sitl_gazebo-classic/worlds
```
```
cd ~/(workspace)/src/fire_Detection/model && cp * ~/PX4-Autopilot/ROMFS/px4fmu_common/init.d-posix/airframes 
```
```
code CMakeLists.txt
```
 
```(in file: Add the airframe file(1076_gazebo-classic_quad_f450_camera)  at the bottom of the list starting with   px4_add_romfs_files(...))```

```    
cd ~/PX4-Autopilot/src/modules/simulation/simulator_mavlink && code sitl_targets_gazebo-classic.cmake 
```
```(in file: Add the airframe name (quad_f450_camera) which starts with  set(models …)  as-well as the world file grass_pad  to the line starting with   set(worlds... ))```
```
roscd mavros_off_board/worlds/gazebo && cp -r * ~/.gazebo/models/
```


How to RUN
=============
```
roslaunch mavros_off_board mavros_posix_sitl.launch
```
```
roscd fire_detection
```
```
python3 move.py
```

```If you want to change the targeting point.```

```
rostopic pub -1 /target_point fire_detection/TargetPoint "x: 5
y: 5
z: 5"
```

  
    
    
