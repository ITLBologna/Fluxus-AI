from path import Path
from back_end.yolox.exps.default import yolox_m, yolox_l, yolox_s, yolox_x, yolov3

def get_exp_by_file(exp_file):
    exp_file = Path(exp_file).name.split('.')[0]

    exp = None

    if exp_file == "yolox_m":
        exp = yolox_m.Exp()
    elif exp_file == "yolox_l":
        exp = yolox_l.Exp()
    elif exp_file == "yolox_s":
        exp = yolox_s.Exp()
    elif exp_file == "yolox_x":
        exp = yolox_x.Exp()
    elif exp_file == "yolov3":
        exp = yolov3.Exp()

    assert exp is not None, "exp in None, check path"

    return  exp


