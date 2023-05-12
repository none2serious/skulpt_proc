# skulpt_proc
Quick and dirty code to extract values from skulpt screen caps. <br><br>
## Installation: <br>
  Download this repository <br>
  cd into the skulpt_proc folder <br>
  activate your base conda environment <br>
    &nbsp;&nbsp;&nbsp;&nbsp; `conda activate base` <br>
    &nbsp;&nbsp;&nbsp;&nbsp; (it may make sense to update conda now as well) <br>
    &nbsp;&nbsp;&nbsp;&nbsp; `conda update conda` <br>
  create skulpt environment: <br>
  &nbsp;&nbsp;&nbsp;&nbsp;`conda env create -f skulpt_env.yml` <br>
  activate the new skulpt environment: <br>
  &nbsp;&nbsp;&nbsp;&nbsp;`conda activate skulpt` <br>
  copy the proc_skulpt_images.py folder somewhere on your system. A good place<br>
  might be a python folder in your home directory (e.g. ~/python) <br>

## usage: `proc_skulpt_imgs.py [-h] input_folder dest_folder`
  `Process Skulpt ScreenCap image files.` <br>
  `positional arguments:` <br>
   ` input_folder  The input folder` <br>
   ` dest_folder   The destination folder` <br>
 <br>
  `options:` <br>
    `-h, --help    show this help message and exit` <br>

The script will process all PNG images in the 'input_folder' and  <br>
save them as a csv in 'dest_folder', in the format: <br>
   skulpt_data_[date string].csv <br>
  <br>
## Example
  ### if you run:
  ```
  python ~/python/proc_skulpt_imgs.py  /Data/SkulptImages  `pwd` 
  ```
  the script will process all .PNG images in /Data/SkulptImages, <br>
  and save the resulting csv in the present working directory (\`pwd\`) <br>
  which is just the folder from which you called the script. 

Note that the script only saves values recorded in RS2, but you can <br>
edit the keepcols list in the script to retain more or fewer items.
