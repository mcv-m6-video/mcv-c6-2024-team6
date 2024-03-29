import numpy as np
import matplotlib.pyplot as plt
import cv2
import os
import flow_vis
import copy

import optical_flow.utils  as utils

import matplotlib.cm as cm

from matplotlib.colors import Normalize
from PIL import Image
import math



def visualize_optical_flow_error(GT, OF_pred, output_dir = "./results/"):
    error_dist = u_diff, v_diff = GT[:, :, 0] - \
        OF_pred[:, :, 0], GT[:, :, 1] - OF_pred[:, :, 1]
    error_dist = np.sqrt(u_diff ** 2 + v_diff ** 2)

    max_range = int(math.ceil(np.amax(error_dist)))
    

    plt.clf()
    plt.figure(figsize=(8, 5))
    plt.title('MSEN Distribution')
    plt.hist(error_dist.ravel(),
             bins=30, range=(0.0, max_range))
    plt.ylabel('Count')
    plt.xlabel('Mean Square Error in Non-Occluded Areas')
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, "MSEN_hist.png"))
    plt.close()



def visualize_flowvis(flow, filepath):
    flow_color = flow_vis.flow_to_color(flow[:, :, :2], convert_to_bgr=True)
    cv2.imwrite(filepath, flow_color)

def visualize_magdir(im1_path: str, flow, filename):
    im1 = np.array(Image.open(im1_path).convert('RGB'))
    im1 = im1.astype(float) / 255.
    hsv = np.zeros(im1.shape, dtype=np.uint8)
    hsv[:, :, 0] = 255
    hsv[:, :, 1] = 255
    mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    hsv[..., 0] = ang * 180 / np.pi / 2
    hsv[..., 2] = cv2.normalize(mag, None, 0, 255, cv2.NORM_MINMAX)
    bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    cv2.imwrite(f'./results/magnitude_dir_{filename}.png', bgr)


def visualize_arrow(im1_path: str, flow, filename: str):
    im1 = cv2.imread(im1_path)
    im1 = cv2.cvtColor(im1, cv2.COLOR_BGR2RGB)
    h, w = flow.shape[:2]
    flow_horizontal = flow[:, :, 0]
    flow_vertical = flow[:, :, 1]

    step_size = 12
    X, Y = np.meshgrid(np.arange(0, w, step_size), np.arange(0, h, step_size))
    U = flow_horizontal[Y, X]
    V = flow_vertical[Y, X]
    
    magnitude = np.sqrt(U**2 + V**2)
    norm = Normalize()
    norm.autoscale(magnitude)
    cmap = cm.inferno
    
    plt.figure(figsize=(10, 10))
    plt.imshow(im1)
    plt.quiver(X, Y, U, V, norm(magnitude), angles='xy', scale_units='xy',  scale=1, cmap=cmap, width=0.0015)
    plt.axis('off')
    plt.savefig(f'./results/arrow_{filename}.png', dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close()


def visualize_direction_idx_plot(im1_path: str, flow, filename):
    im1 = np.array(Image.open(im1_path).convert('RGB'))
    im1 = im1.astype(float) / 255.
    fig, ax = plt.subplots(figsize=(8, 8))
    
    # Background
    ax.imshow(im1)

    step = 10
    x, y = np.meshgrid(np.arange(0, flow.shape[1], step), np.arange(0, flow.shape[0], step))
    u = flow[y, x, 0]
    v = flow[y, x, 1]
    
    direction = np.arctan2(v, u)
    norm = plt.Normalize(vmin=-np.pi, vmax=np.pi)
    cmap = plt.cm.hsv
    colors = cmap(norm(direction))
    colors = colors.reshape(-1, colors.shape[-1])
    quiver = ax.quiver(x, y, u, v, color=colors, angles='xy', scale_units='xy', scale=1, width=0.0015, headwidth=5)

    sm = plt.cm.ScalarMappable(cmap=cmap, norm=norm)
    sm.set_array([])  # Empty array for colorbar
    cbar = fig.colorbar(sm, ax=ax, ticks=[-np.pi, -np.pi/2, 0, np.pi/2, np.pi])
    cbar.set_ticklabels(['-π', '-π/2', '0', 'π/2', 'π'])
    cbar.set_label('Direction')
    plt.savefig(f'./results/{filename}_direction.png', dpi=300, bbox_inches='tight')
    plt.close()




def plot_optical_flow_quiver(ofimg, original_image, output_dir = "./results", step=20, scale=.15, flow_with_camera=False):
    magnitude = np.hypot(ofimg[:, :, 0], ofimg[:, :, 1])

    if flow_with_camera:
        ofimg = np.array(ofimg).astype(np.int16)
        ofimg *= -1

    x, y = np.meshgrid(
        np.arange(0, magnitude.shape[1]), np.arange(0, magnitude.shape[0]))
    plt.clf()

    h, w = ofimg.shape[:2]
    fig, ax = plt.subplots(figsize=(w/100, h/100))
    ax.quiver(x[::step, ::step], y[::step, ::step], ofimg[::step, ::step, 0], ofimg[::step,
               ::step, 1], magnitude[::step, ::step], scale_units='xy', angles='xy', scale=scale)
    ax.imshow(original_image, cmap='gray')
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, f'optical_flow_quiver{"_camera" if flow_with_camera else ""}.png'), bbox_inches='tight', pad_inches=0)
    plt.close()


def plot_optical_flow_surface(flow, original_image, output_dir = "./results"):
    plt.clf()
    labeled = flow[..., 2]

    # Normalize flow to range [0, 1]
    flow_norm = flow / (np.abs(flow).max() + 1e-8)
    u, v = flow_norm[:, :, 0], flow_norm[:, :, 1]

    # Calculate phase angle using arctan2
    phase = np.arctan2(v, u) / (2 * np.pi) % 1
    magnitude = np.sqrt(u ** 2 + v ** 2)

    # Standarize phase
    phase = utils.standarize(phase)

    hsv = np.stack([phase, np.ones_like(phase), np.ones_like(phase)]).transpose(
        1, 2, 0).astype(np.float32)
    hsv[:, :, 0] *= 179
    hsv[:, :, 1:] *= 255
    rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB) / 255
    rgba = np.dstack((rgb, labeled))

    fig, ax = plt.subplots(subplot_kw={"projection": "3d"})

    x, y = np.meshgrid(
        np.arange(0, magnitude.shape[1]), np.arange(0, magnitude.shape[0]))
    
    surf = ax.plot_surface(x, -magnitude, -y, facecolors=rgba,
                           linewidth=0, antialiased=False)

    IMAGE_Z = np.ones_like(magnitude) * 0

    rgbimage = cv2.cvtColor(original_image, cv2.COLOR_BGR2RGB) / 255
    rgbaimg = np.dstack((rgb, np.ones_like(magnitude) * 0.5))
    ax.plot_surface(x, IMAGE_Z, -y, facecolors=rgbimage,
                            linewidth=0, antialiased=True)
    os.makedirs(output_dir, exist_ok=True)
    fig.savefig(os.path.join(output_dir, 'optical_flow_surface.png'), bbox_inches='tight', pad_inches=0)
    plt.close()
    
    
    
def plot_optical_flow_hsv(flow, 
                          labelled=None, 
                          hide_unlabeled=True, 
                          use_whole_range=False, 
                          value=1, 
                          onlyphase=False, 
                          onlymagnitude=False, 
                          output_dir="./results/"):
    # Normalize flow to range [0, 1]
    flow_norm = flow / (np.abs(flow).max() + 1e-8)
    u, v = flow_norm[:, :, 0], flow_norm[:, :, 1]

    # Calculate phase angle using arctan2
    phase = np.arctan2(v, u) / (2 * np.pi) % 1
    magnitude = np.sqrt(u ** 2 + v ** 2)

    # Standarize phase
    phase = utils.standarize(phase)
    
    # Normalize magnitude
    # Credit for thr to Team1
    clip_th = np.quantile(magnitude, 0.95)
    magnitude = np.clip(magnitude, 0, clip_th)
    magnitude = magnitude / magnitude.max()

    if use_whole_range:
        phase = cv2.equalizeHist((255 * phase).astype(np.uint8)) / 255

    hsv = np.stack([phase, magnitude, np.ones_like(phase) * value]
                   ).transpose(1, 2, 0).astype(np.float32)

    if onlymagnitude:
        hsv[:, :, 0] = .5
    elif onlyphase:
        hsv[:, :, 1:] = 1

    hsv[:, :, 0] *= 179
    hsv[:, :, 1:] *= 255

    rgb = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)

    if hide_unlabeled:
        rgb = rgb * labelled.astype(np.uint8)[:, :, None]

    h, w = flow.shape[:2]
    plt.clf()
    fig, ax = plt.subplots(figsize=(w/100, h/100))
    ax.imshow(rgb)
    ax.axis('off')
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    os.makedirs(output_dir, exist_ok=True)
    plt.savefig(os.path.join(output_dir, 'optical_flow_hsv.png'), bbox_inches='tight', pad_inches=0)
    plt.close()




if __name__ == "__main__":
    
    path_to_save = "./results"
    os.makedirs("./results", exist_ok=True)
    
    
    path_1 = 'data_stereo_flow/training/image_0/000045_10.png'
    path_2 = 'data_stereo_flow/training/image_0/000045_11.png'
    path_gt_non_oc = 'data_stereo_flow/training/flow_noc/000045_10.png'
    path_flow = 'results/OF_post_process2.png'#'data_stereo_flow/training/image_0/000045_11.png'
    
    image_1 = cv2.imread(path_1)   
    image_2 = cv2.imread(path_2)
    image_3 = cv2.imread(path_flow)
    
    gt = cv2.imread(path_gt_non_oc)
    
    #visualize_optical_flow_error(GT=gt, OF_pred=image_3)
    visualize_direction_idx_plot(im1_path=path_1, flow=image_3.astype(np.float32), filename="1")
    #visualize_flowvis(flow=image_3, filename="1")
    #plot_optical_flow_hsv(flow=image_3[:,:,:2], labelled=image_3[:,:,2])
    #plot_optical_flow_quiver(image_3, image_1)
    #plot_optical_flow_quiver(image_3, image_1, flow_with_camera=True)
    #plot_optical_flow_surface(image_3, image_1)
    
    
