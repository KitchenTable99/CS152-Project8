#Caleb Bitting
#CS152
#Project8
#Bruce and Caitrin
#

# Importing the necessary libraries
import graphicsPlus as gr
import statistics
import time
import math
import random

# Creating global variables
check_blocks = set()
hit_blocks = set()

# Defining classes
class Paddle(gr.Rectangle):

	# Basic init method
	def __init__(self):
		super().__init__(gr.Point(514, 1), gr.Point(685, 19))		# Initialize paddle in the middle of the screen and set its fill
		self.setFill(gr.color_rgb(189, 77, 201))
		self._length = 171

	# Moves the Paddle left
	def moveLeft(self):
		self.move(-20, 0)
		if self.p1.x < 1:						# If the paddle would move off the screen, don't let it
			correction_dist =  1 - self.p1.x
			self.move(correction_dist, 0)

	# Moves the Paddle right
	def moveRight(self):
		self.move(20, 0)
		if self.p2.x > 1199:					# If the paddle would move off the screen, don't let it
			correction_dist =  1199 - self.p2.x
			self.move(correction_dist, 0)

	# Returns the leftmost x-coordinate of the paddle
	def getLeft(self): return self.getCenter().getX() - self._length/2

	# Returns the rightmost x-coordinate of the paddle
	def getRight(self): return self.getCenter().getX() + self._length/2

	# Puts the Paddle back in the middle of the screen
	def recenter(self):
		current_p1 = self.getP1()
		dx = 514 - current_p1.getX()
		self.move(dx, 0)

	def pointPosition(self, Pointer):
		'''Given the Pointer object, this function returns a string of the zone in which the Pointer made contact from the options 'left', 'right', or 'center'.'''
		self_center = self.getCenter()
		left_divider = self_center.getX() - (self._length/6)
		right_divider = self_center.getX() + (self._length/6)
		center_x = Pointer.getCenter().getX()
		if center_x < left_divider:
			return 'left'
		elif center_x > right_divider:
			return 'right'
		else:
			return 'middle'

class Block(gr.Rectangle):

	# Give this class access to a couple global variable
	global hit_blocks
	global check_blocks
	global blocks

	height = 32		# Standard height and width
	width = 85.5

	def __init__(self, row_num, rect_num):
		self.center_x = (rect_num+.5)*self.width			# Doing mathematical wizardry to find the needed points to pass to the __init__ method of gr.Rectangle
		self.center_y = 800 - (4.5+abs(row_num-5))*self.height
		p1 = gr.Point((self.center_x - self.width/2), (self.center_y - self.height/2))
		p2 = gr.Point((self.center_x + self.width/2), (self.center_y + self.height/2))
		super().__init__(p1, p2)
		self.colorize(row_num)
		self.row_num = row_num
		self.rect_num = rect_num

	def getRow(self): return self.row_num

	def colorize(self, row_num):
		'''Set the color of the blocks based on their row.'''
		if row_num == 0:
			self.setFill(gr.color_rgb(104, 105, 246))
		elif row_num == 1:
			self.setFill(gr.color_rgb(80, 172, 58))
		elif row_num == 2:
			self.setFill(gr.color_rgb(241, 150, 63))
		elif row_num == 3:
			self.setFill(gr.color_rgb(240, 135, 60))
		elif row_num == 4:
			self.setFill(gr.color_rgb(232, 95, 91))
		else:
			self.setFill(gr.color_rgb(189, 77, 29))

	def getBoundingBox(self):
		'''Returns a tuple containing the high and low values of the rectangle's bounding box.'''
		low_x = self.center_x - self.width/2
		high_x = self.center_x + self.width/2
		low_y = self.center_y - self.height/2
		high_y = self.center_y + self.height/2
		return (low_x, high_x, low_y, high_y)

	def remove(self):
		'''The logic surrounding the removal of a block.'''
		self.undraw()		# First undraw the block
		hit_blocks.add(self)	# Add it to a set of blocks that have already been hit
		check_blocks.discard(self)		# Remove it from the set of blocks to check for a collision
		try_add = []
		target_row = self.row_num 			# Extracting the necessary information
		target_rect = self.rect_num

		# Attempt to add the four boxes directly neighboring the one that just got hit by the Pointer. Some logic is needed to handle both wraparound cases and IndexErrors
		if target_row - 1 >= 0:
			try_add.append(blocks[target_row-1][target_rect])
		try:
			try_add.append(blocks[target_row][target_rect+1])
		except IndexError:
			pass
		if target_rect - 1 >= 0:
			try_add.append(blocks[target_row][target_rect-1])
		try:
			try_add.append(blocks[target_row+1][target_rect])
		except IndexError as e:
			pass

		# Don't add a block that has already been hit to the list of blocks to check
		for attempt in try_add:
			if attempt not in hit_blocks:
				check_blocks.add(attempt)

	def __and__(self, other):
		'''Checks to see whether the Pointer and Block collided and, if so, returns a tuple of True and which axis over which to reverse.
		   If no collision—Trump brags about exhoneration—I mean, returns (False, None)'''
		low_x, high_x, low_y, high_y = self.getBoundingBox()
		check_points = other.collisionPoints()
		collide = False
		for point in check_points:
			if point.x >= low_x and point.x <= high_x and point.y >=low_y and point.y <= high_y:
				collide = True
				break
		if collide:
			# Check to see which line the point collided with
			dist_x1 = abs(point.x - self.p1.x)
			dist_x2 = abs(point.x - self.p2.x)
			dist_y1 = abs(point.y - self.p1.y)
			dist_y2 = abs(point.y - self.p2.y)
			smallest = min([dist_x1, dist_x2, dist_y1, dist_y2])
			# The guilty point collided with either a vertical line
			if smallest == dist_x1 or smallest == dist_x2:
				return (True, 'x') # In which case we need to reverse the x-velocity
			else:
				return (True, 'y') # Or a horizontal line so we need to reverse the y-velocity
		else:
			return (False, None)

	__rand__ = __and__

	# Debugging stuff
	def __repr__(self):
		return f'Block({self.row_num}, {self.rect_num})'

class Pointer(gr.Rectangle):

	side = 18		# Setting the side length and initial velocity
	velocity_0 = 4

	def __init__(self, paddle_object):
		super().__init__(gr.Point(591, 19), gr.Point(609, 37))
		self.setFill(gr.color_rgb(189, 77, 201))
		self.velocity = [0, 0]
		self._paddle = paddle_object		# Takes a private paddle object for ease of methods down the line

	def velocityIncrease(self):
		'''Scales up the velocity by a factor of 4/3.'''
		self.velocity[0] *= (4/3)
		self.velocity[1] *= (4/3)
	
	def launch(self):
		'''Sets the velocity of the pointer from the starting position.'''
		angle = (math.pi/4) + random.random()*(math.pi/2)		# Generates a random angle between 3pi/4 and pi/4
		x_vel = math.cos(angle)*self.velocity_0
		y_vel = math.sin(angle)*self.velocity_0
		self.velocity = [x_vel, y_vel]

	# Reverses the Pointer along the x-axis
	def reverseX(self): self.velocity[0] *= -1

	def reverseY(self, paddle = False):
		'''Reverses the Pointre along the y-axis. If the paddle argument is passed, teleport the Pointer up a couple pixels.'''
		if paddle:		# This is to avoid the Pointer from glitching and getting stuck on the Paddle
			self.move(0, 3)
		self.velocity[1] *= -1

	def checkCollisions(self):
		'''This function checks for collisions and handles the necessary adjustments.'''
		self._checkBorders()
		self._checkPaddle()
		no_blocks_left = self._checkBlocks()
		if no_blocks_left:		# if the player has won the game return True. Needed for the play loop.
			return True

	def _checkBorders(self):
		'''Check to see if the Pointer has hit one of the sides excluding the bottom, and reverse the velocity if needed.'''
		if self.p1.x < 1 or self.p2.x > 1199:
			self.reverseX()
		elif self.p2.y > 769:
			self.reverseY()
		else:
			pass

	def checkBottom(self): return 1 if self.p1.y < 1 else 0		# Return 1 if the Pointer has hit the bottom and 0 if not

	def _checkPaddle(self):
		'''Check to see if the Pointer and Paddle have collided.'''
		# Get paddle bounding box
		paddle_object = self._paddle
		low_x = paddle_object.p1.x
		high_x = paddle_object.p2.x
		low_y = paddle_object.p1.y
		high_y = paddle_object.p2.y
		# Get Pointer collision points
		check_points = self.collisionPoints(paddle=True)
		# Check for collisions and reverse the directions if needed
		for point in check_points:
			if point.x >= low_x and point.x <= high_x and point.y >=low_y and point.y <= high_y:
				hit_zone = paddle_object.pointPosition(self)
				# Make sure that the Pointer deflects the correct way
				if hit_zone == 'middle':
					self.reverseY(paddle = True)			# Just reverse the y-velocity
				elif hit_zone == 'right':
					self.reverseY(paddle = True)
					abs_x_vel = abs(self.velocity[0])		# Always go back towards the right if the Pointer hits on the right side
					self.velocity[0] = abs_x_vel
				else:
					self.reverseY(paddle = True)			# Go towards the left if the Pointer hits the left side.
					target_x_vel = -1*abs(self.velocity[0])
					self.velocity[0] = target_x_vel
				break

	def _checkBlocks(self):
		'''Check to see if the Pointer has colided with any Block that is in the check_blocks list.'''
		global check_blocks
		for block in check_blocks:
			collision, direction = self & block 		# see Block object for __add__ method
			if collision:								
				break
		try:
			if collision:
				if direction == 'x':
					self.reverseX()
				else:
					self.reverseY()
				block.remove()					# see Block object for remove method
		except UnboundLocalError:
			return True

	def collisionPoints(self, paddle=False):
		'''Returns a list of points to check for collision. If paddle argument is true, this returns the valid points to check for Paddle collisions.'''
		if not paddle:
			point1 = self.p1
			point2 = self.p2
			point3 = gr.Point(self.p1.x, self.p2.y)
			point4 = gr.Point(self.p2.x, self.p1.y)
			return [point1, point2, point3, point4]
		point1 = self.p1
		point2 = gr.Point(self.p2.x, self.p1.y)
		if point1.x > self._paddle.getRight():				# Make sure that the Pointer has not passed the paddle in the x-axis
			return []
		elif point2.x < self._paddle.getLeft():
			return []
		else:
			return [point1, point2]

	def recenter(self):
		'''Recenters the Pointer.'''
		current_p1 = self.getP1()
		dx = 591 - current_p1.getX()
		dy = 18 - current_p1.getY()
		self.move(dx, dy)
		self.velocity = [0, 0]

	def __next__(self):
		'''Moves the Pointer object one time unit.'''
		self.move(self.velocity[0], self.velocity[1])

# Defining functions
def create_blocks():
	'''Returns a nested list of Block objects arranged in 6 rows 14.'''
	global check_blocks
	blocks = []
	for row_num in range(0, 6):
		row  = []
		for rect_num in range(0, 14):
			temp_block = Block(row_num, rect_num)
			row.append(temp_block)
			if row_num == 0 or row_num == 5:		# Put the bottom and row of blocks into a list of possible collision objects
				check_blocks.add(temp_block)
		blocks.append(row)
	return blocks

def addScore(block, score):
	'''This function takes a Block object that has been removed but not scored and a text object representing the score and returns a text object representing the updated score.'''
	row = block.row_num
	if row == 0:
		add_score = 1
	elif row == 1:
		add_score = 1
	elif row == 2:
		add_score = 2
	elif row == 3:
		add_score = 3
	elif row == 4:
		add_score = 5
	else:
		add_score = 8
	return parse_text_obj(score, increment=add_score)

def loseLife(pointer_obj, paddle_obj, life_obj):
	'''This function 'resets' the screen by centering the paddle_obj and pointer_obj and updates the life_obj to reflect the loss of life. If the player loses their last life, this returns 'dead'.'''
	paddle_obj.recenter()
	pointer_obj.recenter()
	life_obj = parse_text_obj(life_obj, increment=-1)		# Decrement the lives and end the game if there are no more lives
	current_life = parse_text_obj(life_obj)
	if current_life == 0:
		return 'dead'

def wait_for_space(window, pointer_obj, starting_text):
	'''This function waits for the user to press space and then launches the Pointer.'''
	started = False
	while not started:
		key = window.checkKey()
		if key == 'space':
			started = True
			pointer_obj.launch() 		# Start the pointer off with some velocity
			next(pointer_obj)
			starting_text.undraw()
		else:
			time.sleep(.01)
		window.update()

def play_loop(window, paddle_obj, pointer_obj, score_obj, collide_blocks):
	
	# Play!
	scored_blocks = set()
	done = False
	increase1 = False
	increase2 = False
	while done == False:
		# Moves the paddle
		key = window.checkKey()
		if key == 'Left':
			paddle_obj.moveLeft()
		elif key == 'Right':
			paddle_obj.moveRight()

		# Advances the pointer and checks for collisions	
		next(pointer_obj)
		window.update()
		blocks_gone = pointer_obj.checkCollisions()
		bottom_collision = pointer_obj.checkBottom()
		
		# Handles any hit blocks
		for block in collide_blocks:
			if block not in scored_blocks:
				addScore(block, score_obj)
				scored_blocks.add(block)

		# Handles needed increases in velocity
		if len(collide_blocks) == 4 and increase1 == False:
			pointer_obj.velocityIncrease()
			increase1 = True
		if len(collide_blocks) == 12 and increase2 == False:
			pointer_obj.velocityIncrease()
			increase2 = True

		# Necessary delay
		time.sleep(.01)

		# Manual quit key
		if key == 'q':
			done = True

		# Checking for exit conditions and returning one if found
		if bottom_collision:
			return 'bottom'
		if blocks_gone:
			return 'blocks gone'

def parse_text_obj(text_obj, increment=None):
	'''This function returns the number at the end of the text_object passed to it. If an incriment is passed, this function will instead return the text_obj with the increment performed.'''
	raw_text = text_obj.getText()
	space_index = raw_text.index(' ')
	current_num = int(raw_text[space_index:])
	if increment == None:
		return current_num
	else:
		current_num += increment
		temp_text = raw_text[:space_index]
		new_text = temp_text + ' ' + str(current_num)
		text_obj.setText(new_text)
		return text_obj

# Calling a function
blocks = create_blocks()

def main():

	# Intializing all the necessary objects and drawing them
	global blocks
	global hit_blocks
	# Create the window
	win = gr.GraphWin('Atari 2600: Breakout', 1200, 800, False)
	win.setBackground('black')
	win.setCoords(0, 0, 1200, 800)
	# Separating line for header
	line = gr.Line(gr.Point(0, 770), gr.Point(1200, 770))
	line.setOutline('white')
	line.draw(win)
	# Create life counter and score
	life_counter = gr.Text(gr.Point(70, 785), 'Lives: 3')
	score = gr.Text(gr.Point(1115, 785), 'Score:   0')
	# Format the text items
	for text in [life_counter, score]:
		text.setTextColor('white')
		text.setSize(24)
		text.setFace('courier')
		text.draw(win)
	# Initialize the Paddle
	pad = Paddle()
	pad.draw(win)
	# Initialize the Blocks
	for row in blocks:
		for block in row:
			block.draw(win)
	# Initialize the Pointer
	pointer = Pointer(pad)
	pointer.draw(win)
	#Put up the starting instruction
	press = gr.Text(gr.Point(600, 350), 'Press Space to start....')
	press.setSize(36)
	press.setFace('courier')
	press.setTextColor('white')
	press.draw(win)




	# The actual game loop
	game = 'start'
	real_end = 'not dead'
	while game != 'over':
		wait_for_space(win, pointer, press)
		end_condition = play_loop(win, pad, pointer, score, hit_blocks)
		if end_condition == 'bottom':
			real_end = loseLife(pointer, pad, life_counter)
		elif end_condition == 'blocks gone':
			game = 'over'
		if real_end == 'dead':
			break




	# Display appropriate end screen
	for row in blocks:
		for block in row:
			block.undraw()
	winning = gr.Text(gr.Point(600, 375), 'You win!!!')
	winning.setSize(36)
	winning.setFace('courier')
	if parse_text_obj(score) > 280:
		winning.setTextColor('lime green')
	else:
		winning.setText('You lose :((')
		winning.setTextColor('red')
	winning.draw(win)
	win.update()
	time.sleep(3)
	click_to_close = gr.Text(gr.Point(600, 100), 'Click to close')
	click_to_close.setSize(18)
	click_to_close.setFace('courier')
	click_to_close.setTextColor('white')
	click_to_close.draw(win)
	win.update()
	win.getMouse()

if __name__ == '__main__':
	main()