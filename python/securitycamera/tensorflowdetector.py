from utils import label_map_util

from utils import visualization_utils as vis_util
import cv2
import imutils
import numpy as np
import os
import tensorflow as tf
import six.moves.urllib as urllib
import tarfile
import logging

logger = logging.getLogger('security_camera')
class TensorflowDetector(object):


    def downloadModel(self, MODEL_NAME):
        MODEL_FILE = MODEL_NAME + '.tar.gz'
        DOWNLOAD_BASE = 'http://download.tensorflow.org/models/object_detection/'
        logger.info("Preparing to download tensorflow model {}".format(MODEL_FILE))
        logger.info("Is file downloaded? %s " % os.path.isfile(MODEL_FILE))
        if not os.path.isfile(MODEL_FILE):
            opener = urllib.request.URLopener()
            opener.retrieve(DOWNLOAD_BASE + MODEL_FILE, MODEL_FILE)
        tar_file = tarfile.open(MODEL_FILE)
        for file in tar_file.getmembers():
            file_name = os.path.basename(file.name)
            if 'frozen_inference_graph.pb' in file_name:
                tar_file.extract(file, os.getcwd())

    def __init__(self):
        # What model to download.
        # MODEL_NAME = 'ssd_mobilenet_v1_coco_2017_11_17'
        # http://download.tensorflow.org/models/object_detection/ssdlite_mobilenet_v2_coco_2018_05_09.tar.gz
        # MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'
        MODEL_NAME = 'ssdlite_mobilenet_v2_coco_2018_05_09'
        #MODEL_NAME = 'ssd_inception_v2_coco_2018_01_28'
        # http://download.tensorflow.org/models/object_detection/ssd_inception_v2_coco_2018_01_28.tar.gzMODE
        # MODEL_NAME = 'ssd_mobilenet_v2_coco_2018_03_29'


        self.downloadModel(MODEL_NAME)

        # Path to frozen detection graph. This is the actual model that is used for the object detection.
        PATH_TO_CKPT = MODEL_NAME + '/frozen_inference_graph.pb'

        # List of the strings that is used to add correct label for each box.
        PATH_TO_LABELS = os.path.join(os.environ['OBJECT_DETECTION_API_PATH'],'data', 'mscoco_label_map.pbtxt')

        NUM_CLASSES = 90

        label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
        categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES,
                                                                    use_display_name=True)
        self.category_index = label_map_util.create_category_index(categories)

        # Load the Tensorflow model into memory.
        detection_graph = tf.Graph()
        with detection_graph.as_default():
            od_graph_def = tf.GraphDef()
            with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
                serialized_graph = fid.read()
                od_graph_def.ParseFromString(serialized_graph)
                tf.import_graph_def(od_graph_def, name='')

            self.sess = tf.Session(graph=detection_graph)

        # Define input and output tensors (i.e. data) for the object detection classifier

        # Input tensor is the image
        self.image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')

        # Output tensors are the detection boxes, scores, and classes
        # Each box represents a part of the image where a particular object was detected
        self.detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')

        # Each score represents level of confidence for each of the objects.
        # The score is shown on the result image, together with the class label.
        self.detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
        self.detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')

        # Number of objects detected
        self.num_detections = detection_graph.get_tensor_by_name('num_detections:0')

        self.detection_graph = detection_graph

    def detectPerson(self, frame):
        (im_height,im_width) = frame.shape[:2]
        #image_np = self.load_image_into_numpy_array(frame)
        # switch to rgb
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image_np_expanded = np.expand_dims(rgb, axis=0)
        output_dict = self.run_inference_for_single_image(image_np_expanded, self.detection_graph)
        result = False
        classes = output_dict['detection_classes']

        boundingBoxes = []
        for i in range(len(classes)):
            score = output_dict['detection_scores'][i]

            label = self.category_index.get(classes[i])
            if (score >= 0.5 and label['name'] == 'person'):
                result = True
                logger.info("Detected person")
                detection_boxes = output_dict['detection_boxes']
                boxes_shape = detection_boxes.shape
                logger.debug('detection boxes shape {}'.format(boxes_shape))
                for detection_box in detection_boxes:

                    ymin = detection_box[0] * im_height
                    xmin = detection_box[1] * im_width
                    ymax = detection_box[2] * im_height
                    xmax = detection_box[3] * im_width
                    if ymin == 0 and xmin == 0 and ymax== 0 and xmax ==0:
                        continue
                    bbox = (int(xmin), int(ymin), int(xmax), int(ymax))
                    boundingBoxes.append(bbox)


                #self.drawBoundingBoxes(frame, output_dict)
                break

        return (result,frame, boundingBoxes)

    def drawBoundingBoxes(self, frame, output_dict):
        logger.debug("detected person")
        logger.debug(output_dict['detection_boxes'][0])
        frame.setflags(write=1)
        vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            output_dict['detection_boxes'],
            output_dict['detection_classes'],
            output_dict['detection_scores'],
            self.category_index,
            use_normalized_coordinates=True,
            line_thickness=8,
            min_score_thresh=0.40)

    def load_image_into_numpy_array(self, image):
        (im_height, im_width) = image.shape[:2]
        return np.array(image.data).reshape(
            (im_height, im_width, 3)).astype(np.uint8)

    def run_inference_for_single_image(self, frame_expanded, graph):
        # Perform the actual detection by running the model with the image as input
        (boxes, scores, classes, num) = self.sess.run(
            [self.detection_boxes, self.detection_scores, self.detection_classes, self.num_detections],
            feed_dict={self.image_tensor: frame_expanded})
        output_dict = {
            "detection_classes": np.squeeze(classes).astype(np.int32),
            "detection_boxes": boxes[0],
            "detection_scores": np.squeeze(scores)
        }
        return output_dict
