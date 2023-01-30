from typing import Optional

import yaml
from path import Path


class Conf(object):

    def __init__(self, yaml_path=None):
        # type: (Optional[str]) -> None
        """
        :param yaml_path: path of the yaml file containing configuration
            parameters; if `None`, the default yaml file will be used.
            >> default yaml file: <project_dir>/conf/conf.yaml
        """

        if yaml_path is None:
            yaml_path = Path(__file__).parent / 'conf.yaml'

        with open(yaml_path, 'r') as yaml_file:
            self.__dict = yaml.load(yaml_file, Loader=yaml.FullLoader)

        # self.lanes = sorted(self.__dict['lanes'])
        self.v_classes = sorted(self.__dict['v_classes'])
        self.coco_classes = self.__dict['coco_classes']
        self.coco_classes_inv = {v: k for k, v in self.coco_classes.items()}
        self.cluster_label = self.__dict['cluster_label']
        # self.class_trans = self.__dict['class_translation']

        # mapping between vheicle class string and it's int ID
        self.__vclass2int = {}
        for i, key in enumerate(self.__dict['v_classes']):
            self.__vclass2int[key] = i

        # mapping between lane string and it's int ID
        # self.__lane2int = {}
        # for i, key in enumerate(self.__dict['lanes']):
        #     self.__lane2int[key] = i

        self.project_root = Path(__file__).parent.parent  # type: Path
        self.res_path = self.project_root / 'resources'  # type: Path

        # self.videopath = {}
        # for key, value in self.__dict['video_paths'].items():
        #     self.videopath[key] = Path(value)

        # self.csv_out_path = Path(self.__dict['csv_out_path'])

    def vclass2int(self, vclass_str):
        # type: (str) -> int
        """
        :param vclass_str: vehicle class name (string)
        :return: vehicle class index (int)
        """
        return self.__vclass2int[vclass_str]


    # def lane2int(self, lane_str):
    #     type: # (str) -> int
        # """
        # :param lane_str: lane name (string)
        # :return: lane index (int)
        # """
        # return self.__lane2int[lane_str]


cnf = Conf()
