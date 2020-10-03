
popSize=10
defaultConf=dspotAllamps
INPUT=data.csv
OLDIFS=$IFS
IFS=','
[ ! -f $INPUT ] && { echo "$INPUT file not found"; exit 99; }
while read pname tname
do
   echo "$pname $tname $popSize"
   cd ~/pharo-projects/$pname
   ~/Pharo/pharo Pharo.image eval "(SmallAmp initializeWith: (SAConfig $defaultConf maxPop: $popSize; yourself)) testCase: $tname; amplifyEval"
done < $INPUT
IFS=$OLDIFS
