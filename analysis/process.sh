#!/bin/bash

RESULTDIR=../data/output/sioux
BASELINE_RESULTDIR=../data/output/sioux_baseline
ITER=150

OUTPUTDIR=temp
mkdir -p $OUTPUTDIR

REPORT=$OUTPUTDIR/report.md

# Read data

python3 readers/read_events.py $RESULTDIR/output_events.xml.gz $OUTPUTDIR/data.db final
python3 readers/read_events.py $BASELINE_RESULTDIR/output_events.xml.gz $OUTPUTDIR/data.db initial
python3 readers/read_services.py $RESULTDIR/ITERS/it.$ITER/$ITER.av_services.xml.gz $OUTPUTDIR/data.db final
python3 readers/read_population.py $RESULTDIR/output_plans.xml.gz $OUTPUTDIR/data.db final
python3 readers/read_population.py $BASELINE_RESULTDIR/output_plans.xml.gz $OUTPUTDIR/data.db initial
python3 readers/read_relaxation.py $RESULTDIR $OUTPUTDIR/relaxation.dat
python3 readers/read_distances.py $BASELINE_RESULTDIR/ITERS/it.$ITER/$ITER.experienced_plans.xml.gz $OUTPUTDIR/data.db initial
python3 readers/read_distances.py $RESULTDIR/ITERS/it.$ITER/$ITER.experienced_plans.xml.gz $OUTPUTDIR/data.db final
python3 readers/read_network.py $RESULTDIR/output_network.xml.gz $OUTPUTDIR/data.db
python3 readers/read_link_times.py $RESULTDIR/output_events.xml.gz $OUTPUTDIR/data.db final

# Process data

python3 processors/plot_relaxation.py $OUTPUTDIR/relaxation.dat $OUTPUTDIR/relaxation.png
python3 processors/create_mode_matrices.py $OUTPUTDIR/data.db $OUTPUTDIR/matrices.dat initial final

python3 processors/plot_legs.py $OUTPUTDIR/data.db initial 600 $OUTPUTDIR/initial_share.png
python3 processors/plot_legs.py $OUTPUTDIR/data.db final 600 $OUTPUTDIR/final_share.png
python3 processors/plot_services.py $OUTPUTDIR/data.db final 600 $OUTPUTDIR/services.png

python3 processors/plot_travel_time.py $OUTPUTDIR/data.db initial final 600 average $OUTPUTDIR/traveltime.png
python3 processors/plot_waiting_times.py $OUTPUTDIR/data.db final 600 $OUTPUTDIR/waitingtimes.png
python3 processors/plot_distances.py $OUTPUTDIR/data.db initial final 600 $OUTPUTDIR/distances.png

python3 processors/plot_legdist.py $OUTPUTDIR/data.db final av departure $OUTPUTDIR/avdepartures.png
python3 processors/plot_legdist.py $OUTPUTDIR/data.db final car departure $OUTPUTDIR/cardepartures.png

python3 processors/plot_changedist.py $OUTPUTDIR/data.db initial final transit_walk av $OUTPUTDIR/avtransitchange.png
python3 processors/plot_link_times_day.py temp/data.db final $OUTPUTDIR/congestion.gif

python3 processors/plot_totaldist.py $OUTPUTDIR/data.db initial final 600 $OUTPUTDIR/totaldist.png

# Build the report

echo $BASELINE_RESULTDIR > $OUTPUTDIR/initial_path.md
echo $RESULTDIR > $OUTPUTDIR/final_path.md

cp template/report.md $OUTPUTDIR/report.md
cp template/markdown.css $OUTPUTDIR/markdown.css

CURRENTDIR=`pwd`

cd $OUTPUTDIR
python3 $CURRENTDIR/processors/include_md.py report.md
pandoc report.md -s -c markdown.css --self-contained -o report.html
