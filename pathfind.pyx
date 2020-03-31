#!/usr/local/bin/cython
cdef int getdist(pos1:(int,int),pos2:(int,int)):
	return pow((pos1[0]-pos2[0])**2+(pos1[1]-pos2[1])**2,0.5)
def get_path(int posx,int posy,deadly,dest,recursion=0,tries=[0]):
	cdef int focus
	if tries[0]<len(deadly)*10:
		focus=1
	else:
		focus=2
	poss=[(*pos,min(getdist(pos,dest),getdist(pos,(dest[0]-30,dest[1])),getdist(pos,(dest[0]+30,dest[1])),getdist(pos,(dest[0],dest[1]-30)),getdist(pos,(dest[0],dest[1]+30)))) for pos in (((posx-1)%30,posy),((posx+1)%30,posy),(posx,(posy-1)%30),(posx,(posy+1)%30)) if pos not in deadly]
	if len(poss)==0:
		if recursion==0:
			return []
		else:
			deadly.pop()
			return False
	else:
		poss.sort(key=lambda pos:pos[focus])
		for x,y,dist in poss:
			tries[0]+=1
			if dist==0:
				if recursion==0:
					return [(x,y)]
				else:
					return [(x,y),(posx,posy)]
			else:
				if tries[0]>=100000:
					path=[(x,y)]
				else:
					path=get_path(posx=x,posy=y,deadly=deadly[1:]+[(posx,posy)],recursion=recursion+1,dest=dest,tries=tries)
				if path==False:
					pass
				else:
					if recursion!=0:
						path.append((posx,posy))
					return path
		if recursion==0:
			return []
		else:
			return False
