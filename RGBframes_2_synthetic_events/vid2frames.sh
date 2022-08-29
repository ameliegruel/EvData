# HERE: change dataset path to where the mp4 videos are stored
dataset="/home/amelie/Scripts/APROVIS3D_CoastlineDetection/data/2022_i3S_TestBeachDataset/"

fps=24  # 24 frames per second

for file in $(ls -R $dataset); do
    if [[ ${file: -4} == ".MP4" ]]; then
        echo $file;
        mkdir -p $path"frames_"${file::-4}/;
        ffmpeg -i $path$file -vf hue=s=0 -r $fps $path"frames_"${file::-4}/frame_%06d.png;
    elif [[ $file =~ ^/.* ]]; then
        path=${file::-1}/;
    fi
done