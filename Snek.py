#!/usr/bin/python3
import os, sys, rgraphics, time, curses, random
curpath=os.path.abspath(os.path.dirname(__file__))+"/"
shds=rgraphics.Shades()
colr=rgraphics.Color()
######Snek()#############################################################
class Snek():
	def __init__(self,length=2,posx=15,posy=15,automated=False):
		self.posx=posx
		self.posy=posy
		self.len=length
		self.dir=1
		self.dots=[]
		self.dead=False
		self.automated=automated
		self.t=0
		self.score=0
	def move(self):
		d=self.dir
		if d==0:
			self.posy-=1
		elif d==1:
			self.posx+=1
		elif d==2:
			self.posy+=1
		elif d==3:
			self.posx-=1
	def checkdots(self):
		self.dots.append([snek.posy,snek.posx])
		while len(self.dots)>self.len:
			self.dots.pop(0)
	def drawon(self):
		global screen
		for dot in self.dots:
			screen.content[dot[0]][dot[1]]=rgraphics.Px(colr.grn,shds.a)
	def keyfunc(self,key=None):
		if key in [259,119] and self.dir!=2:
			self.dir=0
		elif key in [261,100] and self.dir!=3:
			self.dir=1
		elif key in [258,115] and self.dir!=0:
			self.dir=2
		elif key in [260,97] and self.dir!=1:
			self.dir=3
	def wrap(self,screen):
		if self.posx>len(screen.content[0])-1:
			self.posx=0
		elif self.posx<0:
			self.posx=len(screen.content[0])-1
		if self.posy>len(screen.content)-1:
			self.posy=0
		elif self.posy<0:
			self.posy=len(screen.content)-1
	def checkdeath(self,deathpos):
		if [self.posy,self.posx] in deathpos:
			return True
	def checkapple(self,apple):
		global walls
		if apple==[self.posy,self.posx]:
			apple=randpos()
			while apple in walls+self.dots:
				apple=randpos()
			self.len+=1
		return apple
	def checkbos(self,bos):
		global speed
		if bos[2]>=0:
			if bos[0:2]==[None,None]:
				bos=randpos()+[0]
			if bos[0:2]==[snek.posy,snek.posx]:
				bos=randpos()+[12]
				while bos in walls+self.dots:
					bos=randpos()+[12]
			if bos[2]==12:
				speed*=1.5
			elif bos[2]==1:
				speed/=1.5
				bos[2]=random.randint(-100,0)
			if bos[2]>0:
				bos[2]-=1
		else:
			bos[2]+=1
		return bos
	def scorecalc(self):
		global speed
		apples=self.len-2
		self.score=(apples/(self.t**(1/(snek.t+1))))*(speed**2)
	def timecalc(self):
		global starttime
		self.t=time.time()-starttime
	def die(self):
		rgraphics.clearscreen()
		apples=self.len-2
		print("\033[1J\rScore: "+str(apples)+" apples in "+str(int(self.t))+" seconds at a speed of "+str(speed)+". That's a total score of "+str(int(self.score)))
		os.system("setterm -cursor on")
		input()
####setup()#############################################################################
def setup(interactive:bool=False):
	global dots, apple, walls, dead, snek, bos, automated, speed, screen
	snek=Snek()
	if interactive:
		speed=float(input("How fast do you want to have it?\n"))
	else:
		speed=10.0
	if speed<0.3 or speed>10.0:
		raise ValueError("Speed has to be bigger or equal 0.3 and smaller or equal 10.")
	height=width=30
	if interactive:
		if len(sys.argv)>1:
			if sys.argv[-1].startswith("/"):
				f=open(sys.argv[-1],"r")
			elif sys.argv[-1].startswith("./"):
				f=open(curpath+sys.argv[-1][2:],"r")
			else:
				f=open(curpath+sys.argv[-1],"r")
		else:
			try:
				f=open(curpath+input("What map should be used?\n")+".rsa")
			except OSError:
				print("Doesn't exist, using default map.")
				f=open(curpath+"default.rsa")
	else:
		f=open(curpath+"closed.rsa")
	arena=f.read().lower().split("\n")
	for line in arena:
		if line.startswith("walls"):
			walls=[]
			prewalls=line.split("=")[1].split(",")
			if prewalls!=[""]:
				for prewall in prewalls:
					prewall=prewall.split("&")
					wall=[]
					for pos in prewall:
						wall.append(int(pos))
					walls.append(wall)
			else:
				walls=[]
		elif line.startswith("apple"):
			apple=[]
			prapple=line.split("=")[-1].split("&")
			for pos in prapple:
				apple.append(int(pos))
		elif line.startswith("spawn"):
			spawn=line.split("=")[-1].split("&")
			snek.posx=int(spawn[1])
			snek.posy=int(spawn[0])
		elif line.startswith("screen-height"):
			height=int(line.split("=")[-1])
		elif line.startswith("screen-width"):
			width=int(line.split("=")[-1])
	f.close()
	screen=rgraphics.Graphic(height=height,width=width)
	if interactive:
		snek.automated=input("Should the Snake be automated? (y/n)\n")
		if snek.automated.lower()=="n":
			snek.automated=False
		else:
			snek.automated=True
		os.system("setterm -cursor off")
	else:
		snek.automated=True
	bos=[None,None,random.randint(-100,0)*-1]
if __name__=="__main__":
	setup(interactive=True)
else:
	setup(interactive=False)
####main(######)########################################################################
def main(stdscr):
	global apple, walls, snek, bos, screen
	stdscr.nodelay(True)							#sets waiting for key press to none
	while not snek.dead:
		if snek.automated:
			key=autokey()
		else:
			key = stdscr.getch()					#gets key press
		snek.keyfunc(key)							#steers the snek
		snek.move() 								#moves the snake
		snek.wrap(screen) 							#wraps the edges of the screen
		snek.dead=snek.checkdeath(snek.dots+walls)	#checks if the snake dies of going into itsef or the walls
		apple=snek.checkapple(apple)				#checks if snake eats apple and sets a new apple and lengthens the snek if true
		bos=snek.checkbos(bos)						#handles the bottle of speed
		snek.timecalc()								#calculates passed time
		snek.scorecalc()							#calculates scores
		snek.checkdots()
		snek.drawon() 								#renders and displays all objects
		draw()
		time.sleep(0.1/speed)
####randpos(######################################################################)#####
def randpos(minx=0,maxx=len(screen.content)-1,miny=0,maxy=len(screen.content[0])-1):
	return [random.randint(minx,maxx),random.randint(miny,maxy)]
#259↑ 261→ 258↓ 260←
#119W 97 A 115S 100D
####autokey()###########################################################################
def autokey():
	global apple, snek,walls
	deadly=snek.dots+walls
	right=left=up=down=False
	if apple[1]>snek.posx and not [snek.posy,snek.posx+1] in deadly:
		right=True
	elif apple[1]<snek.posx and not [snek.posy,snek.posx-1] in deadly:
		left=True
	if apple[0]>snek.posy and not [snek.posy+1,snek.posx] in deadly:
		down=True
	elif apple[0]<snek.posy and not [snek.posy-1,snek.posx] in deadly:
		up=True
	if not (right or left or up or down):
		up=not [snek.posy-1,snek.posx] in deadly
		down=not [snek.posy+1,snek.posx] in deadly
		left=not [snek.posy,snek.posx-1] in deadly
		right=not [snek.posy,snek.posx+1] in deadly
	if up and down:
		down=random.choice([True,False])
		up=not down
	if up and right:
		right=random.choice([True,False])
		up=not right
	if up and left:
		left=random.choice([True,False])
		up=not left
	if left and right:                                        																		
		right=random.choice([True,False])
		left=not right
	if left and down:
		down=random.choice([True,False])
		left=not down
	if down and right:
		down=random.choice([True,False])
		right=not down
	if up and snek.dir!=2:
		return 259
	elif down and snek.dir!=0:
		return 258
	elif left and snek.dir!=1:
		return 260
	elif right and snek.dir!=3:
		return 261
	else:
		if up:
			return 259
		elif down:
			return 258
		elif left:
			return 260
		elif right:
			return 261
		else:
			return 0
####draw()##############################################################################
def draw():
	if bos[2]==0:
		screen.content[bos[0]][bos[1]]=rgraphics.Px(colr.bue,shds.a)
	screen.content[apple[0]][apple[1]]=rgraphics.Px(colr.red,shds.a)
	for wall in walls:
		screen.content[wall[0]][wall[1]]=rgraphics.Px(colr.wht,shds.a)
	screen.display()
	towrite="\033[0m\033["+str(len(screen.content)+1)+";0H\rApples: "+str(snek.len-2)+"  Time: "+str(int(snek.t))+"  Final Score: "+str(int(snek.score))
	sys.stdout.write(towrite+" "*(59-(len(screen.content[0])+len(str(snek.len-2)+str(int(snek.t))+str(int(snek.score))))))
def findonmap(y,x):	#returns 0 for nothing, 1 for apple, 2 for boost, -1 for snake and -2 for wall
	if apple==(y,x):
		return 1
	elif bos==(y,x,0):
		return 2
	elif (y,x) in snek.dots:
		return -1
	elif (y,x) in walls:
		return -2
	else:
		return 0
def start():
	global starttime
	starttime=time.time()
	try:
		curses.wrapper(main)
	except KeyboardInterrupt:
		rgraphics.clearscreen()
	try:
		snek.die()
	except KeyboardInterrupt:
		quit()
#259↑ 261→ 258↓ 260←
#119W 100D 115S 97 A
if __name__=="__main__":
	start()
