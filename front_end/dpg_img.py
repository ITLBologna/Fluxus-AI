import cv2
import dearpygui.dearpygui as dpg
import numpy as np


def __resize2w(img, desired_w):
    # type: (np.ndarray, int) -> np.ndarray
    """
    Resize image to the desired width keeping its original aspect ratio.

    :param img: image to resize
    :param desired_w: desired with for the output image
    :return: resized image
    """
    height, width = img.shape[0:2]
    desired_h = int(round((desired_w * height) / width))
    return cv2.resize(
        img, (desired_w, desired_h),
        interpolation=cv2.INTER_AREA
    )


def __resize_and_pad(img, aspect_ratio, desired_w):
    # type: (np.ndarray, float, int) -> np.ndarray
    """
    Resize image to the desired width keeping its original aspect ratio,
    then pad it in order to reach the desired aspect ratio `aspect_ratio`.

    :param img: image to resize and pad
    :param aspect_ratio: desired aspect ratio for the output image
    :param desired_w: desired width for the output image
    :return: resized and padded image
    """
    pad_top, pad_bottom = 0, 0
    pad_left, pad_right = 0, 0

    # (1) resize to desired width (keeping original aspect ratio)
    img = __resize2w(img, desired_w)

    # (2) pad image to reach the desired aspect ratio
    height, width = img.shape[0:2]
    current_ratio = width / height
    if current_ratio < aspect_ratio:
        # image is more vertical than desired => W needs to be increased
        diff = (aspect_ratio * height) - width
        pad_right += int(np.ceil(diff / 2))
        pad_left += int(np.floor(diff / 2))
    elif current_ratio > aspect_ratio:
        # image is more horizontal than desired => H needs to be increased
        diff = ((1 / aspect_ratio) * width) - height
        pad_top += int(np.floor(diff / 2))
        pad_bottom += int(np.ceil(diff / 2))

    img = np.pad(
        img, ((pad_top, pad_bottom), (pad_left, pad_right), (0, 0)),
        'constant', constant_values=128
    )

    # (3) resize image again if its width (after padding)
    # does is not equal to the desired width
    if img.shape[1] != desired_w:
        img = __resize2w(img, desired_w)

    return img


def init_texture(tag, img, aspect_ratio, desired_w):
    # type: (str, np.ndarray, float, int) -> str
    """
    Init DPG texture from a numpy image `img` and bring it to
    the desired size and aspect ratio.

    :param tag: dpg tag for the texture
    :param img: numpy image you want to convert to dpg texture
    :param aspect_ratio: desired aspect ratio for the output texture
    :param desired_w: desired width for the output texture
    :return: tag of the output texture
    """
    img = __resize_and_pad(img, aspect_ratio, desired_w)
    h, w = img.shape[0], img.shape[1]
    data = (img.ravel().astype(np.float32)) / 255.

    with dpg.texture_registry():
        texture = dpg.add_raw_texture(
            w, h, data, tag=tag,
            format=dpg.mvFormat_Float_rgb
        )

    return texture


def change_texture(tag, img, aspect_ratio, desired_w):
    # type: (str, np.ndarray, float, int) -> None
    """
    Change DPG texture with the given tag using the input numpy image `img`.
    :param tag: tag of the texture you want to change
    :param img: numpy image for the new texture
    :param aspect_ratio: desired aspect ratio for the new texture
    :param desired_w: desired width for the new texture
    """
    img = __resize_and_pad(img, aspect_ratio, desired_w)
    data = (img.ravel().astype(np.float32)) / 255.
    dpg.set_value(tag, data)
