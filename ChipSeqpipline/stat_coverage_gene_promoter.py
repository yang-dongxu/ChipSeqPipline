import sys
import os


#usage python thisfile.py outputname  refgene.txt datapoints TSS-5' TTS-3' <bw1 bw2 ...>

if len(sys.argv)<6:
    usage="usage python {} outputname  refbed  <bed1 bed2 ...>".format(__file__)
    print(usage)

outputname=sys.argv[1]
refbed=sys.argv[2]

if len(sys.argv)>3:
    inputfiles=sys.argv[3:]
else:
    inputfiles=sys.stdin.read().split()
    inputfiles=[i.strip() for i in inputfiles]


def process_bedtool_output(bedtool_result,input_filename):
    project=os.path.split(input_filename)[1]
    result_by_line=[]
    for line in bedtool_result:
        lineresult=project+","+",".join(line.split()[-3:-1])
        result_by_line.append(lineresult)
    return '\n'.join(result_by_line)


results=[]
for filename in inputfiles:
    cmd=f"bedtools coverage -a {filename} -b {refbed}"
    result=os.popen(cmd)
    results.append(process_bedtool_output(result,filename))
    print("##"+results[-1])

f=open(outputname,'a')
f.write('\n'.join(results))
f.close()




        
