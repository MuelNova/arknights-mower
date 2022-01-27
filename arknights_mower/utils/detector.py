import numpy as np

from . import typealias as tp
from .log import logger


def confirm(img: tp.Image) -> tp.Coordinate:
    """
    检测是否出现确认界面
    """
    height, weight, _ = img.shape

    # 4 scan lines: left, right, up, down
    left, right = weight // 4 * 3 - 10, weight // 4 * 3 + 10
    up, down = height // 2 - 10, height // 2 + 10

    # the R/G/B must be the same for a single pixel in the specified area
    if (img[up:down, left:right, :-1] != img[up:down, left:right, 1:]).any():
        return None

    # the pixel average of the specified area must be in the vicinity of 55
    if abs(np.mean(img[up:down, left:right]) - 55) > 5:
        return None

    # set a new scan line: up
    up = 0
    for i in range(down, height):
        for j in range(left, right):
            if np.ptp(img[i, j]) != 0 or abs(img[i, j, 0] - 13) > 3:
                break
            elif j == right-1:
                up = i
        if up:
            break
    if up == 0:
        return None

    # set a new scan line: down
    down = 0
    for i in range(up, height):
        for j in range(left, right):
            if np.ptp(img[i, j]) != 0 or abs(img[i, j, 0] - 13) > 3:
                down = i
                break
        if down:
            break
    if down == 0:
        return None

    # detect successful
    point = (weight // 2, (up + down) // 2)
    logger.debug(f'detector.confirm: {point}')
    return point


def infra_notification(img: tp.Image) -> tp.Coordinate:
    """
    检测基建内是否存在蓝色通知
    前置条件：已经处于基建内
    """
    height, weight, _ = img.shape

    # set a new scan line: right
    right = weight
    while np.max(img[:, right-1]) < 100:
        right -= 1
    right -= 1

    # set a new scan line: up
    up = 0
    for i in range(height):
        if img[i, right, 0] < 100 < img[i, right, 1] < img[i, right, 2]:
            up = i
            break
    if up == 0:
        return None

    # set a new scan line: down
    down = 0
    for i in range(up, height):
        if not (img[i, right, 0] < 100 < img[i, right, 1] < img[i, right, 2]):
            down = i
            break
    if down == 0:
        return None

    # detect successful
    point = (right - 10, (up + down) // 2)
    logger.debug(f'detector.infra_notification: {point}')
    return point


def announcement_close(img: tp.Image) -> tp.Coordinate:
    """
    检测「关闭公告」按钮
    """
    height, weight, _ = img.shape

    # 4 scan lines: left, right, up, down
    up, down = 0, height // 4
    left, right = weight // 4 * 3, weight

    sumx, sumy, cnt = 0, 0, 0
    for i in range(up, down):
        line_cnt = 0
        for j in range(left, right):
            if np.ptp(img[i, j]) == 0 and abs(img[i, j, 0] - 89) < 3:  # condition
                sumx += i
                sumy += j
                cnt += 1
                line_cnt += 1

                # the number of pixels meeting the condition in one line reaches 100
                if line_cnt >= 100:
                    return None

                # the number of pixels meeting the condition reaches 2000
                if cnt >= 2000:
                    # detect successful
                    point = (sumy // cnt, sumx // cnt)
                    logger.debug(f'detector.announcement_close: {point}')
                    return point

    return None


def visit_next(img: tp.Image) -> tp.Coordinate:
    """
    检测「访问下位」按钮
    """
    height, weight, _ = img.shape

    # set a new scan line: right
    right = weight
    while np.max(img[:, right-1]) < 100:
        right -= 1
    right -= 1

    # set a new scan line: up
    up = 0
    for i in range(height):
        if img[i, right, 0] > 150 > img[i, right, 1] > 40 > img[i, right, 2]:
            up = i
            break
    if up == 0:
        return None

    # set a new scan line: down
    down = 0
    for i in range(up, height):
        if not (img[i, right, 0] > 150 > img[i, right, 1] > 40 > img[i, right, 2]):
            down = i
            break
    if down == 0:
        return None

    # detect successful
    point = (right - 10, (up + down) // 2)
    logger.debug(f'detector.visit_next: {point}')
    return point
