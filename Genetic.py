import random,copy,pickle,rgraphics,os,curses,sys
from time import time, sleep
import Snek as snek

class Synapse():
	def __init__(self,num:float=random.random(),op:"list of int"=None,connect:list=[]):
		self.n=num
		self._n=num
		if op==None:
			self.op=[random.choice((0,1,2,3,4,5)) for x in range(len(connect))]	#None, +, -, *, /, =
		else:
			self.op=op
		self.c=connect
	def fire(self):
		x=0
		for connection in self.c:
			try:
				self.operate(connection.n,x)
			except:
				pass
			x+=1
	def operate(self,value,x):
		op=self.op[x]
		if op==0:
			return
		elif op==1:
			self.n+=value
		elif op==2:
			self.n-=value
		elif op==3:
			self.n*=value
		elif op==4:
			self.n/=value	#I really don't want the AI to do this, because it just consumes so much processing power, but I gotta give it freedom.
		elif op==5:
			self.n=value
	def mutate(self,rate):
		self._n=self._n+rate*(random.random()*2-1)
		self.n=self._n
		self.op=[random.choice((0,1,2,3,4,5)) if random.random()<rate else operation for operation in self.op]

class Network():
	def __init__(self,layers_syns:list=[32,32,32,30,30,28,28,26,26,24,24,20,20,20,18,18,16,16,12,12,10,10,10,5,5,5,5,4,4,4,3,3,2]):
		self.layers=[]
		for syn_count in layers_syns:
			self.layerplus(syn_count)
		self.nice=0
	def layerplus(self,i:int):
		self.layers.append([Synapse(connect=self.getlastlayersyns()) for x in range(i)])
	def getlastlayersyns(self):
		try:
			return [self.layers[-1][y] for y in range(len(self.layers[-1]))]
		except IndexError:
			return []
	def react(self,inpot:list):
		for index in range(len(inpot)):
			self.layers[0][index].n=inpot[index]
		for layer in self.layers:
			for synapse in layer:
				synapse.fire()
		return (self.layers[-1][0],self.layers[-1][1])
	def mutate(self,rate):
		for layer in self.layers:
			for synapse in layer:
				synapse.mutate(rate)

class Pool():
	def __init__(self,pop_count:int=100,elite_size:int=5,mutation_rate:float=0.1,name:str="default",load_from_file:bool=True):
		self.name=name.lower()
		self.elite_size=elite_size
		self.rate=mutation_rate
		self.pop_count=pop_count
		try:
			if not load_from_file:
				raise OSError()
			else:
				self.load()
		except OSError:
			self.pop=[Network() for x in range(pop_count)]
	def evolve(self,rate):
		elite=[]
		highestnice=0
		self.pop.sort(key=self._sortbynice,reverse=True)
		for x in range(self.elite_size):
			elite.append(self.pop.pop(0))
		self.pop=self.pop[:self.pop_count]
		self.pop=copy.deepcopy(elite)+self.pop+copy.deepcopy(self.pop)
		for nw in self.pop:
			nw.mutate(rate)
		self.pop=elite+self.pop
		self.pop.sort(key=self._sortbynice,reverse=True)
		self.pop=self.pop[:self.pop_count]
	def _sortbynice(self,item):
		return item.nice
	def dump(self):
		self.pop.sort(key=self._sortbynice,reverse=True)
		with open(".genetic_pool_"+self.name+".pkl","wb") as f:
			pickle.dump(self.pop,f,pickle.HIGHEST_PROTOCOL)
		with open(".best_net_"+self.name+".pkl","wb") as f:
			pickle.dump(self.pop[0],f,pickle.HIGHEST_PROTOCOL)
	def load(self):
		with open(".genetic_pool_"+self.name+".pkl","rb") as f:
			self.pop=pickle.load(f)
		
class Snek_Manager():
	def __init__(self):
		self.pool=Pool()
	def snek_main(self,stdscr,cycle,starttime):
		while not snek.snek.dead:
			key=self.autokey(cycle)
			snek.snek.keyfunc(key)							#steers the snek
			snek.snek.move() 								#moves the snake
			snek.snek.wrap(snek.screen) 							#wraps the edges of the screen
			snek.snek.dead=snek.snek.checkdeath(snek.snek.dots+snek.walls)	#checks if the snake dies of going into itsef or the walls
			snek.apple=snek.snek.checkapple(snek.apple)				#checks if snake eats apple and sets a new apple and lengthens the snek if true
			snek.bos=snek.snek.checkbos(snek.bos)						#handles the bottle of speed
			snek.snek.timecalc()								#calculates passed time
			snek.snek.scorecalc()							#calculates scores
			snek.snek.checkdots()
			snek.snek.drawon() 								#renders and displays all objects
			snek.draw()
			sys.stdout.write("\n\r"+str(cycle)+"/"+str(len(self.pool.pop))+"    "+str(self.gen)+"  ")
			if snek.snek.len<=2 and snek.snek.t>=5:
				snek.snek.dead=True
			#sleep(0.1/snek.speed)
		return snek.snek.score
	def main(self,stdscr):
		stdscr.nodelay(True)							#sets waiting for key press to none
		self.gen=0
		while True:
			for cycle in range(len(self.pool.pop)):
				snek.starttime=time()
				self.pool.pop[cycle].nice=self.snek_main(stdscr,cycle,snek.starttime)
				snek.snek=snek.Snek()
				snek.apple=snek.randpos()
				snek.bos=snek.randpos()+[0]
			self.pool.evolve(0.01)
			self.pool.dump()
			self.gen+=1
			
	def autokey(self,cycle):
		inpot=[snek.snek.posx,snek.snek.posy,snek.snek.dir,snek.apple[0],snek.apple[1],snek.bos[0],snek.bos[1]]
		for x in range(snek.snek.posx-2,snek.snek.posx+3):
			for y in range(snek.snek.posy-2,snek.snek.posy+3):
				inpot.append(snek.findonmap(y,x))		#appends a 5x5 radius around the snake to the input
		syn0,syn1=self.pool.pop[cycle].react(inpot)
		if syn0.n<0 and syn1.n<0:
			return 259			#up
		elif syn0.n<0 and syn1.n>0:
			return 258			#down
		elif syn0.n>0 and syn1.n<0:
			return 260			#left
		elif syn0.n>0 and syn1.n>0:
			return 261			#right
		else:
			return 0			#none
		
		
if __name__=="__main__":
	snekman=Snek_Manager()
	try:
		curses.wrapper(snekman.main)
	except KeyboardInterrupt:
		pass
	finally:
		rgraphics.clearscreen()
		os.system("setterm -cursor on")


