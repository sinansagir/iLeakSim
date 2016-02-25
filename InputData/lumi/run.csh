#!/bin/csh

set datestart_=`date -d 2010-03-30 +%s`
#set todayinday_=`date +%Y%m%d`
#set today_=`date -d ${todayinday_} +%s`
set datefinish_=`date -d 2013-01-01 +%s`
set step_=86400
set period_=`echo ${datestart_} ${datefinish_} ${step_} | awk '{printf "%.0f",($2-$1)/$3}'`
set counter_=0
#'{printf "%.0f",$1}'
if (-e list.log )then
mv list.log .list.log
endif
touch list.log
set endWhile_ = `echo $period_ + 1 | bc`
echo $counter_
echo $endWhile_
while ($counter_ < $endWhile_)
	echo $counter_
    @ time_ = ${datestart_} + ${step_} * (${counter_} + 1)
    set thisrun_=`date -u --date "1970-01-01 ${time_} sec GMT" +%Y-%m-%d`
    echo "${thisrun_}_lumi.txt" >> list.log
    @ counter_++
end

set dates_=`cat list.log | awk -F"_lumi" '{print $1}' | sed 's/201/1/g'`

foreach d_(${dates_})

set checkExistingFile_=`echo "lumi/20"${d_}"_lumi.txt"`    
if ( -e ${checkExistingFile_} ) then
echo $checkExistingFile_
continue
endif

set y_=`echo ${d_} | awk -F"-" '{print $1}'`
set m_=`echo ${d_} | awk -F"-" '{print $2}'`
set d_=`echo ${d_} | awk -F"-" '{print $3}'`

#if ( ${y_} < 11 ) then
#continue
#endif

#if ( ${m_} < 5 ) then
#continue
#endif

if ( -e lumi/20${y_}-${m_}-${d_}_lumi.txt ) then
rm lumi/20${y_}-${m_}-${d_}_lumi.txt
endif

echo "CUMULATIVE_LUMI_INVNB" >& lumi/20${y_}-${m_}-${d_}_lumi.txt

echo lumiCalc2.py --begin "${m_}/${d_}/${y_} 00:00:00" --end "${m_}/${d_}/${y_} 23:59:59" overview

#lcr2.py --begin "03/13/11 00:00:00" --end "10/30/11 23:59:59" --amodetag PROTPHYS --beamenergy 3500 --beamfluctuation 0.2 -b stable overview
#set status_=`python lcr2.py --begin "${m_}/${d_}/${y_} 00:00:00" --end "${m_}/${d_}/${y_} 23:59:59" `

#set unit_=`lcr2.py --begin "${m_}/${d_}/${y_} 00:00:00" --end "${m_}/${d_}/${y_} 23:59:59" `
#echo hello
lumiCalc2.py --begin "${m_}/${d_}/${y_} 00:00:00" --end "${m_}/${d_}/${y_} 23:59:59" overview >> lumi/20${y_}-${m_}-${d_}_lumi.txt

end
