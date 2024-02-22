# Pipeline to transform a RGB video (originally in MP4 / AVI / FLV) into events (saved as NPY)
# Takes as input argument:
#   1) dataset (mandatory): directory where the RGB video(s) are stored
#   2) fps (optionnal, default=24): number of frames per second in the input RGB video
# Example of use: ./run_RGB2ev.sh /home/agruel/Data/oilspill/SouthernCaliforniaOilSpill/ -f 30
# 22/02/24 - Amélie Gruel (IMS lab, Université de Bordeaux, France)

dataset=''
fps=24
visu='false'

OPTSTRING="d:f:v"
while getopts $OPTSTRING flag; do
  case $flag in
    f) fps="${OPTARG}" ;;
    v) visu='true' ;;
    d) dataset="${OPTARG}" ;;
    ?) echo "[Error] The correct options are -d (link to the dataset with RGB videos), -f (number of frames per second, by default 24) and -v (to visualise the events produced)."
       exit 1;;
  esac
done

if [[ $dataset == '' ]]; then
    echo "[Error] The dataset must be defined using the -d flag."; 
    exit 1;
fi

echo "Generating frames..."
./vid2frames.sh -d $dataset -f $fps
echo ""

echo "Generating events..."
python3 getEvents.py $dataset -fps $fps
rm -rf $dataset/frames*

if [[ $visu == 'true' ]]; then
    for file in $(ls -R $dataset | grep "events.*npy"); do 
        echo "Visualise" $file;
        python3 visualise_events.py $dataset$file -u nano -nd -s -si $dataset
    done
fi