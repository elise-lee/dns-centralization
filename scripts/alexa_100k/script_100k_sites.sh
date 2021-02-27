start=1
count=100
for value in {1..1000}
do
	python3 topsites.py --key=8zAVhuUZP07eCZ5DWDrmraj0gqBUK6B452rMGdVs --action=TopSites --country='' --options="&Count=${count}&Output=json&Start=${start}" >> websites.json
	start=`expr $start + $count` 
done
