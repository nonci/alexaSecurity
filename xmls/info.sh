#! /bin/bash

# Script che visualizza informazioni a partire dai file XML nella cartella shared_prefs

FILE1=shared_prefs/service.identity.xml

show () {
  printf "%25s | " $(echo $1|rev|sed "s/^\([^\.]*\)\..*/\1/1"|rev)
  grep "$1" "$2" | sed -n "s/^.*>\(.*\)<.*$/\1/p"
  grep "$1" "$2" | sed -n "s/^.*value=\"\(.*\)\".*$/\1/p";
}

show "user.name" $FILE1
show "user.profile.lastName" $FILE1
show "user.id" $FILE1
show "user.countryOfResidence" $FILE1
show "user.email" $FILE1
show "user.profile.comms.phoneNumber" $FILE1
show "user.directedId" $FILE1
show "user.marketplace" $FILE1
#show "user.accessToken" $FILE1
