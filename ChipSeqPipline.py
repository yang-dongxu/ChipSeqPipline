import os
import sys
import argparse
import json




VERSION="0.0.1"
LIBRARY='library'
SUB_TITLE='sub command'
script_name=os.path.abspath(__file__)
SCRIPT_PATH=os.path.join(os.path.split(script_name)[0])
DEFAULT_CONFIG=os.path.join(SCRIPT_PATH,LIBRARY,"default.json")


sys.path.append(os.path.join(SCRIPT_PATH,"library"))
import parse_input
from combine_module import combine_modules


def parse_argument(title=SUB_TITLE,):
    parser=argparse.ArgumentParser()
    sub_parser=parser.add_subparsers(title=title)
    add_generate_config(sub_parser=sub_parser)
    add_run(sub_parser=sub_parser)
    parser.set_defaults(func=parser.print_help)
    return parser


def add_generate_config(sub_parser:argparse.ArgumentParser):
    new_parser=sub_parser.add_parser("generate_config")
    new_parser.add_argument('-o','--outdir',dest="outdir",type=str,action="store",default=os.getcwd())
    new_parser.set_defaults(func=generate_config)
    return True


def add_run(sub_parser:argparse.ArgumentParser,default_config=DEFAULT_CONFIG):
    new_parser=sub_parser.add_parser("run")

    input_opt=new_parser.add_mutually_exclusive_group()
    input_opt.add_argument('-a','--auto',dest="auto",action="store_true",default=True,help="choose this to let this script get seg pair info with input dir auto. default choose\n")
    input_opt.add_argument('-b','--byhand',dest="byhand",action="store_true",default=False,help='choose this to input seg pair info with a file, which is determine by -f\n')

    new_parser.add_argument('-i','--input_dir',dest="input_dir",type=str,action='store',help="input a dir where fq exists, and the script wiil determine the pair\n")
    new_parser.add_argument('-f','--seqinfo',dest="seqinfo",type=str,action="store",help="input a file with paired seqs, it should be a csv with no head, and contain three columns:project_name,pair1,pair2\n")

    new_parser.add_argument('-o','--outdir',dest="outdir",type=str,action="store",default="CSPoutput",help="output dir")
    new_parser.add_argument('-c','--config',dest="config",type=str,action="store",default=DEFAULT_CONFIG)
    new_parser.set_defaults(func=run)
    return True



def generate_config(args,config_path=DEFAULT_CONFIG):
    out_name=os.path.join(os.getcwd(),args.outdir)
    cmd="cp {default} {target}".format(default=config_path,target=out_name)
    print(cmd)
    os.system(cmd)
    return True

def run(args):
    if args.byhand:
        seqs=parse_input.parse_inputfile(args.seqinfo)
        cmd=f"{args.seqinfo},{args.outdir},{args.config}"
    else:
        seqs=parse_input.parse_inputdir(args.input_dir)
        cmd=f"{args.input_dir},{args.outdir},{args.config}"

    f=open(args.config)
    all_configs=json.loads(f.read())
    f.close()
    for seq in seqs:
        config=all_configs[seq.config_id]
        config["generate_cmd"]["cmd_name"]=all_configs["cmd_name"]
        combine_modules(seq,config,args)
    cmd_name=os.path.join(args.outdir,all_configs["cmd_name"])
    log_name=os.path.join(args.outdir,all_configs["log_name"])

    cmd_1=cmd_name+".part1"
    cmd_2=cmd_name+".part2"
    
    with open(cmd_1) as f:
        f1=f.read()
    with open(cmd_2) as f:
        f2=f.read()

    ####aligment 分析的部分，放在命令行最后
    outname_dir=os.path.join(os.getcwd(),args.outdir,all_configs[parse_input.DEFAULT_CONFIG]["stats"]["outdir"])
    outname=os.path.join(outname_dir,"alignments.stats")
    script_name=os.path.join(os.path.split(DEFAULT_CONFIG)[0],'stat_alignment.py')
    cmd1=f"\n####aligment stats start####\npython {script_name} {log_name} {outname}\n####alignment stats stop####\n"
    cmd=cmd1

    ###用来统计metagene相关的部分，放在最后
    if all_configs[parse_input.DEFAULT_CONFIG]["stats"]["stat_metagene"]:
        script=os.path.join(os.path.split(os.path.abspath(__file__))[0],LIBRARY,"stat_metagene.py")
        outname=os.path.join(outname_dir,"metagene.stats")
        config=all_configs[parse_input.DEFAULT_CONFIG]["stats"]
        refgene=config["refgene"]
        datapoints=config["datapoints"]
        tss5=config["TSS-upstream-region"]
        tts3=config["TTS-downstream-region"]
        threads=config["stat_metagene_threads"]
        bw_path=os.path.join(os.getcwd(),args.outdir,all_configs[parse_input.DEFAULT_CONFIG]["toBw"]["outdir"])
        inputfile="du -a {} | grep bw | cut -f 2 |" .format(bw_path)
        cmd2=f"\n####metagene stats start####\n {inputfile} python {script} {outname} {refgene} {datapoints} {tss5} {tts3} {threads}\n####metagene stats stop####\n"
        cmd=cmd+cmd2

    
    with open(cmd_name,'w') as f:
        sep_bar="\n"+"#"*20+"\n"
        f.write(f1+sep_bar+f2+cmd)
    
    if all_configs["bash_run"]:
        f=open(cmd_name)
        for cmd in f:
            if '>' in cmd and '#' not in cmd:
                cmd_to_log="{cmd}".format(cmd=cmd.strip())
            else:
                cmd_to_log="{cmd} >> {log} 2>&1".format(cmd=cmd.strip(),log=log_name)
            status=os.system(cmd_to_log) >>8
            if status!=0:
                #the cmd exit with errors
                print("{} for {}".format(status,cmd))
                with open(cmd_name+".broken",'a') as p:
                    p.write(cmd)
        #cmd="bash {cmd_name} 2>&1 | tee {log}  ".format(cmd_name=cmd_name,log=log_name)
        #os.system(cmd)
    
    print("Complete!")



if __name__=="__main__":
    parser=parse_argument()
    args=parser.parse_args()
    args.func(args)



