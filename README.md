# skulpt_proc
Quick and dirty code to extract values from skulpt screen caps.
Installation:
  Download this repository
  cd into the skulpt_proc folder
  activate your base conda environment
    conda activate base
    (it may make sense to update conda now as well)
    conda update conda
  create skulpt environment:
    conda env create -f skulpt_env.yml
  activate the new skulpt environment:
    conda activate skulpt
  copy the proc_skulpt_images.py folder somewhere on your system (e.g. ~/python)

## usage: proc_skulpt_imgs.py [-h] input_folder dest_folder

  Process Skulpt ScreenCap image files.

  positional arguments:
    input_folder  The input folder
    dest_folder   The destination folder

  options:
    -h, --help    show this help message and exit

The script will process all PNG images in the 'input_folder' and 
save them as a csv in 'dest_folder', in the format:
   skulpt_data_[date string].csv
 
## Example
  ### if you run:
  python ~/python/proc_skulpt_imgs.py  /Data/SkulptImages  \`pwd\` <br>
  the script will process all .PNG images in /Data/SkulptImages, <br>
  and save the resulting csv in the present working directory (\`pwd\`) <br>
  which is just the folder from which you called the script. 

Note that the script only saves values recorded in RS2, but you can <br>
edit the keepcols list in the script to retain more or fewer items.
