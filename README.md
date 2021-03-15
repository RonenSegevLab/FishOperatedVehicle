# FishOpratedVehicle
### Software And Installation Guide 

- Install ubuntu Raspberry Pi Image from Ubiquity-Robotics:
https://downloads.ubiquityrobotics.com/pi.html
- Create catkin workspace:
http://wiki.ros.org/catkin/Tutorials/create_a_workspace
- Install ROS packages


#### Example for arduino code to control your motors:
###### C++
```C++
#include <SoftwareSerial.h>
#include <PololuQik.h>
#include <ros.h>
#include <geometry_msgs/Twist.h>
ros::NodeHandle nh;
PololuQik2s12v10 qik(11, 10, 4); 
int V = 0;
int U = 0;

void messageCb(const geometry_msgs::Twist& cmd_vel)
{
    digitalWrite(LED_BUILTIN, HIGH-digitalRead(LED_BUILTIN));   // blink the led
    qik.setSpeeds(cmd_vel.linear.x, cmd_vel.linear.y);
}
geometry_msgs::Twist twist_msgs;
ros::Publisher chatter("robotv", &twist_msgs);
ros::Subscriber<geometry_msgs::Twist> sub("/M0M1", messageCb );

void setup()
{
  qik.init();
  nh.initNode();
  nh.subscribe(sub);
}
void loop() {
  nh.spinOnce();
  delay(1);
}
```
