import numpy as np
import torch
from path import Path

from back_end.yolox.lib.data.data_augment import preproc
from back_end.yolox.lib.exp.build import get_exp_by_file
from back_end.yolox.lib.utils.boxes import postprocess


class YoloX:

    def __init__(self, device, weightsPath, conf=0.3, iou_thresh=0.45, tsize=640, num_classes=80, get_top2=True):
        self.device = device

        yolo_name = Path(weightsPath).name.replace("pth", "py")
        self.exp = get_exp_by_file(yolo_name)
        self.exp.test_size = (tsize, tsize)
        self.exp.nmsthre = iou_thresh
        self.exp.test_conf = conf
        self.num_classes = num_classes
        self.model = self.exp.get_model()
        self.model.to(device)

        ckpt = torch.load(weightsPath, map_location=device)
        self.model.load_state_dict(ckpt["model"])

        self.model.eval()

        self.get_top2 = get_top2


    def decode(self, output, img_info, cls_conf=0.35):
        if output[0] is None:
            return np.empty(shape=(0, 8))

        output = output[0].cpu().numpy()
        ratio = img_info["ratio"]

        # # preprocessing: resize
        # bboxes = np.asarray(output[:, 0:4] / ratio).astype(np.int32)
        #
        # cls = output[:, 6]
        # scores = output[:, 4] * output[:, 5]

        # return bboxes, cls, scores

        if output.shape[1] == 7:
            output[:, 0:4] = output[:, 0:4] / ratio
            output[:, 4] = output[:, 4] * output[:, 5]
            output[:, 5] = output[:, 6]
            output[:, 6] = 0
            output = np.concatenate([output, np.zeros(shape=(len(output), 1), dtype=np.float32)], axis=1)

        elif output.shape[1] == 9:
            output[:, 0:4] = output[:, 0:4] / ratio
            output[:, 4] = output[:, 4] * output[:, 5]
            output[:, 5] = output[:, 4] * output[:, 6]
            output[:, 6] = output[:, 7]
            output[:, 7] = output[:, 8]
            output[:, 8] = 0
            output[:, [6, 5]] = output[:, [5, 6]]

        return output[:, :8]


    def predict(self, im0):
        with torch.no_grad():
            img_info = {}
            height, width = im0.shape[:2]
            img_info["height"] = height
            img_info["width"] = width

            img, ratio = preproc(im0, self.exp.test_size)
            img_info["ratio"] = ratio

            img = torch.from_numpy(img).to(self.device).float().unsqueeze(0)

            pred = self.model(img)
            bboxes = postprocess(pred, num_classes=self.num_classes, conf_thre=self.exp.test_conf,
                                 nms_thre=self.exp.nmsthre, class_agnostic=True, get_top2=self.get_top2)
            # bboxes, cls, score = self.decode(bboxes, img_info)

            # return bboxes, cls, score

            return self.decode(bboxes, img_info)
