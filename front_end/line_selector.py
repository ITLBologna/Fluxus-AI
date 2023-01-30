import cv2
import numpy as np

UI_COL1 = (127, 252, 3)[::-1]  # light green
UI_COL2 = (63, 126, 1)[::-1]  # dark green
UI_COL3 = (240, 0, 0)[::-1]  # light red
UI_COL4 = (152, 0, 0)[::-1]  # dark red


def rescale_point(point, scale):
    p = np.array(point) / scale
    p = np.round(p)
    return int(p[0]), int(p[1])


def line2rect(p1, p2):
    p1 = np.array(p1)
    p2 = np.array(p2)

    ln = np.linalg.norm(p1 - p2)
    dx, dy = int(round((ln * 0.25))), int(round((ln * 0.5)))

    x_min = min(p1[0], p2[0]) - dx
    y_min = min(p1[1], p2[1]) - dy

    x_max = max(p1[0], p2[0]) + dx
    y_max = max(p1[1], p2[1]) + dy

    rect = [
        (int(x_min), int(y_min)), (int(x_max), int(y_min)),
        (int(x_max), int(y_max)), (int(x_min), int(y_max))
    ]
    return rect


class LineSelector(object):

    def __init__(self, video_path, win_name):
        self.cap = cv2.VideoCapture(video_path)
        _, self.background = self.cap.read()
        self.frame = self.background.copy()

        h, w, _ = self.frame.shape
        self.frame_height, self.frame_width = h, w

        self.scale = 1280 / w

        self.state = 'empty'

        self.poly = []
        self.p1 = None
        self.p2 = None
        self.out_dict = {
            'p1': None,
            'p2': None,
            'polygon': None
        }

        self.win_name = win_name
        cv2.namedWindow(self.win_name, cv2.WINDOW_AUTOSIZE | cv2.WINDOW_GUI_NORMAL)
        cv2.setMouseCallback(self.win_name, self.click_cb)
        cv2.setWindowProperty(
            self.win_name,
            cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN
        )

        self.stop = False
        self.stop_win = []

        self.texts = (
            f'Use the [left mouse button] to define two points of the straight line.',
            f'Use the [right mouse button] to define at least 4 points of the transition polygon.',
            f'Press [Enter] to confirm your selection.',
            f'Press [F] to reset all points.'
        )
        self.next_frame()

    def draw_header(self, img):
        w, h = 1100, 200
        w0, h0 = (img.shape[1] - w) // 2, 64
        top_bar = img[h0:h0 + h, w0:w0 + w]
        top_bar = top_bar * 0.6
        top_bar = top_bar.astype(np.uint8)
        top_bar = cv2.GaussianBlur(top_bar, ksize=(25, 25), sigmaX=13)

        img[h0:h0 + h, w0:w0 + w] = top_bar
        img = cv2.rectangle(
            img, pt1=(w0, h0), pt2=(w0 + w, h0 + h),
            color=(255, 255, 255), thickness=3
        )

        for i, t in enumerate(self.texts):
            font_scale = 0.76
            tk = 2
            w, h = cv2.getTextSize(t, 0, font_scale, 2)[0]
            img = cv2.putText(
                img=img, text=t, org=(w0 + 30, h0 + 30 + h + h * i * 2),
                fontFace=0, fontScale=font_scale, color=(255, 255, 255),
                thickness=tk, lineType=cv2.LINE_AA, bottomLeftOrigin=False
            )

        return img

    def next_frame(self):
        read_ok, bck = self.cap.read()
        if read_ok:
            bck = self.draw_header(bck)
            self.background = bck
            self.frame = self.background.copy()

    def click_cb(self, event, x, y, *_args):

        if event == cv2.EVENT_LBUTTONUP:
            if self.state in 'empty':
                self.p1 = (x, y)
                self.state = 'start'
            elif self.state == 'moving':
                self.p2 = (x, y)
                self.state = 'done'
            elif self.state == 'done':
                self.p1 = (x, y)
                self.p2 = None
                self.state = 'start'

        if event == cv2.EVENT_MOUSEMOVE:
            if self.state in ['start', 'moving']:
                self.state = 'moving'
                self.p2 = (x, y)

        if event == cv2.EVENT_RBUTTONUP:
            self.poly.append((x, y))

    def render(self):
        self.frame = self.background.copy()

        self.frame = cv2.resize(
            self.frame, (0, 0), fx=self.scale, fy=self.scale,
            interpolation=cv2.INTER_AREA
        )

        if self.p1 is not None and self.p2 is not None:
            self.frame = cv2.line(
                self.frame, self.p1, self.p2,
                thickness=4, color=UI_COL1,
                lineType=cv2.LINE_AA
            )

        for center in [self.p1, self.p2]:
            if center is not None:
                self.frame = cv2.circle(
                    self.frame, center=center, radius=8,
                    thickness=-1, color=UI_COL1,
                    lineType=cv2.LINE_AA
                )
                self.frame = cv2.circle(
                    self.frame, center=center, radius=3,
                    thickness=-1, color=UI_COL2,
                    lineType=cv2.LINE_AA
                )

        for center in self.poly:
            if center is not None:
                self.frame = cv2.circle(
                    self.frame, center=center, radius=8,
                    thickness=-1, color=UI_COL3,
                    lineType=cv2.LINE_AA
                )
                self.frame = cv2.circle(
                    self.frame, center=center, radius=3,
                    thickness=-1, color=UI_COL4,
                    lineType=cv2.LINE_AA
                )

        if self.poly.__len__() >= 3:
            self.frame = cv2.polylines(self.frame, [np.asarray(self.poly)], True, UI_COL3)

        # if self.rect is not None:
        #     self.frame = cv2.rectangle(
        #         self.frame, pt1=self.rect[0], pt2=self.rect[2],
        #         thickness=4, color=UI_COL1, lineType=cv2.LINE_AA
        #     )

        cv2.imshow(self.win_name, self.frame)

    def run(self):
        while not self.stop:
            self.render()
            key = cv2.waitKey(30)

            if cv2.getWindowProperty(self.win_name, 0) < 0:
                self.stop = True
                self.out_dict = None
                break

            if key == -1:
                continue

            elif key == 13:
                p1 = rescale_point(self.p1, self.scale)
                p2 = rescale_point(self.p2, self.scale)
                # rect = line2rect(p1, p2)
                self.poly = [rescale_point(p, self.scale) for p in self.poly]
                self.out_dict = {'p1': p1, 'p2': p2, 'polygon': self.poly, "frame_height": self.frame_height,
                                 "frame_width": self.frame_width}
                if all([self.p1 is not None, self.p1 is not None, len(self.poly) >= 4]):
                    self.stop = True

            elif chr(key) == 'f':
                self.poly = []
                self.p1 = None
                self.p2 = None
                self.next_frame()

        cv2.destroyWindow(self.win_name)
        return self.out_dict


def demo():
    od = LineSelector(video_path='../resources/demo_video/corsia1.mp4', win_name='corsia1.mp4').run()
    print(od)


if __name__ == '__main__':
    demo()
