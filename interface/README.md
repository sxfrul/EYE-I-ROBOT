6/4/2024
> - **fixed amp issue (MAX98357)**
>   <br> * Add line `dtparam=audio=off` in config.txt on raspbian (bookworm) **WITH NO RECOMMENDED SOFTWARE**
>   
> - **fixing 'no camera detected'**
>   <br> * Enable the extended features such as the camera: `start_x=1`
>   <br> * Needs to be at least 128M for the camera processing: `gpu_mem=128`
>   <br> * Comment/remove the existing camera_auto_detect line since this causes issues with OpenCV/V4L2 capture: `#camera_auto_detect=1`
