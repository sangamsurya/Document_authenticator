import cv2
import numpy as np
import math

def calculate_psnr(img1, img2):
    psnr_total = 0
    for i in range(3):  # B, G, R
        mse = np.mean((img1[..., i] - img2[..., i]) ** 2)
        if mse == 0:
            psnr_total += float('inf')
        else:
            PIXEL_MAX = 255.0
            psnr_total += 20 * math.log10(PIXEL_MAX / math.sqrt(mse))
    return psnr_total / 3

def calculate_snr(img1, img2):
    snr_total = 0
    for i in range(3):  # B, G, R
        signal_power = np.mean(img1[..., i] ** 2)
        noise_power = np.mean((img1[..., i] - img2[..., i]) ** 2)
        if noise_power == 0:
            snr_total += float('inf')
        else:
            snr_total += 10 * math.log10(signal_power / noise_power)
    return snr_total / 3

# Load original and noisy color images
original = cv2.imread('image4.jpg')
noisy = cv2.imread('output/stego_image_rev_flask.png')

if original is None or noisy is None:
    raise FileNotFoundError("Image paths are incorrect.")

if original.shape != noisy.shape:
    raise ValueError("Images must be the same size and type.")

# PSNR & SNR before denoising
psnr = calculate_psnr(original, noisy)
snr= calculate_snr(original, noisy)

print("=== Color Image PSNR/SNR ===")
print(f"PSNR: {psnr:.2f} dB, SNR: {snr:.2f} dB")

