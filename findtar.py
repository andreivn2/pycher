import cv2
import numpy as np
import os

def find_target_coordinates(threshold=0.7):
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(script_dir, "target.png")
    capture_path = os.path.join(script_dir, "ss.png")

    img_rgb = cv2.imread(capture_path, cv2.IMREAD_GRAYSCALE)
    template_orig = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    if img_rgb is None or template_orig is None:
        print("Error loading images.")
        return None

    best_val = -1
    best_pt = None
    best_scale = 1.0

    scales = np.linspace(0.75, 1.25, 20)  # Try 20 scales from 50% to 150%

    for scale in scales:
        # Resize template
        template = cv2.resize(template_orig, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
        h, w = template.shape[:2]

        if h > img_rgb.shape[0] or w > img_rgb.shape[1]:
            continue  # Skip if resized template is bigger than image

        res = cv2.matchTemplate(img_rgb, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        print(f"Template matching at scale {scale:.2f} -- confidence {max_val:.2f}")

        if max_val > best_val:
            best_val = max_val
            best_pt = (max_loc[0] + w // 2, max_loc[1] + h // 2)
            best_match = template
            best_scale = scale

    print(f"Target found at: {best_pt} (scale: {best_scale:.2f}, confidence: {best_val:.2f})")
    width, height = int(template_orig.shape[0] * best_scale), int(template_orig.shape[1] * best_scale)  # Width and height of the rectangle

    # Calculate the bottom-right corner of the rectangle
    top_left = (best_pt[0] - height//2, best_pt[1] - width//2)
    bottom_right = (best_pt[0] + height//2,best_pt[1] + width//2)

    # Draw the rectangle on the image
    # The color is in BGR format, here it's red (255, 0, 0)
    # Thickness is 2 pixels
    cv2.rectangle(img_rgb, top_left, bottom_right, (0, 0, 255), 2)

    # Optionally, save the image
    cv2.imwrite('ss.png', img_rgb)

    return (best_pt, best_val)

if __name__ == "__main__":
    find_target_coordinates()
