from os.path import split
import sys
import os

DEFAULT_CONFIG="DEFAULT"
class RawDataInfo:
    def __init__(self,project_name,seq1,seq2,control_project="",seq1c="",seq2c="",config_id=DEFAULT_CONFIG,):
        self.project=project_name
        self.seq1=seq1
        self.seq2=seq2
        
        if control_project=="":
            self.control_project=project_name
            self.seq1c=seq1
            self.seq2c=seq2
        else:
            self.control_project=control_project
            self.seq1c=seq1c
            self.seq2c=seq2c
        self.config_id=DEFAULT_CONFIG

    def __str__(self):
        return "{},{},{}".format(self.project,self.seq1,self.seq2)



def parse_inputfile(path):
    f=open(path)
    all_seqs=[]
    for line in f:
        lineSplit=line.strip().split(",")
        if len(lineSplit)==6:
            seqinfo=RawDataInfo(lineSplit[0],lineSplit[1],lineSplit[2],lineSplit[3],lineSplit[4],lineSplit[5])
        elif len(lineSplit)==3:
            seqinfo=RawDataInfo(lineSplit[0],lineSplit[1],lineSplit[2])
        elif len(lineSplit)==7:
            seqinfo=RawDataInfo(lineSplit[0],lineSplit[1],lineSplit[2],lineSplit[3],lineSplit[4],lineSplit[5],lineSplit[6])
        elif len(lineSplit)==4:
            seqinfo=RawDataInfo(lineSplit[0],lineSplit[1],lineSplit[2],config_id=lineSplit[3])



        all_seqs.append(seqinfo)

    f.close()
    return all_seqs


def parse_inputdir(path):
    file_names={}
    all_seqs=[]
    for root,dirs,name in os.walk(path):
        if  ".fq.gz" not in name:
            continue
        project_name=name.split("_")[0]
        if project_name not in file_names:
            file_names[project_name]=[os.path.join(root,name)]
        else:
            file_names[project_name].append(os.path.join(root,name))
    
    for key,value in file_names.items():
        if len(value)!=2:
            continue
        seqinfo=RawDataInfo(key,value[0],value[1])
        all_seqs.append(seqinfo)
    return all_seqs
