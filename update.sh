#!/bin/bash
path=`pwd`
python3=`which python3`
autoFile="$path/process.py"
#echo $autoFile
crontab_str="*/20 * * * * $python3 $autoFile >/dev/null &"
#echo "$crontab_str"
crontab_file_name="crontab.new"
crontab -l > $crontab_file_name
cp -f "$crontab_file_name" "$crontab_file_name.back.`date +'%s'`"
echo "$crontab_str" >> $crontab_file_name
crontab $crontab_file_name
