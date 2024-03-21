import cv2
import os
import numpy as np
import math
import time

live_feed_dir = 'live_feed'  # Directory containing the images
refresh_rate = 2  # How often to refresh the images (in seconds)

def get_image_files(directory):
    """Get a list of image file paths in the specified directory"""
    supported_exts = ('.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff')
    return [os.path.join(directory, f) for f in os.listdir(directory) if f.endswith(supported_exts)]

def create_composite_image(image_files, images_per_row=4):
    """Create a composite image from the list of image files"""
    images = [cv2.imread(file) for file in image_files if cv2.imread(file) is not None]
    if not images:
        return None
    
    # Assume all images are the same size
    img_h, img_w = images[0].shape[:2]
    num_images = len(images)
    num_rows = math.ceil(num_images / images_per_row)
    
    # Create a black canvas
    composite_image = np.zeros((img_h * num_rows, img_w * images_per_row, 3), dtype=np.uint8)
    
    for idx, img in enumerate(images):
        x = (idx % images_per_row) * img_w
        y = (idx // images_per_row) * img_h
        composite_image[y:y+img_h, x:x+img_w, :] = img
    
    return composite_image

def display_images(directory):
    cv2.namedWindow('Live Feed', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('Live Feed', 800, 600)
    
    while True:
        image_files = get_image_files(directory)
        composite_image = create_composite_image(image_files)
        
        if composite_image is not None:
            cv2.imshow('Live Feed', composite_image)
        else:
            cv2.imshow('Live Feed', np.zeros((400, 400, 3), dtype=np.uint8))  # Display a black window if no images
        
        cv2.waitKey(refresh_rate * 1000)  # Refresh rate in milliseconds

if __name__ == "__main__":
    display_images(live_feed_dir)
