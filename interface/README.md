6/4/2024
- fixed amp issue (MAX98357) by adding dtparam=audio=off on raspbian (bookworm) WITH NO RECOMMENDED SOFTWARE

6/4/2024
- fixing 'no camera detected'
# This enables the extended features such as the camera.
start_x=1

# This needs to be at least 128M for the camera processing, if it's bigger you can just leave it as is.
gpu_mem=128

# You need to commment/remove the existing camera_auto_detect line since this causes issues with OpenCV/V4L2 capture.
#camera_auto_detect=1