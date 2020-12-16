## uasge
* python ChipSeqPiplie.py generate_config -o outdir  

this command will generate a config file in your outdir, and some options should be edit to make it compatible with your environment

* python ChipSeqPipline.py run -bf seq_info.txt -c config_file -o outdir  
this is the really working command. -b means input your seq pairs info by hand ,which actually is provided with -f and seq_info
the seq_info file is a csv with the format below（*there should no header!*),and the config_file is generate by the step above



| project | fq.gz.1 | fq.gz.2 |
| ---- | ----| ---- | 
|1|1.1|1.2|
|2|2.1|2.2|

or table like this below:  

| project | fq.gz.1 | fq.gz.2 |control_project|control_fq.1|control_fq.2|
| ---- | ----| ---- | ---- | ----| ---- 
|1|1.1|1.2|3|3.1|3.2|
|2|2.1|2.2|3|3.1|3.2|
|3|3.1|3.2|3|3.1|3.2|

*ATTENTION*: the option of bash is to determin whether actually run or just generate a cmd file. It's suggested to generate a cmd file for the first to check, and then turn it to true and run

You can't skip the mapping step by now, but if you just don't need mapping, it's recommend to generate cmds by this pipline sort the steps you want.
