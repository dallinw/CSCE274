import state_interface
import threading
import random
import logging

#Global Constants
MOVING = False # Is the robot currently moving
LOWANG = -30 # Lowest number in range
HIGHANG = 30 # Highest number in range
TURNANG = 180 # Default angle for robot to turn when it bumbs/detects a cliff
SPEED = 100 # Speed to use for all robot movements
sp = 700 # Set point
pe = 0 # Past Error
le = 0 # Last Error
st = .5 # Sampling Time
kp = .016 # Proportional Gain
kd = .002 # Derivative Gain
LSPEED = 0
RSPEED = 0

# - PID Controller - Returns a value based off of sensor data.  Returned value determines what to do
def pd():
  global le
  global pe
  e = sp - connection.read_light_right() - 10*connection.read_light_front_right() - 10*connection.read_light_center_right() #Error
  P = kp*e     					# Proportional Controller
  D = kd*( e - le )/st      	# Derivative Controller
  u = P  + D     	  			# Controller Output
  le = e						# Updates last error
  return int(u)			  	


def FollowWall():
  global MOVING
  global LSPEED
  global RSPEED
  charging = read_charging_state()
  dock = read_charge_souce_available()
  if dock is not 0 or charging is not 0:
    #stop moving
    #turn the robot off
    #sys.exit()
    #sleep?
  elif dock is 0 or charging is 0:
    while MOVING:
      # Reset driving speed to drive straight every iteration after the correction.
      LSPEED = 50
      RSPEED = 50
      ir_omni = read_ir_omni()
      ir_right = read_ir_right()
      ir_left = read_ir_left()
      charging2 = read_charging_state()
      dock2 = read_charge_source_available()
      connection.drive_direct(RSPEED,LSPEED)
      wheelDrop,bumpRight,bumpLeft = connection.bump_wheel_drop()

      if charging2 is not 0 or dock is not 0:
        #stop moving
        #turn the robot off
        #sys.exit()?
        #sleep?
      elif wheelDrop:
        connection.stop()
        connection.song()
        MOVING = False
        break
      elif cliff != 0:
        connection.stop()
        connection.obstacle()
      elif bumpLeft:
        connection.stop()
        connection.turnClockwise()
      elif bumpRight:
        connection.stop()
        connection.turnCounterClockwise()
      elif bumpLeft and bumpRight:
        connection.stop()
        connection.obstacle()
      #elif something about checking infrared sensors
      #elif something about diffeent infrared values
      #how many elif do we need? Answe: Gotta test to figure it out
      #what to do if all the omni values are 0? <<<< Does this matter? If we say drive(x,y) its overwitten immediately by the wall algorithm
    
      # Call to the PD controller. Most of these values have been tweaked using trial and error along multiple wall designs. USE THIS UNTIL INFARED IS DETECTED
      u = pd()
      if u > 14:
        LSPEED = 30
        RSPEED = 20
      elif (u >= 9 and u <= 11):
        LSPEED = 150 + u
        RSPEED = 35 - u
      else:
        LSPEED = 35 + u
        RSPEED = 35 - u
      if MOVING:
        connection.drive_direct(RSPEED,LSPEED)
        connection.tpause(st)

connection = state_interface.Interface()
connection.set_full()

while True: 
  cleanDetect = connection.read_button(connection.getClean())
  wheelDrop, bumpLeft, bumpRight = connection.bump_wheel_drop()
  cliff = connection.read_cliff()

  if not MOVING and not wheelDrop and cliff == 0 and cleanDetect:
    myThread = threading.Thread(target=FollowWall)
    MOVING = True
    myThread.start()
  elif MOVING and cleanDetect:
    MOVING = False
    connection.stop()
