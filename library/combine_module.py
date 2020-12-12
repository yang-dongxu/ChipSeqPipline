import sys
import os


from parse_input import RawDataInfo
from process_funcs import *

METHOD={
    "fastqc":fastqc,
    "trim_galore":trim_galore,
    "mapping":mapping,
    "to_bam":to_bam,
    "sort_and_clean":sort_and_clean,
    "peakcalling":peakcalling,
    "toBw":toBw,
    "generate_cmd":generate_cmd,
    "stats":stats

}





class Path_info:
    def __init__(self,outpath=""):
        self.project=""
        self.control_project=""
        self.inputpaths=[]
        self.control_paths=[]
        self.results=""
        self.results_latter=""
        self.outpath_root=os.path.abspath(outpath)

        #{process:[name1,name2]}
        self.paths={}
    
    def get_from_rawinfo(self,rawinfo:RawDataInfo):
        self.project=rawinfo.project
        if len(rawinfo.seq2):
            self.inputpaths=[rawinfo.seq1,rawinfo.seq2]
        else:
            self.inputpaths[rawinfo.seq1]
        self.control_project=rawinfo.control_project
        if len(rawinfo.seq2c):
            self.control_paths=[rawinfo.seq1c,rawinfo.seq2c]
        else:
            self.control_paths=[rawinfo.seq1c]

    def set_input_path(self,*args):
        self.inputpaths=args
    
    def set_control_path(self,*args):
        self.control_paths=args
    
    def append_result(self,new_result):
        self.results+="\n"+new_result
    
    def append_result_latter(self,new_results):
        self.results_latter+="\n"+new_results


def combine_modules(seqinfo:RawDataInfo,config_dict:dict,args):
    need_modules=[i for i in config_dict["order"] if config_dict[i]["need"] ]
    inputpaths=Path_info(outpath=args.outdir)
    inputpaths.get_from_rawinfo(rawinfo=seqinfo)
    for func in need_modules:
        callable_func=METHOD[func]
        callable_func(inputpaths,config_dict[func])
    
