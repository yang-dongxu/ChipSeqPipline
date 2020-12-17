
import os
import sys

def format_command_params(config)->str:
    cmd=""
    for key,value in config.items():
        if not isinstance(value,list):
            continue
        if value[0]:
            if len(key)==1:
                tmp="-{opt} {param}  ".format(opt=key,param=value[1])
            else:
                tmp="--{opt} {param}  ".format(opt=key,param=value[1])
            cmd+=tmp
    return cmd

def mkdirs(path):
    if not os.path.exists(path):
        os.makedirs(path)
    return True


def fastqc(inputpath,config):
    print("fastqc processed")

def trim_galore(inputpath,config):

    outdir=config["outdir"]
    output_dir_name=os.path.join(inputpath.outpath_root,outdir)
    mkdirs(output_dir_name)

    file_names=[os.path.split(i)[1] for i in inputpath.inputpaths]
    if file_names[0][:-6][-1]=="1":
        result_name1=file_names[0][:-6]+"_val_1.fq.gz"
        result_name2=file_names[1][:-6]+"_val_2.fq.gz"
    else:
        result_name1=file_names[1][:-6]+"_val_1.fq.gz"
        result_name2=file_names[0][:-6]+"_val_2.fq.gz"
 
    result_name=[result_name1,result_name2]
    result_name=[os.path.join(output_dir_name,i) for i in result_name]
    
    #if config["fastqc_outdir"]:
        #config["fastqc_args"][1]+="  --outdir {}".format(config["fastqc_outdir"])

    software=config["path"]
    cmd_1=format_command_params(config)
    cmd_2="{}  {}  --output_dir {}".format(inputpath.inputpaths[0],inputpath.inputpaths[1],output_dir_name)
    cmd="\t".join([software,cmd_1,cmd_2])

    log_cmd="echo \"####\t{}\t####\\n\"".format(cmd)
    log_header="echo \"######Start toBam {}######\\n\"".format(inputpath.project)
    log_footer="echo \"######Stop toBam {}######\\n\"".format(inputpath.project)
    result="\n".join([log_header,log_cmd,cmd,log_footer])

    inputpath.append_result(result)
    inputpath.set_input_path(result_name[0],result_name[1])
    inputpath.paths["trimmed"]=[result_name[0],result_name[1]]
    return inputpath


def mapping(inputpath,config):
    method=config["method"]
    outdir=config["outdir"]
    config=config[method]
    assert len(inputpath.inputpaths)==2
    if method=="bowtie2":
        assert os.path.exists(config["x"][1]+".1.bt2")
        assert config["x"][0]
        param_part1=format_command_params(config)
        output_dir_name=os.path.join(inputpath.outpath_root,outdir)
        mkdirs(output_dir_name)
        result_name=os.path.join(output_dir_name,inputpath.project+'.sam')
        result_name_control=os.path.join(output_dir_name,inputpath.control_project+'.sam')
        param_part2="-1 {seq1} -2 {seq2} -S {name}".format(seq1=inputpath.inputpaths[0],seq2=inputpath.inputpaths[1],name=result_name)
        cmd=" ".join([config["path"],param_part1,param_part2])
        log_cmd="echo \"####\t{}\t####\\n\"".format(cmd)
        log_header="echo \"######Start mapping {}######\\n\"".format(inputpath.project)
        log_footer="echo \"######Stop mapping {}######\\n\"".format(inputpath.project)
        result="\n".join([log_header,log_cmd,cmd,log_footer])

        inputpath.append_result(result)
        inputpath.set_input_path(result_name)
        inputpath.set_control_path(result_name_control)
        inputpath.paths["sam"]=[result_name]
    return inputpath

def to_bam(inputpath,config):
    sortware_name=config["path"]+"  view"
    outdir=config["outdir"]

    param_part1=format_command_params(config)
    param_part2=inputpath.inputpaths[0]
    #print(param_part2)
    assert isinstance(param_part2,str)

    out_dir_name=os.path.join(inputpath.outpath_root,outdir)
    mkdirs(out_dir_name)
    result_name=os.path.join(out_dir_name,inputpath.project+'.bam')
    param_part3="-o {name}".format(name=result_name)

    cmd="\t".join([sortware_name,param_part1,param_part2,param_part3])
    if config["rmSam"]:
        #删除sam文件
        cmd_rm="rm -f {sam}".format(sam=inputpath.paths["sam"][0])
        cmd=cmd+'\n'+cmd_rm
    log_cmd="echo \"####\t{}\t####\\n\"".format(cmd).replace('\n',' && ')
    log_header="echo \"######Start toBam {}######\\n\"".format(inputpath.project)
    log_footer="echo \"######Stop toBam {}######\\n\"".format(inputpath.project)
    result="\n".join([log_header,log_cmd,cmd,log_footer])

    inputpath.append_result(result)
    inputpath.set_input_path(result_name)

    result_name_control=os.path.join(out_dir_name,inputpath.control_project+'.bam')
    inputpath.set_control_path(result_name_control)

    inputpath.paths["bams"]=[result_name]


    return inputpath

def sort_and_clean(inputpath,config):
    outdir=config["outdir"]
    software=config["path"]
    threads=config["threads"]
    final_suffix=config["suffix"]

    out_full_dir=os.path.join(inputpath.outpath_root,outdir)
    mkdirs(out_full_dir)
    out_name=os.path.join(out_full_dir,inputpath.project)


    ##part1 sort
    i1=inputpath.inputpaths[0]
    o1=out_name+".sort"
    cmd1_part1="{software} sort".format(software=software)
    cmd1_part2="-n -@ {threads} {i1} -o {o1}\n".format(threads=threads[1],i1=i1,o1=o1)
    cmd1="\t".join([cmd1_part1,cmd1_part2])

    ##part2 fixmate
    i2=o1
    o2=out_name+'.fix'
    cmd2_1="{software} fixmate".format(software=software)
    cmd2_2="-m -r -@ {threads} {i2} {o2}\n".format(threads=threads[1],i2=i2,o2=o2)
    cmd2="\t".join([cmd2_1,cmd2_2])

    ##part3 sort again for markdup
    i3=o2
    o3=o2+".sort"
    cmd3_1="{software} sort".format(software=software)
    cmd3_2="-@ {threads} {i3} -o {o3}\n".format(threads=threads[1],i3=i3,o3=o3)
    cmd3="\t".join([cmd3_1,cmd3_2])

    ##part4 markdup
    i4=o3
    o4=out_name+"_"+final_suffix
    cmd4_1="{software} markdup".format(software=software)
    cmd4_2="-r -@ {threads} {i4} {o4}\n".format(threads=threads[1],i4=i4,o4=o4)
    cmd4="\t".join([cmd4_1,cmd4_2])

    ##part5 rm tmps
    cmd5="rm -f {} {} {}".format(o1,o2,o3)

    cmd="".join([cmd1,cmd2,cmd3,cmd4,cmd5])

    log_cmd="echo \"####\t{}\t####\\n\"".format(cmd.replace("\n","  &&  "))
    log_header="echo \"######Start cleanBam {} ######\\n\"".format(inputpath.project)
    log_footer="echo \"######Stop cleanBam {} ######\\n\"".format(inputpath.project)
    result="\n".join([log_header,log_cmd,cmd,log_footer])

    inputpath.append_result(result)
    inputpath.set_input_path(o4)

    o4_control=os.path.join(out_full_dir,inputpath.control_project)+"_"+final_suffix
    inputpath.set_control_path(o4_control)

    inputpath.paths["cleanBam"]=[o4]

    return inputpath



def peakcalling(inputpath,config):
    method=config["method"]
    outdir=config["outdir"]
    config=config[method]

    out_full_dir=os.path.join(inputpath.outpath_root,outdir,inputpath.project)
    mkdirs(out_full_dir)
    i1=inputpath.inputpaths[0]
    i2=inputpath.control_paths[0]

    if method=="macs2":
        software="{} callpeak".format(config["path"])
        cmd_1=format_command_params(config)
        if i1==i2:
            cmd_2="-t {}".format(i1)
        else:
            cmd_2="-t {} -c {}".format(i1,i2)
        cmd_3="--outdir {} -n {}".format(out_full_dir,inputpath.project)
        cmd="\t".join([software,cmd_1,cmd_2,cmd_3])
    else:
        cmd="ERROR! choose a peakcalling software!"

    log_cmd="echo \"####\t{}\t####\\n\"".format(cmd.replace("\n","  &&  "))
    log_header="echo \"######Start peakcalling {}######\\n\"".format(inputpath.project)
    log_footer="echo \"######Stop peakcalling {}######\\n\"".format(inputpath.project)
    result="\n".join([log_header,log_cmd,cmd,log_footer])

    inputpath.append_result_latter(result)
    bdg_path=os.path.join(out_full_dir,inputpath.project+"_treat_pileup.bdg")
    inputpath.set_input_path(bdg_path)

    inputpath.paths["bdg"]=[bdg_path]
    inputpath.paths["narrowPeak"]=os.path.join(out_full_dir,inputpath.project+"_peaks.narrowPeak")
    return inputpath




def toBw(inputpath,config):

    assert os.path.exists(config["chromsize"])

    outdir=config["outdir"]
    out_full_dir=os.path.join(inputpath.outpath_root,outdir)
    mkdirs(out_full_dir)
    result_name=os.path.join(out_full_dir,inputpath.project+'.bw')
    
    i1=inputpath.inputpaths[0]
    tmp_name=i1+".tmp"
    cmd1="sort -k1,1 -k2,2n {} > {}".format(i1,tmp_name)
    cmd2="bedGraphToBigWig {i} {chromsize}  {o}".format(i=tmp_name,chromsize=config["chromsize"],o=result_name)
    
    cmd3="rm -f {}".format(tmp_name)
    cmd="\n".join([cmd1,cmd2,cmd3])

    log_cmd="echo \"####\t{}\t####\\n\"".format(cmd.replace("\n","  &&  "))
    log_header="echo \"######Start bdg2bw {}######\\n\"".format(inputpath.project)
    log_footer="echo \"######Stop bdg2bw {}######\\n\"".format(inputpath.project)
    result="\n".join([log_header,log_cmd,cmd,log_footer])

    inputpath.append_result_latter(result)
    inputpath.set_input_path(result_name)
    inputpath.paths["bw"]=[result_name]




def generate_cmd(inputpath,config):
    cmd_name=os.path.join(inputpath.outpath_root,config["cmd_name"])

    ##tmp1 用来存储先行命令，tmp2用来存储在先行命令运行完之后的命令，如peakcalling相关
    tmp1=cmd_name+'.part1'
    tmp2=cmd_name+'.part2'

    cmd="\necho \" ######## {} processing {} ######## \\n\"\n"
    cmd_header=cmd.format("Start ",inputpath.project)
    cmd_footer=cmd.format("End",inputpath.project)

    f=open(tmp1,'a+')
    f.write(cmd_header)
    f.write(inputpath.results)
    f.write(cmd_footer)
    f.close()

    f=open(tmp2,'a+')
    f.write(cmd_header)
    f.write(inputpath.results_latter+'\n')
    f.write(cmd_footer)
    f.close()


def stats(inputpath,config):

    assert os.path.exists(config["chromsize"])
    assert os.path.exists(config["refgene"])

    outname_dir=os.path.join(inputpath.outpath_root,config["outdir"])
    mkdirs(outname_dir)

    #用来统计peaks数的部分
    script=os.path.join(os.path.split(os.path.abspath(__file__))[0],"stat_peaks.py")
    outname=os.path.join(outname_dir,"peaks.stats")
    if "narrowPeak" in inputpath.paths:
        inputfile=inputpath.paths["narrowPeak"]
        cmd1=f"python {script} {outname} {inputfile}"
    else:
        cmd1="##ERROR! no information about peaks!"
    cmd=cmd1
    

    log_cmd="echo \"####\t{}\t####\\n\"".format(cmd.replace("\n","  &&  "))
    log_header="echo \"######Start generate stats {}######\\n\"".format(inputpath.project)
    log_footer="echo \"######Stop generate stats {}######\\n\"".format(inputpath.project)
    result="\n".join([log_header,log_cmd,cmd,log_footer])



    inputpath.append_result_latter(result)
    return inputpath

