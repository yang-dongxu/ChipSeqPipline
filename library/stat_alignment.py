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

f=open(outname,'a')

# %%
aligment_pattern="######Start mapping (\S+)######[\s\S]+?(\d+ reads[\s\S]+?alignment rate)\s######Stop mapping (\S+)######"
# %%
all_mapping_results=re.findall(aligment_pattern,text)
for p1,body,p2 in all_mapping_results:
    if p1.strip() !=p2.strip():
        continue
    parts=[i.strip() for i in body.split('----') ]
    if len(parts) != 3:
        continue
    else:
        total_reads=parts[0].split('\n')[0].strip().split()[0]
        uniq_reads=parts[0].split('\n')[3].strip().split()[0]
        result="{project},{total},{unique}\n".format(project=p1,total=total_reads,unique=uniq_reads)
        f.write(result)

f.close()
print("alignment stats complete!")



# %%
