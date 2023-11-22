
import rospy
from geometry_msgs.msg import PoseStamped, Quaternion
from mavros_msgs.msg import State
from mavros_msgs.srv import CommandBool, CommandBoolRequest, SetMode, SetModeRequest
from sensor_msgs.msg import NavSatFix
from geometry_msgs.msg import Point
from fire_detection.msg import TargetPoint

import math

class OffboardController():
    def __init__(self):
        self.current_state = State()
        self.cnt = 0
        self.current_x = 0
        self.current_y = 0
        self.current_z = 0


        self.radius = 10
        
        self.target_x = 10
        self.target_y = 10
        self.target_z = 5
        
        self.current_target_x = self.target_x
        self.current_target_y = self.target_y
        self.current_target_z = self.target_z

        self.current_yaw = 0.0
        self.distance = 0

        rospy.init_node("fire_detection")
        self.rate = rospy.Rate(20)
        self.state_sub = rospy.Subscriber("/mavros/state", State, callback=self.state_cb)
        self.local_pos_pub = rospy.Publisher("/mavros/setpoint_position/local", PoseStamped, queue_size=10)
        rospy.wait_for_service("/mavros/cmd/arming")
        self.arming_client = rospy.ServiceProxy("/mavros/cmd/arming", CommandBool)
        rospy.wait_for_service("/mavros/set_mode")
        self.set_mode_client = rospy.ServiceProxy("/mavros/set_mode", SetMode)
        rospy.Subscriber("/target_point",TargetPoint, self.retargeting)
        self.pos_sub = rospy.Subscriber("/mavros/local_position/pose", PoseStamped, callback=self.local_position_cb)
        # rospy.Subscriber("/mavros/global_position/global", NavSatFix, callback=self.global2local)
        while not rospy.is_shutdown() and not self.current_state.connected:
            self.rate.sleep() 

        self.run()      

    def retargeting(self, data):
        print("RETARGETING")
        self.target_x = data.x
        self.target_y = data.y
        self.target_z = data.z
        self.cnt = 0
    
    def state_cb(self, msg):
        self.current_state = msg

    def run(self):
        offb_set_mode = SetModeRequest()
        offb_set_mode.custom_mode = 'OFFBOARD'
        arm_cmd = CommandBoolRequest()
        arm_cmd.value = True
        last_req = rospy.Time.now()

        while not rospy.is_shutdown():
            if self.current_state.mode != "OFFBOARD" and (rospy.Time.now() - last_req) > rospy.Duration(5.0):
                if self.set_mode_client.call(offb_set_mode).mode_sent:
                    rospy.loginfo("OFFBOARD enabled")
                last_req = rospy.Time.now()
            else:
                if not self.current_state.armed and (rospy.Time.now() - last_req) > rospy.Duration(5.0):
                    if self.arming_client.call(arm_cmd).success:
                        rospy.loginfo("Vehicle armed")
                    last_req = rospy.Time.now()
            
            pose = self.update_position()
            self.local_pos_pub.publish(pose)
            self.rate.sleep() 

    def local_position_cb(self, data):
        self.current_x = data.pose.position.x
        self.current_y = data.pose.position.y
        self.current_z = data.pose.position.z
           

    def update_position(self):
        self.current_yaw += 0.005
        # self.radius += 0.01
        pose = PoseStamped()
        if self.current_yaw >= 2 * math.pi:
            self.current_yaw = 0.0

        if self.distance_check(self.current_x, self.target_x ,self.current_y, self.target_y,self.current_z, self.target_z) and self.cnt == 0:
            print("within target!")
            self.cnt = 1

        if self.cnt == 0:
            pose = self.target_moving()
        elif self.cnt == 1:
            pose = self.fire_detecting()
        
        return pose

    def distance_check(self, x1, x2, y1 ,y2, z1, z2):
        self.distance = math.sqrt((x1 - x2)**2 + (y1 - y2)**2 + (z1 - z2)**2)
        return self.distance <= 1       

    def target_moving(self):
        pose = PoseStamped()
        pose.pose.position.x = self.target_x
        pose.pose.position.y = self.target_y
        pose.pose.position.z = self.target_z
        return pose

    def fire_detecting(self):
        pose = PoseStamped()
        pose.pose.position.x = self.target_x + self.radius * math.cos(self.current_yaw)
        pose.pose.position.y = self.target_y + self.radius * math.sin(self.current_yaw)
        pose.pose.position.z = self.target_z    
        pose.pose.orientation.x = self.radius *math.cos(self.current_yaw/2+math.pi/4)
        pose.pose.orientation.y = self.radius *math.sin(self.current_yaw/2+math.pi/4)
        return pose
    
if __name__ == "__main__":
    offboard_controller = OffboardController()
