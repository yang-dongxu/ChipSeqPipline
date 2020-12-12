import os
import sys

#usage python thisfile outputfilename <inputfile1 inputfile2 ...>

if len(sys.argv)<2:
    usage="usage python {} outputfilename <inputfile1 inputfile2 ...>".format(__file__)

outputname=sys.argv[1]

if len(sys.argv)>=3:
    inputfiles=sys.argv[2:]

else:
    names=sys.stdin.read().split()
    inputfiles=[i.strip() for i in names ]


print(f"inputfile:\t{inputfiles}")

with open(outputname,'a' ) as f:
    for file in inputfiles:
        count=0
        if not os.path.exists(file):
            stats=file+","+'0\n'
        else:
            p=open(file,'r')
            for line in p:
                count+=1
            p.close()
            stats=file+','+str(count)+'\n'
        f.write(stats)
        print(stats)

