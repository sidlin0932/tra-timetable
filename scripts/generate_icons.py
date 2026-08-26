# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw, ImageFont
import os

def create_pwa_icon(size, filename):
    # Create an image with rounded dark-blue to cyan gradient background
    img = Image.new('RGBA', (size, size), (15, 23, 42, 255)) # Dark slate background #0f172a
    draw = ImageDraw.Draw(img)
    
    # Draw rounded cyan/blue circle
    padding = size // 10
    draw.ellipse([padding, padding, size - padding, size - padding], fill=(2, 132, 199, 255)) # Primary blue #0284c7

    # Draw a stylized train front in white and gold
    # Train body
    train_w = size * 0.55
    train_h = size * 0.52
    train_x = (size - train_w) / 2
    train_y = (size - train_h) / 2 + size * 0.02
    
    # Top curved roof
    draw.rounded_rectangle([train_x, train_y, train_x + train_w, train_y + train_h], radius=int(size * 0.08), fill=(255, 255, 255, 255))
    
    # Windshield window
    win_w = train_w * 0.78
    win_h = train_h * 0.32
    win_x = train_x + (train_w - win_w) / 2
    win_y = train_y + train_h * 0.12
    draw.rounded_rectangle([win_x, win_y, win_x + win_w, win_y + win_h], radius=int(size * 0.04), fill=(15, 23, 42, 255))
    
    # Dual headlights
    light_r = size * 0.04
    l1_x = train_x + train_w * 0.22
    l2_x = train_x + train_w * 0.78
    l_y = train_y + train_h * 0.72
    draw.ellipse([l1_x - light_r, l_y - light_r, l1_x + light_r, l_y + light_r], fill=(245, 158, 11, 255)) # Amber headlight
    draw.ellipse([l2_x - light_r, l_y - light_r, l2_x + light_r, l_y + light_r], fill=(245, 158, 11, 255))
    
    # Bottom bumper / track bar
    bar_w = train_w * 0.9
    bar_h = size * 0.035
    bar_x = train_x + (train_w - bar_w) / 2
    bar_y = train_y + train_h + size * 0.02
    draw.rounded_rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], radius=int(bar_h/2), fill=(255, 255, 255, 255))

    img.save(filename, 'PNG')
    print(f"Saved {filename} ({size}x{size})")

create_pwa_icon(192, 'f:/Antigravity/台鐵時刻表0701/icon-192.png')
create_pwa_icon(512, 'f:/Antigravity/台鐵時刻表0701/icon-512.png')
