import os
import sys
from multiprocessing import Pool, Value, process
from functools import partial

#usage python thisfile.py outputname  refgene.txt datapoints TSS-5' TTS-3' <bw1 bw2 ...>

if len(sys.argv)<6:
    usage="usage python {}  outputname  refgene.txt  datapoints TSS-5' TTS-3' threads <bw1 bw2 ...>".format(__file__)
    print(usage)

outputname=sys.argv[1]
refgene=sys.argv[2]
datapoints=int(sys.argv[3])
uper_region=int(sys.argv[4])
down_region=int(sys.argv[5])
processors=int(sys.argv[6])

if len(sys.argv)>=8:
    inputfiles=sys.argv[7:]
else:
    names=sys.stdin.read().split()
    inputfiles=[i.strip() for i in names ]

print("input files: {}".format(inputfiles))



def get_gene_info(refgene):
    f=open(refgene)
    gene_info={}
    for line in f:
        lineSplit=line.split()
        gene_id=lineSplit[1]
        chrom_name=lineSplit[2]
        if lineSplit[3]=="+":
            start_site=int(lineSplit[4])
            end_site=int(lineSplit[5])
        else:
            start_site=int(lineSplit[5])
            end_site=int(lineSplit[4])
        if start_site==end_site:
            continue
        gene_info[gene_id]=[chrom_name,start_site,end_site]
    f.close()
    print("refGene get!")
    return gene_info

def process_bigwigsummary(geneid,file_name,region:tuple,datapoints):
    chrom=region[0]
    start=region[1]
    end=region[2]
    label=region[3]
    cmd=f"bigWigSummary {file_name} {chrom} {start} {end} {datapoints}"
    f=os.popen(cmd)
    datas=f.read().split()
    if len(datas)==datapoints:
        datas=['0' if value =="n/a" else value.strip() for value in datas]
    else:
        datas=['0']*datapoints
    results=[f"{file_name},{geneid},{label},{i},{datas[i].strip()}" for i in range(len(datas))]
    return "\n".join(results)


def merge_files(inputfiles,outname):
    cmd="cat {} > {} ".format("  ".join(inputfiles),outname)
    os.system(cmd)
    rm_tmps=[f"rm -f {i}" for i in inputfiles]
    for i in rm_tmps:
        os.system(i)
    return True


def process_bigwigsummary(region:tuple,geneid,file_name,datapoints):
    chrom=region[0]
    start=region[1]
    end=region[2]
    label=region[3]
    cmd=f"bigWigSummary {file_name} {chrom} {start} {end} {datapoints}"
    f=os.popen(cmd)
    datas=f.read().split()
    if len(datas) == datapoints:
        datas=['0' if value =='n/a' else value for value in datas]
    else:
        datas=['0']*datapoints
    results=[f"{file_name},{geneid},{label},{i},{datas[i].strip()}" for i in range(len(datas))]
    return "\n".join(results)

def get_summary_for_file(names:tuple,gene_info,upper=uper_region,down=down_region,datapoints=datapoints):
    assert len(names)==2
    file=names[0]
    outname=names[1]
    f=open(outname,'w')
    all_results=[]
    for geneid,info in gene_info.items():
        bigwig_for_geneid=partial(process_bigwigsummary,geneid=geneid,file_name=file,datapoints=datapoints)
        chrom=info[0]
        if info[1] < info[2]:
            tss=info[1]
            tts=info[2]

            tss_upper=max(0,int(tss)-int(upper))
            tts_down=tts+down
        else:
            tss=info[2]
            tts=info[1]

            tss_upper,tss=tss,tss+upper
            tts,tts_down=max(0,tts-down),tts

            tss,tts=tts,tss

        regions=[(chrom,tss_upper,tss,"promoter"),(chrom,tss,tts,"gene"),(chrom,tts,tts_down,"downstream")]

        results=[bigwig_for_geneid(i) for i in regions]
        all_results.append('\n'.join(results))
    f.write('\n'.join(all_results)+'\n')
    return outname


if __name__=="__main__":
    POOL=Pool(processors)
    gene_info=get_gene_info(refgene)
    upper=uper_region
    down=down_region
    w=True
    outname=outputname

    tmp_lens=len(inputfiles)

    get_summ_partial=partial(get_summary_for_file,gene_info=gene_info,upper=uper_region,down=down_region,datapoints=datapoints)
    outnames=[outname+"."+str(i)+'.tmp' for i in range(tmp_lens)]
    names=[(inputfiles[i],outnames[i]) for i in range(tmp_lens)]
    POOL.map(get_summ_partial,names)
    POOL.close()
    POOL.join()
    #[get_summ_partial(i) for i in names]
    merge_files(outnames,outname)


    print("success!")




