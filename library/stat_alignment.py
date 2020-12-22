# %%
import sys
import os
import re
# %%

log_name=sys.argv[1]
outname=sys.argv[2]


f=open(log_name)
text=f.read()
f.close()

f=open(outname,'w')
columns=["project","total_reads","uniq_mapping_reads","multi_mapping_reads","filtered_reads"]
f.write(",".join(columns)+"\n")

# %%
aligment_pattern="######Start mapping (\S+)######[\s\S]+?(\d+ reads[\s\S]+?alignment rate)\s######Stop mapping (\S+)######"
macs_pattern="######Start peakcalling {project}######[\s\S]+######Stop peakcalling {project}######"
# %%
all_mapping_results=re.findall(aligment_pattern,text)
for p1,body,p2 in all_mapping_results:
    if p1.strip() !=p2.strip():
        continue
    print(p1)

    ### get filtered reads num from macs2 log
    macs_pattern_project=macs_pattern.format(project=p1)
    macs_log=re.findall(macs_pattern_project,text)
    assert len(macs_log)==1
    extract_peak_reads_pattern="fragments after filtering in treatment: (\d+)"
    filtered_reads=re.findall(extract_peak_reads_pattern,macs_log[0])[0]


    ##### get aligment reads num from bowtie2 log
    parts=[i.strip() for i in body.split('----') ]
    if len(parts) != 3:
        continue
    else:
        total_reads=parts[0].split('\n')[0].strip().split()[0]
        uniq_reads=parts[0].split('\n')[3].strip().split()[0]
        dup_reads=parts[0].split('\n')[4].strip().split()[0]
        result="{project},{total},{unique},{dup},{filter_unique}\n".format(project=p1,total=total_reads,unique=uniq_reads,dup=dup_reads,filter_unique=filtered_reads)
        f.write(result)

f.close()
print("alignment stats complete!")



# %%
