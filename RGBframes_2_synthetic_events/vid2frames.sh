# Bash script to transform a RGB video (originally in MP4 / AVI / FLV) into grayscale frames (later used by vid2e to produce events)
# Takes as input argument:
#   1) dataset (mandatory): directory where the RGB video(s) are stored
#   2) fps (optionnal, default=24): number of frames per second in the input RGB video
# 05/21 - Amélie Gruel (I3S, Université Côte d'Azur, France)

dataset=''
fps=24
visu='false'

OPTSTRING="d:f:"
while getopts $OPTSTRING flag; do
  case $flag in
    f) fps="${OPTARG}" ;;
    d) dataset="${OPTARG}" ;;
    ?) echo "[Error] The correct options are -d (link to the dataset with RGB videos), -f (number of frames per second, by default 24) and -v (to visualise the events produced)."
       exit 1;;
  esac
done

if [[ $dataset == '' ]]; then
    echo "[Error] The dataset must be defined using the -d flag."; 
    exit 1;
fi

for file in $(ls -R $dataset); do
    filename=`echo $file | sed 's,^.*[^/]*/,,'`
    if [[ ${filename: -4} == ".mp4" ]] || [[ ${filename: -4} == ".flv" ]] || [[ ${filename: -4} == ".AVI" ]]; then

        START=$(date +%s.%N)

        echo $filename 
        mkdir -p $dataset"frames_"${filename::-4}/;
        ffmpeg -i $path$file -vf hue=s=0 -r $fps $dataset"frames_"${filename::-4}/frame_%06d.png;

        END=$(date +%s.%N)
        DIFF=$(echo "$END - $START" | bc)
        echo "time" $filename ":" $DIFF
        echo ""

    elif [[ $file =~ ^/.* ]]; then
        path=${file::-1}/;
    fi
done
