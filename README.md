# Video_QC_Checker
Video Quality Control 

checks for:
- [x] Short Scene Cut (less then [fps - 5] - you can change this threshold)
- [x] Black frames (full black pixels)

## Installation

1. Clone the repository
2. Install dependencies:
  ```bash
    pip install opencv-python
    pip install tqdm
  ```
## Usage
```bash
python Video_QC.py {Path_To_Video_File}
```
  
Or run on GPU using CUDA (NVIDIA GPU's) (***require to compile opencv with CUDA***)
```bash
python Video_QC_GPU_CUDA.py {Path_To_Video_File}
```
