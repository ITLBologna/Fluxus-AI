import pickle
from datetime import datetime

import cv2
import numpy as np
import torch.cuda
from path import Path

from back_end.sort.sort import Sort
from back_end.yolox.detect import YoloX
from conf import cnf
from utils import Polygon, in_hull
from urllib.request import urlretrieve

class LineCrossing:
    """
    Line Crossing Service
    """
    def __init__(self, line):
        """
        :param line: 2x2 numpy array or list
        """
        self.line = np.asarray(line)
        if line[0][0] > line[1][0]:
            self.line = np.asarray([line[1], line[0]])
        assert self.line.shape == (2,2), "line shape not (2,2)"

        self.waiting_tracks = {}

    def update(self, point, track_id):
        """
        :param point: (x,y) point coord
        :param track_id: track number identifier
        :return: False if point is above the line else True
        """

        v1 = self.line[1] - self.line[0]
        v2 = self.line[1] - point
        xp = v1[0] * v2[1] - v1[1] * v2[0]  # Cross product

        above = xp > 0

        if above:
            self.waiting_tracks[track_id] = track_id
            return False
        elif not above and track_id in self.waiting_tracks:
            self.waiting_tracks.pop(track_id)
            return True

def bb_iou(boxA, boxB):
    # determine the (x, y)-coordinates of the intersection rectangle
    xA = max(boxA[0], boxB[0])
    yA = max(boxA[1], boxB[1])
    xB = min(boxA[2], boxB[2])
    yB = min(boxA[3], boxB[3])
    # compute the area of intersection rectangle
    interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
    # compute the area of both the prediction and ground-truth
    # rectangles
    boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
    boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)
    # compute the intersection over union by taking the intersection
    # area and dividing it by the sum of prediction + ground-truth
    # areas - the interesection area
    iou = interArea / float(boxAArea + boxBArea - interArea)
    # return the intersection over union value
    return iou



def refine_labels(content):
    data = np.array(content, dtype=object)
    cars_area = [a[-1] for a in content if a[2] == "car"]
    t_b_area = [a[-1] for a in content if a[2] in ["truck", "bus", "train", "boat", "airplane"]]

    if len(cars_area) > 0 and len(t_b_area) > 0:
        k = 3
        mask = np.where(
            (data == "truck") | (data == "bus") | (data == "car") | (data == "train") | (data == "boat") | (
                        data == "airplane")
        )[0]
        data_to_cluster = np.take(data, mask, axis=0)

        # define criteria, number of clusters(K) and apply kmeans()
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 1000, 1.0)

        ret, label, center = cv2.kmeans(data_to_cluster[:, -1].reshape(-1, 1).astype(np.float32), k, None, criteria, 10,
                                        cv2.KMEANS_RANDOM_CENTERS)

        map_label_cluster = dict(zip(sorted(range(len(center)), key=lambda k: center[k]), cnf.cluster_label.values()))

        for i, l in enumerate(label):
            idx = mask[i]
            data[idx][2] = map_label_cluster[l[0]]

    elif len(cars_area) > 0 and not len(t_b_area) > 0:
        # k = 2
        mask = np.where(data == "car")[0]
        # data_to_cluster = np.take(data, mask, axis=0)

        for i in mask:
            data[i][2] = cnf.cluster_label[0]

        median = np.median(cars_area)

        for i in range(len(data)):
            if data[i][-1] >= 1.2 * median:
                data[i][2] = cnf.cluster_label[1]

    # for i in range(len(data)):
    #     data[i][2] = cnf.class_trans[data[i][2]]

    return data


class StreamAnalyzer:

    def __init__(self, video_file, calib_dict):
        # type: (str, dict) -> list
        """
        :param video_file: video file path
        :param calib_dict:
            line: ndarray of 2 points defining a line -> 2x2 ndarray
            poly: ndarray of 3 or more points defining a polygon -> Nx2 ndarray eg 3x2
            frame_width: int
            frame_height: int
        :return: list of rows compliant with the csv file
        """
        self.calib_dict = calib_dict
        self.line = np.asarray([self.calib_dict['p1'], self.calib_dict['p2']])
        self.poly = Polygon(self.calib_dict['polygon'])
        self.video_file = video_file
        self.frame_height = self.calib_dict['frame_height']
        self.frame_width = self.calib_dict['frame_width']

        self.colors = [tuple(np.random.random(size=3) * 256) for i in range(65536)]

        self.w_path = Path(__file__).parent / 'yolox' / 'yolox_m.pth'
        if not self.w_path.exists():
            print("try download yolox weights")
            url = "https://github.com/Megvii-BaseDetection/YOLOX/releases/download/0.1.1rc0/yolox_m.pth"
            try:
                urlretrieve(url, filename=self.w_path)
            except:
                "no internet connection, needed to download weights"
        device = "cuda:0" if torch.cuda.is_available() else "cpu"

        self.detector = None
        self.detections = None
        self.tracker = None
        self.tracks = None

        self.data_file = Path(self.video_file.replace(".mp4", ".dat"))
        if self.data_file.isfile() and self.data_file.exists():
            with open(self.data_file, 'rb') as f:
                self.detections = pickle.load(f)
        else:
            self.detector = YoloX(device=device, weightsPath=self.w_path, num_classes=len(cnf.coco_classes),
                                  get_top2=False)

        self.track_file = Path(self.video_file.replace(".mp4", ".trk"))
        if self.track_file.isfile() and self.track_file.exists():
            with open(self.track_file, 'rb') as f:
                self.tracks = pickle.load(f)
        else:
            self.tracker = Sort(max_age=1, min_hits=3)
            self.lc = LineCrossing(self.line)
        self.fps = 0

    def run(self, debug=False):

        if self.detections is None:
            self.detections = []
            print("running detector")

            cap = cv2.VideoCapture(self.video_file)
            self.fps = cap.get(cv2.CAP_PROP_FPS)

            ret, frame = cap.read()
            assert ret is True, "Cap not opened"

            tot_frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)

            cv2.imwrite(self.video_file.replace(".mp4", ".png"), frame)

            while ret:
                frame_copy = frame.copy()

                timestamp = datetime.utcfromtimestamp(cap.get(cv2.CAP_PROP_POS_MSEC) / 1000).strftime(
                    '%H:%M:%S')
                framestamp = int(cap.get(cv2.CAP_PROP_POS_FRAMES))

                detections = self.detector.predict(frame)

                self.detections.append([timestamp, framestamp, detections])

                if debug:
                    cv2.line(frame_copy, tuple(self.line[0]), tuple(self.line[1]), [0, 255, 0], 1)
                    pts = np.array(self.poly.points).reshape((-1, 1, 2))
                    cv2.polylines(frame_copy, [pts], True, (0, 0, 255))

                    for det in detections:
                        cv2.rectangle(frame_copy, (int(det[0]), int(det[1])), (int(det[2]), int(det[3])), [0, 0, 255],
                                      1)

                    cv2.imshow("detector", frame_copy)
                    k = cv2.waitKey(1)
                    if k == 27 or k == ord('q'):
                        cv2.destroyAllWindows()
                        break

                progress = framestamp / tot_frames
                yield progress

                ret, frame = cap.read()

            cap.release()

            with open(self.data_file, "wb") as f:
                pickle.dump(self.detections, f)

        if self.tracks is None:
            print("generating tracks")
            upper_tracks = {}
            self.tracks = {}

            cap = cv2.VideoCapture(self.video_file)
            self.fps = cap.get(cv2.CAP_PROP_FPS)

            tot_detections = len(self.detections)

            for eli, elem in enumerate(self.detections):
                timestamp, framestamp, dets = elem

                # filter out persons in vehicles
                if dets.shape[0] > 1:
                    dets_dict = {di: dv for di, dv in enumerate(dets)}
                    persons = {di: dv for di, dv in enumerate(dets) if dv[5] == 0}
                    to_remove = []
                    for di, dv in dets_dict.items():
                        if dv[5] != 0:  # if not person
                            for pi, pv in persons.items():
                                if (dv[0] <= pv[0] and dv[1] <= pv[1] and dv[2] >= pv[2] and dv[3] >= pv[3]) or (
                                        (pv[3] - pv[1]) / (pv[2] - pv[0])) < 1.5 or bb_iou(dv[:4], pv[:4]) > 0.5:
                                    to_remove.append(pi)

                    for ti in list(set(to_remove)):
                        dets_dict.pop(ti)

                    dets = list(dets_dict.values())

                if debug:
                    ret, frame = cap.read()
                    frame_copy = frame.copy()
                    fstamp = int(cap.get(cv2.CAP_PROP_POS_FRAMES))
                    assert int(fstamp) == int(framestamp), "synch error"

                outputs = self.tracker.update(np.copy(dets))
                outputs = np.asarray(outputs, dtype=np.float32)
                outputs_copy = np.empty_like(outputs, dtype=object)
                outputs_copy[:] = outputs[:].astype(np.int32)
                outputs_copy[:, 6] = outputs[:, 6]
                outputs_copy[:, 8] = outputs[:, 8]
                outputs_copy[:, 9] = outputs[:, 9]
                outputs = outputs_copy

                for box in outputs:
                    track_id = box[4]

                    bottom_center_point = np.asarray(((box[0] + box[2]) // 2, box[3]))

                    if not in_hull(bottom_center_point, self.poly):
                        continue

                    # above = isabove(self.line, bottom_center_point)     # check if object cross the line
                    # if above:
                    #     upper_tracks[track_id] = track_id
                    # elif not above and track_id in upper_tracks and track_id not in self.tracks:
                    if self.lc.update(bottom_center_point, track_id) and track_id:
                        x_min, y_min, x_max, y_max = box[0], box[1], box[2], box[3]
                        x_min, y_min = max(0, x_min), max(0, y_min)
                        x_max, y_max = min(self.frame_width, x_max), min(self.frame_width, y_max)
                        area = abs((x_max - x_min)) * abs((y_max - y_min))
                        vehicle_class_1, conf_1 = cnf.coco_classes[box[5]] if box[5] in cnf.coco_classes else "", box[6]
                        # vehicle_class_2, conf_2 = cnf.coco_classes[box[7]] if box[7] in cnf.coco_classes else "", box[8]
                        movement = box[9]
                        speed = round(movement * self.fps, 2)

                        self.tracks[track_id] = [timestamp, framestamp, vehicle_class_1, speed, x_min, y_min,
                                                 x_max, y_max, area]

                    if debug:
                        color = list(self.colors[track_id])
                        color[2] = 0
                        if track_id in self.tracks:
                            color[2] = 255

                    if debug:
                        cv2.rectangle(frame_copy, (box[0], box[1]), (box[2], box[3]), color)
                        cv2.putText(frame_copy, f"{track_id}", bottom_center_point, cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                                    [128, 0, 255])

                if debug:
                    cv2.line(frame_copy, tuple(self.line[0]), tuple(self.line[1]), [0, 255, 0], 1)
                    pts = np.array(self.poly.points).reshape((-1, 1, 2))
                    cv2.polylines(frame_copy, [pts], True, (0, 0, 255))
                    cv2.imshow("tracker", frame_copy)
                    k = cv2.waitKey(1)
                    if k == 27 or k == ord('q'):
                        cv2.destroyAllWindows()
                        break

                progress = eli / tot_detections
                yield progress

            with open(self.track_file, "wb") as f:
                pickle.dump(self.tracks, f)

        self.csv_info = refine_labels(list(self.tracks.values()))

        return self.csv_info
