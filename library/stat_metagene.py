import os
import sys

#usage python thisfile.py outputname  refgene.txt datapoints TSS-5' TTS-3' <bw1 bw2 ...>

if len(sys.argv)<6:
    usage="usage python {} outputname  refgene.txt  datapoints TSS-5' TTS-3' <bw1 bw2 ...>".format(__file__)
    print(usage)

outputname=sys.argv[1]
refgene=sys.argv[2]
datapoints=sys.argv[3]
uper_region=sys.argv[4]
down_region=sys.argv[5]

if len(sys.argv)>=7:
    inputfiles=sys.argv[6:]
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
        start_site=lineSplit[4]
        end_site=lineSplit[5]
        gene_info[gene_id]=[chrom_name,start_site,end_site]
    f.close()
    print("refGene get!")
    return gene_info
    
def get_file_summary(file,gene_info,upper=uper_region,down=down_region,datapoints=datapoints,w=True,outname='meta_gene.stat'):
    cmd="bigWigSummary {file_name} {chr} {start} {end} {datapoints}"
    gene_result={}
    count=0

    f_r=open(outname,'a+')

    for gene_id,info in gene_info.items():
        count+=1
        chrom=info[0]
        tss=info[1]
        tts=info[2]

        tss_upper=max(0,int(tss)-int(upper))
        tts_down=tts+down

        cmd1=cmd.format(file_name=file,chr=chrom,datapoints=datapoints,start=tss_upper,end=tss)
        cmd2=cmd.format(file_name=file,chr=chrom,datapoints=datapoints,start=tss,end=tts)
        cmd3=cmd.format(file_name=file,chr=chrom,datapoints=datapoints,start=tts,end=tts_down)

        cmds=[cmd1,cmd2,cmd3]
        result=[]


        for cmd in cmds:
            f=os.popen(cmd)
            result.append(f.read().split())
        gene_result[gene_id]=result
        if count%1000==0:
            print("{} {:.2f}% got ".format(file,100*count/len(gene_info)))

            if w:
                for i in range(3):
                    for j in range(len(result[i])):
                        intensity=result[i][j]
                        if intensity=="n/a":
                            intensity="0"
                        line="{file},{geneid},{part},{site},{intensity}\n".format(file=file,geneid=gene_id,part=i,site=j,intensity=intensity)
                        f_r.write(line)
    f_r.close()



    return gene_result


def get_all_statis(inputfiles,gene_info,upper=uper_region,down=down_region,datapoints=datapoints,w=True,outname="metagene.stats"):
    result={}
    ##result={bwname:{geneid:[[region1],[region2],[region3]]}}
    for file in inputfiles:
        file_result=get_file_summary(file,gene_info,upper,down,datapoints,w,outname)
        result[file]=file_result
        print("{} summary get!".format(file))
    return result

def output(file_result,file_name=outputname):
    f=open(file_name,'a')
    info="{file},{geneid},{part},{site},{intensity}\n"
    for file, gene_result in file_result.items():
        for gene_id,sites_intensity in gene_result.items():
            for part_id in range(len(sites_intensity)):
                part=sites_intensity[part_id]
                for datasite in range(len(part)):
                    intensity=part[datasite]
                    if intensity=="n/a":
                        intensity=="0"
                    line=info.format(file=file,geneid=gene_id,part=part_id,site=datasite,intensity=intensity)
                    f.write(line)
    f.close()
    return True

if __name__=="__main__":
    gene_info=get_gene_info(refgene)
    result=get_all_statis(inputfiles=inputfiles,gene_info=gene_info,w=True,outname=outputname)
    #complete=output(result,file_name=outputname)
    #if complete:
        #print("success!")
    print("success!")



