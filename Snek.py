#!/usr/bin/python3
import os, sys, rgraphics, time, curses, random, math
from pathfind import get_path
curpath=os.path.abspath(os.path.dirname(__file__))+"/"
shds=rgraphics.Shades()
colr=rgraphics.Color()
######Snek()#############################################################
class Snek():
	def __init__(self,length=2,posx=15,posy=15,automated=False):
		self.posx=posx%30
		self.posy=posy%30
		self.len=length
		self.dir=1
		self.dots=[((posx-n)%30,posy) for n in range(length-1,-1,-1)]
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
		self.dots.append((snek.posx,snek.posy))
		while len(self.dots)>self.len:
			self.dots.pop(0)
	def drawon(self):
		global screen
		for dot in self.dots:
			screen.content[dot[1]][dot[0]]=rgraphics.Px(colr.grn,shds.a)
	def keyfunc(self,key=None):
		if key in (259,119) and self.dir!=2:	#up
			self.dir=0
		elif key in (261,100) and self.dir!=3:	#right
			self.dir=1
		elif key in (258,115) and self.dir!=0:	#down
			self.dir=2
		elif key in (260,97) and self.dir!=1:	#left
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
	def checkdeath(self,deadly):
		return (self.posx,self.posy) in deadly
	def checkapple(self,apple):
		global walls
		if apple==(self.posx,self.posy):
			apple=randpos(exclude=walls+self.dots)
			self.len+=1
		return apple
	def checkbos(self,bos):
		global speed
		if bos[1]>=0:
			if bos[0]==(None,None):
				bos=[randpos(),0]
			if bos[0]==(snek.posx,snek.posy):
				bos=[randpos(),12]
				while bos[0] in walls+self.dots:
					bos=[randpos(),12]
			if bos[1]==12:
				speed*=1.5
			elif bos[1]==1:
				speed/=1.5
				bos[1]=random.randint(-100,0)
			if bos[1]>0:
				bos[1]-=1
		else:
			bos[1]+=1
		return bos
	def scorecalc(self):
		global speed
		apples=self.len-2
		self.score=(apples-(self.t/10))*(_speed)
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
	global dots, apple, walls, dead, snek, bos, automated, speed, screen, _speed
	snek=Snek()
	if interactive:
		speed=float(input("How fast do you want to have it?\n"))
	else:
		speed=5.0
	_speed=speed
	if speed>=0 and (speed<0.3 or speed>10.0):
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
					walls.append(tuple(wall))
		elif line.startswith("apple"):
			apple=tuple([int(pos) for pos in line.split("=")[-1].split("&")])
		elif line.startswith("spawn"):
			spawn=line.split("=")[-1].split("&")
			snek.posx=int(spawn[0])
			snek.posy=int(spawn[1])
		elif line.startswith("screen-height"):
			height=int(line.split("=")[-1])
		elif line.startswith("screen-width"):
			width=int(line.split("=")[-1])
	f.close()
	screen=rgraphics.Graphic(width=width,height=height)
	if interactive:
		snek.automated=input("Should the Snake be automated? (y/n)\n")
		if snek.automated.lower()=="n":
			snek.automated=False
		else:
			snek.automated=True
		os.system("setterm -cursor off")
	else:
		snek.automated=True
	bos=[(None,None),random.randint(-100,0)*-1]
if __name__=="__main__":
	setup(interactive=True)
else:
	setup(interactive=False)
####main(######)########################################################################
def main(stdscr):
	global apple, walls, snek, bos, screen, apath
	if snek.automated:
		apath=[(snek.posx+1,snek.posy)]
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
		if speed>0:
			time.sleep(0.1/speed)
####randpos()###########################################################################
def randpos(minx=0,maxx=len(screen.content)-1,miny=0,maxy=len(screen.content[0])-1,exclude:tuple=()):
	while True:
		result=(random.randint(minx,maxx),random.randint(miny,maxy))
		if not result in exclude:
			break
	return result
#259↑ 261→ 258↓ 260←
#119W 97A 115S 100D
####autokey()###########################################################################
def autokey():
	global apple, snek, walls, apath, bpath
	sx,sy=snek.posx,snek.posy
	if len(apath)==0:
		apath=get_path(sx,sy,snek.dots+walls,apple)
		if len(apath)==0:
			return 0
	nxx,nxy=apath.pop(-1)
	if nxx==(sx-1)%30 and nxy==sy:
		return 260	#left
	elif nxx==(sx+1)%30 and nxy==sy:
		return 261	#right
	elif nxy==(sy+1)%30 and nxx==sx:
		return 258	#down
	elif nxy==(sy-1)%30 and nxx==sx:
		return 259	#up
	else:
		raise ValueError("Can't jump to %sx%s while being at %sx%s"%(nxx,nxy,sx,sy))

####draw()##############################################################################
def draw():
	if bos[1]==0:
		screen.content[bos[0][1]][bos[0][0]]=rgraphics.Px(colr.bue,shds.a)
	screen.content[apple[1]][apple[0]]=rgraphics.Px(colr.red,shds.a)
	for wall in walls:
		screen.content[wall[1]][wall[0]]=rgraphics.Px(colr.wht,shds.a)
	screen.display()
	towrite="\033[0m\033["+str(len(screen.content)+1)+";0H\rApples: "+str(snek.len-2)+"  Time: "+str(int(snek.t))+"  Final Score: "+str(int(snek.score))
	sys.stdout.write(towrite+" "*(59-(len(screen.content[0])+len(str(snek.len-2)+str(int(snek.t))+str(int(snek.score))))))

def findonmap(x,y):	#returns 0 for nothing, 1 for boost, 2 for apple, -1 for snake and -2 for wall
	x%=30
	y%=30
	pos=(x,y)
	if apple==pos:
		return 2
	elif bos==[pos,0]:
		return 1
	elif pos in snek.dots:
		return -1
	elif pos in walls:
		return -2
	else:
		return 0
	
def start():
	global starttime
	starttime=time.time()
	try:
		curses.wrapper(main)
	except KeyboardInterrupt:
		pass
	snek.die()

#259↑ 261→ 258↓ 260←
#119W 100D 115S 97 A
if __name__=="__main__":
	try:
		start()
	except Exception as e:
		rgraphics.clearscreen()
		raise e
