#!/bin/bash

ml load python/2.7

# Path
dpath='/DATA/OWGIS_I_GOES/jevz/'

# Remove previous auxiliar files
flist=$dpath'List'
dlist=$dpath'Downloaded'

[[ -f $flist ]] && rm $flist
[[ -f $dlist ]] && rm $dlist

# Mode
# 0 get files form the current hour
# 1 get files from the current day
# 2 get files from the previous day
# 3 get files from specific day and year
mode=1

# Desired data bands [available from C01 to C16]
# C01 Blue [Visible]
# C02 Red [Visible]
# C04 Veggie [NIR]
# C05 Cirrus [NIR]
# C06 Snow/Ice [NIR]
# C07 Cloud Ice [NIR]
# C07 SWIR [IR]
# C08 Upper-Level Water Vapor [IR]
# C09 Mid-Level Water Vapor [IR]
# C10 Lower-Level Water Vapor [IR]
# C11 Cloud Top Phase [IR]
# C12 Ozone [IR]
# C13 Clean [IR]
# C14 Standard [IR]
# C15 Dirty [IR]
# C16 C02 [IR]

#bands="C01 C02 C03 C04 C05 C06 C07 C08 C09 C10 C11 C12 C13 C14 C15 C16"
#bands="C01 C02 C03 C13"
bands="C13"

# Available processing levels and extends

# L1b-RadM Radiances Mesoescale
# L1b-RadC Radiances CONUS
# L1b-RadF Radiances Full Disk
# L2-CMIPM Reflectance Mesoescale
# L2-CMIPC Reflectance CONUS
# L2-CMIPF Reflectance Full Disk

NCs='L2-CMIPF'

if [[ $mode == 0 ]]; then
 # Get the  specific year, day of the year and hour of the desired files
 yy=$(date -u +'%Y')
 dy=$(date -u +'%j')
 hh=$(date -u +'%H')
 # Connect to aws bucket (Get the file list)
 aws s3 --no-sign-request ls --recursive noaa-goes16/ABI-$NCs/$yy/$dy/$hh | awk '{print $4}' >> $flist

else
 if [[ $mode == 1 ]]; then
  # Get the  specific year, day of the year of the desired files
  yy=$(date -u +'%Y')
  dy=$(date -u +'%j')
  # Connect to aws bucket (Get the file list)
  aws s3 --no-sign-request ls --recursive noaa-goes16/ABI-$NCs/$yy/$dy/ | awk '{print $4}' >> $flist

 else
  if [[ $mode == 2 ]]; then
   # Get the  specific year, day of the year of the desired files
   yy=$(date -u +'%Y')
   dsy=$(date -u +'%j')
   dy=$(($dsy - 1))
   # Connect to aws bucket (Get the file list)
   aws s3 --no-sign-request ls --recursive noaa-goes16/ABI-$NCs/$yy/$dy/ | awk '{print $4}' >> $flist

  else
   if [[ $mode == 3 ]]; then
    yy="2019"
    dy="222"
    # Connect to aws bucket (Get the file list)
    aws s3 --no-sign-request ls --recursive noaa-goes16/ABI-$NCs/$yy/$dy/ | awk '{print $4}' >> $flist

   else
    echo "Mode not recognized"
    exit
   fi
  fi
 fi
fi

# Creates a folder for the specific day of the year
[[ -d $dpath$dy ]] || mkdir $dpath$dy

# Filter Bands
for band in $bands; do
# echo $band
grep $band $flist >> $dlist
done

for nc in $(cat $dlist); do
 name=$(echo $nc | cut -d"/" -f5)
 #echo $name
 if  [ -f $dpath$dy/$name ]; then
  continue
 else
  aws s3 --no-sign-request cp s3://noaa-goes16/$nc $dpath$dy/
 fi
done
