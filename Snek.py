import os, sys, rgraphics, time, curses, random, urllib.parse, urllib.request
####
class Pastebin():
	def __init__(self,url,key):
		self.url=url
		self.key=key
	def login(self):
		url="https://pastebin.com/api/api_login.php"
		
	def read(self):
		values={
			'api_dev_key':self.key,
			'api_user_key':self.url}
	def new(self,text):
		values={
			'api_option' : 'paste',
			'api_dev_key' : self.key,
			'api_paste_code' : text,
			'api_paste_private' : '1',
			'api_paste_name' : 'RLeaderboards.json',
			'api_paste_expire_date' : 'N',
			'api_paste_format' : 'json',
			'api_user_key' : ''}
		with urllib.request.urlopen(urllib.request.Request("https://pastebin.com/api/api_post.php", urllib.parse.urlencode(values).encode('utf-8'))) as response:	#basically magic
			the_page=response.read().decode("utf-8")
		return the_page
#pb=Pastebin("http://pastebin.com/a78EpLYU",'900b71cfac504560cb7f758c1c3e302a')
#pb.read()
#quit()
####
def on_press(key):
	print("{0} pressed".format(key))
curpath=os.path.abspath(os.path.dirname(__file__))+"/"
screen=rgraphics.graphic()
shds=rgraphics.shds
colr=rgraphics.colr
snek={"posx":15,"posy":15,"length":2,"direction":0}
speed=float(input("How fast do you want to have it?\n"))
if speed<0.3 or speed>10:
	raise ValueError("Speed has to be bigger than 0 and smaller or equal 10.")
def setup():
	global dots, apple, walls, dead, snek, bos, automated
	height=width=30
	if len(sys.argv)>1:
		if sys.argv[-1].startswith("/"):
			f=open(sys.argv[-1],"r")
		elif sys.argv[-1].startswith("./"):
			f=open(curpath+sys.argv[-1][2:],"r")
		else:
			f=open(curpath+sys.argv[-1],"r")
	else:
		f=open(curpath+"default.rsa")
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
			snek["posx"]=int(spawn[1])
			snek["posy"]=int(spawn[0])
		elif line.startswith("screen-height"):
			height=int(line.split("=")[-1])
		elif line.startswith("screen-width"):
			width=int(line.split("=")[-1])
	f.close()
	automated=input("Should the Snake be automated? (y/n)\n")
	if automated.lower()=="n":
		automated=False
	else:
		automated=True
	screen.init(width,height,shds.d)
	os.system("setterm -cursor off")
	bos=[None,None,random.randint(-100,0)*-1]
	dots=[]
	dead=False
setup()
def main(stdscr):
	global dots, apple, walls, dead, snek, bos, automated
	stdscr.nodelay(1)				#sets waiting for key press to none
	while not dead:
		if automated:
			key=autokey()
		else:
			key = stdscr.getch()		#gets key press
		#if key!=-1:
		#	print(key)
		keyfunc(key)				#steers the snek
		move() 						#moves the snake
		wrap() 						#wraps the edges of the screen
		dead=checkdeath(dots+walls) #checks if the snake dies of going into itsef or the walls
		checkapple()				#checks if snake eats apple and sets a new apple and lengthens the snek if true
		checkbos()					#handles the bottle of speed
		timecalc()					#calculates passed time
		scorecalc()					#calculates scores
		draw() 						#renders and displays all objects
		time.sleep(0.1/speed)
def scorecalc():
	global snek
	apples=snek["length"]-2
	snek["finalscore"]=(apples/(snek["time"]/30+1))*(speed**2)*10
def timecalc():
	global snek, starttime
	snek["time"]=time.time()-starttime
def randpos(minx=0,maxx=len(screen.content)-1,miny=0,maxy=len(screen.content[0])-1):
	return [random.randint(minx,maxx),random.randint(miny,maxy)]
def checkapple():
	global apple
	if [snek["posy"],snek["posx"]]==apple:
		apple=randpos()
		while apple in walls+dots:
			apple=randpos()
		snek["length"]+=1
#259↑ 261→ 258↓ 260←
#119W 97 A 115S 100D
def autokey():
	global apple, snek, dots, walls
	deadly=dots+walls
	right=left=up=down=False
	if apple[1]>snek["posx"] and not [snek["posy"],snek["posx"]+1] in deadly:
		right=True
	elif apple[1]<snek["posx"] and not [snek["posy"],snek["posx"]-1] in deadly:
		left=True
	if apple[0]>snek["posy"] and not [snek["posy"]+1,snek["posx"]] in deadly:
		down=True
	elif apple[0]<snek["posy"] and not [snek["posy"]-1,snek["posx"]] in deadly:
		up=True
	if not (right or left or up or down):
		up=not [snek["posy"]-1,snek["posx"]] in deadly
		down=not [snek["posy"]+1,snek["posx"]] in deadly
		left=not [snek["posy"],snek["posx"]-1] in deadly
		right=not [snek["posy"],snek["posx"]+1] in deadly
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
	if up and snek["direction"]!=2:
		return 259
	elif down and snek["direction"]!=0:
		return 258
	elif left and snek["direction"]!=1:
		return 260
	elif right and snek["direction"]!=3:
		return 261
	else:
		if up:
			return 258
		elif down:
			return 259
		elif left:
			return 261
		elif right:
			return 260
def checkbos():
	global bos, speed
	if bos[2]>=0:
		if bos[0:2]==[None,None]:
			bos=randpos()+[0]
		if [snek["posy"],snek["posx"]]==bos[0:2]:
			bos=randpos()+[12]
			while bos in walls+dots:
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
def draw():
	dots.append([snek["posy"],snek["posx"]])
	while len(dots)>snek["length"]:
		dots.pop(0)
	if bos[2]==0:
		try:
			screen.content[bos[0]][bos[1]]=colr.bue+shds.a+colr.rst
		except IndexError:
			raise IndexError("bos="+str(bos)+", doesn't fit into screen.content with is "+str(len(screen.content))+"x"+str(len(screen.content[0]))+" big.")
	try:
		screen.content[apple[0]][apple[1]]=colr.red+shds.a+colr.rst
	except IndexError:
		raise IndexError("apple="+str(apple)+", doesn't fit into screen.content with is "+str(len(screen.content))+"x"+str(len(screen.content[0]))+" big.")
	for dot in dots:
		try:
			screen.content[dot[0]][dot[1]]=colr.grn+shds.a+colr.rst
		except IndexError:
			raise IndexError("\ndot="+str(dot)+"\nlen(screen.content)="+str(len(screen.content)))
	for wall in walls:
		screen.content[wall[0]][wall[1]]=shds.a
	screen.display()
	sys.stdout.write("\033["+str(len(screen.content)+1)+";0H"+shds.d*len(screen.content[0])+"\r"+"Apples: "+str(snek["length"]-2)+"\033[2CTime: "+str(int(snek["time"]))+"\033[2CFinal Score: "+str(int(snek["finalscore"])))
#259↑ 261→ 258↓ 260←
#119W 100D 115S 97 A
def keyfunc(key):
	if key in [259,119] and snek["direction"]!=2:
		snek["direction"]=0
	elif key in [261,100] and snek["direction"]!=3:
		snek["direction"]=1
	elif key in [258,115] and snek["direction"]!=0:
		snek["direction"]=2
	elif key in [260,97] and snek["direction"]!=1:
		snek["direction"]=3
def move():
	if snek["direction"]==2:
		snek["posy"]+=1
	elif snek["direction"]==1:
		snek["posx"]+=1
	elif snek["direction"]==0:
		snek["posy"]-=1
	elif snek["direction"]==3:
		snek["posx"]-=1
def wrap():
	if snek["posx"]>len(screen.content[0])-1:
		snek["posx"]=0
	elif snek["posx"]<0:
		snek["posx"]=len(screen.content[0])-1
	if snek["posy"]>len(screen.content)-1:
		snek["posy"]=0
	elif snek["posy"]<0:
		snek["posy"]=len(screen.content)-1
def checkdeath(deathpos):
	if [snek["posy"],snek["posx"]] in deathpos:
		return True
def die():
	rgraphics.clearscreen()
	apples=snek["length"]-2
	print("\033[1J\rScore: "+str(apples)+" apples in "+str(int(snek["time"]))+" seconds at a speed of "+str(speed)+". That's a total score of "+str(int(snek["finalscore"])))
	os.system("setterm -cursor on")
	input()
starttime=time.time()
try:
	curses.wrapper(main)
except Exception as e:
	rgraphics.clearscreen()
	raise e
die()
