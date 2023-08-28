# bladebit wrapper

This wrapper will run bladebit_cuda. It will also delete plot if needed to replot a farm and ensure to maximise your farm size.

## Install

Ensure you have python. then run

````shell
python3 -m venv .
source bin/activate
pip install requierement.txt
````

## Attention warning

We provide binaries build by ourself from [bladebit](https://github.com/Chia-Network/bladebit). We have choosen this for oen main reason, we are using a special branch [cuda-windows-fix](https://github.com/Chia-Network/bladebit/tree/cuda-windows-fix) wich include plot support for 128Go/256Go in ram for Windows & Linux.
Once it will be merged, we will get it from [official chia repo](https://downloads.chia.net/).

## Run it