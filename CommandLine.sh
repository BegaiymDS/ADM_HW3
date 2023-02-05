#!/bin/bash
IFS="§"
let IT=SP=FR=EN=US=ITv=SPv=FRv=ENv=USv=ITw=SPw=FRw=ENw=USw=0
for file in TSV_Files/*.tsv
do read country country2 v w <<< $( awk -F "\t" 'NR==1 { n=split($8, a, " - "); print a[n], "§", a[n-1], "§", $3, "§", $4 }' $file );
if [[ "$country" == *Italy* ]]; then (( IT++ )); (( ITv+=$v )); (( ITw+=$w ));
elif [[ "$country" == *Spain* ]]; then (( SP++ )); (( SPv+=$v )); (( SPw+=$w ));
elif [[ "$country" == *France* ]]; then (( FR++ )); (( FRv+=$v )); (( FRw+=$w ));
elif [[ "$country2" == *England* ]]; then (( EN++ )); (( ENv+=$v )); (( ENw+=$w ));
elif [[ "$country" == *United\ States* ]]; then (( US++ )); (( USv+=$v )); (( USw+=$w ))
fi done;
echo -n "Italy:   Places:" $IT, "Avg visitors per place: "; awk "BEGIN { printf ($ITv)/$IT }"; echo ", Want to visit:" $ITw;
echo -n "Spain:   Places:" $SP, "Avg visitors per place: "; awk "BEGIN { printf ($SPv)/$SP }"; echo ", Want to visit:" $SPw;
echo -n "France:   Places:" $FR, "Avg visitors per place: "; awk "BEGIN { printf ($FRv)/$FR }"; echo ", Want to visit:" $FRw;
echo -n "England:   Places:" $EN, "Avg visitors per place: "; awk "BEGIN { printf ($ENv)/$EN }"; echo ", Want to visit:" $ENw;
echo -n "United States:   Places:" $US, "Avg visitors per place: "; awk "BEGIN { printf ($USv)/$US }"; echo ", Want to visit:" $USw
