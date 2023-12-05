import os
import cv2
import numpy as np
import requests
import pyfakewebcam
import datetime
from videocaptureasync import VideoCaptureAsync

# fetch the mask with retries (the app needs to warmup and we're lazy)
# e v e n t u a l l y c o n s i s t e n t
def get_mask_bodypix(frame, bodypix_url='http://172.19.0.2:9000'):
    mask = None
    while mask is None:
        try:
            _, data = cv2.imencode(".jpg", frame)
            r = requests.post(
                url=bodypix_url,
                data=data.tobytes(),
                headers={'Content-Type': 'application/octet-stream'})
            mask = np.frombuffer(r.content, dtype=np.uint8)
            mask = mask.reshape((frame.shape[0], frame.shape[1]))
        except KeyboardInterrupt:
            raise
        except:
            print("mask request failed, retrying")
    return mask

def post_process_mask(mask):
    mask = cv2.dilate(mask, np.ones((10,10), np.uint8) , iterations=1)
    mask = cv2.blur(mask.astype(float), (30,30))
    return mask

def shift_image(img, dx, dy):
    img = np.roll(img, dy, axis=0)
    img = np.roll(img, dx, axis=1)
    if dy>0:
        img[:dy, :] = 0
    elif dy<0:
        img[dy:, :] = 0
    if dx>0:
        img[:, :dx] = 0
    elif dx<0:
        img[:, dx:] = 0
    return img

def mask_frame(frame):
    mask = get_mask_bodypix(frame)

    return mask

# composite the foreground and background
def blend_frame(frame, background, mask):
    inv_mask = 1-mask
    #if args.enable_hologram:
    #    inv_mask += 0.1*mask
    result = frame
    for c in range(frame.shape[2]):
        result[:,:,c] = frame[:,:,c]*mask + background[:,:,c]*inv_mask
        
    return result

try:
    import argparse
    parser = argparse.ArgumentParser(description='Virtual background fake webcam')
    parser.add_argument('-i', '--input', default='/dev/video1', help='real webcam device')
    parser.add_argument('-o', '--output', default='/dev/video20', help='loopback video device')
    parser.add_argument('--width', default=960, help='video width')
    parser.add_argument('--height', default=720, help='video height')
    parser.add_argument('background', default=['data/*'], nargs='*', help='background files (images or videos)')

    args = parser.parse_args()
   
 
    # setup access to the *real* webcam
    print('Opening webcam', args.input, '...')

    cap = VideoCaptureAsync(args.input, args.width, args.height)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, args.width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, args.height)
    cap.set(cv2.CAP_PROP_FPS, 30)
    
    # setup the fake camera
    fake = None
    if args.output != "imshow":
        print('Writing to loopback device', args.output, '...')
        fake = pyfakewebcam.FakeWebcam(args.output, args.width, args.height)
    
    # load the virtual background
    background_index = 0
    background = None
    bg_cap = None
    
    import glob
    background_filenames = []
    for background_filename in args.background:
        background_filenames += glob.glob(background_filename)
    if len(background_filenames) == 0:
        print("No background files found on", args.background)
        exit(1)

    def set_background():
        global background_index
        global background
        global bg_cap
        background_filename = background_filenames[background_index % len(background_filenames)]

        print("Loading background", background_filename)
        try:
            bg_cap = cv2.VideoCapture(background_filename)
        except:
            background = cv2.imread(background_filename)
            background = cv2.resize(background, (args.width, args.height))

        background_index += 1

    now = datetime.datetime.now()
    nframe = 1
    frame = None
    mask = None
    
    # frames forever
    set_background()
    while True:
        # Capture background
        if bg_cap:
            _, new_background = bg_cap.read()

            if new_background is None:
                # Try to loop back to the beginning
                bg_cap.set(cv2.CAP_PROP_POS_FRAMES, 1)
                _, new_background = bg_cap.read()

            if new_background is not None:
                background = cv2.resize(new_background, (args.width, args.height))
   
        # Capture webcam 
        nframe += 1
        if frame is None or nframe > 5:
            nframe = 0
            _, frame = cap.read()
            mask = mask_frame(frame)
        else:
            cap.read()

        # Blend webcam image into background
        if background is not None and frame is not None and mask is not None:
            final_frame = frame.copy()
            final_frame = blend_frame(final_frame, background, mask)
            if fake:
                # fake webcam expects RGB
                final_frame = cv2.cvtColor(final_frame, cv2.COLOR_BGR2RGB)
                fake.schedule_frame(final_frame)
            else:
                cv2.imshow("mask", final_frame)
                cv2.waitKey(1)
    
except KeyboardInterrupt:
    exit(0)