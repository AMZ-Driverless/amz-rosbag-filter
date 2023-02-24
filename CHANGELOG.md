# Changelog

## 2.2 (2022-02-24)

* Improve the way average velocities are calculated - from now only consider timestamps where current velocity is **different from 0**. This means that periods of ROSBags where the car is not moving **do not count towards average velocity**! Average velocity of ROSBag is still 0 if car does not move at all,
* Improve the way of estimating whether sensor data is available by checking `can_msgs/StateMachines` besides just respective (old) message types

## 2.1 (2022-02-22)

* Improve the `README.md`
* Add `amz-rosbag-analyzer` and `amz-rosbag-filter` aliases on the NAS

## 2.0 (2022-02-20)

* Add support for filtering for ROSBags where following sensors are being used:
  * `VE`
  * `IMU`
  * `ASS`
  * `INS`

## 1.1 (2022-02-11)

* Fix issues related to printing the paths of the filtered rosbags with `pandas`
* Minor changes in logging of progress
