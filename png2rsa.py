#!../../usr/bin/python3.7
import os, sys, png
width,height,pixels,metadata=png.Reader(sys.argv[1]).read()
rowi=0
if metadata["alpha"]:
	rgbcount=4
else:
	rgbcount=3
wallwrite="walls="
applewrite="apple="
spawnwrite="spawn="
widthwrite="screen-width="+str(width)
heightwrite="screen-height="+str(height)
for row in list(pixels):
	row=list(row)
	cycle=0
	x=[]
	for px in row:
		if cycle%rgbcount==0 and cycle!=0:
			spawn=apple=False
			if x[0]>x[1]+x[2]:
				color="\033[32m"
				apple=True
			elif x[1]>x[0]+x[2]:
				color="\033[31m"
				spawn=True
			else:
				color="\033[0m"
			if (x[0]+x[1]+x[2])/3<200:
				sys.stdout.write(color+"#")
				if spawn==True:
					spawnwrite="spawn="+str(rowi)+"&"+str(int(cycle/rgbcount)-1)
				elif apple==True:
					applewrite="apple="+str(rowi)+"&"+str(int(cycle/rgbcount)-1)
				else:
					wallwrite+=str(rowi)+"&"+str(int(cycle/rgbcount)-1)+","
			else:
				sys.stdout.write(" ")
			x=[]
		x.append(px)
		cycle+=1
	print()
	rowi+=1
wallwrite=wallwrite[:-1]
endwrite=wallwrite+"\n"+applewrite+"\n"+spawnwrite+"\n"+widthwrite+"\n"+heightwrite
print(endwrite)
