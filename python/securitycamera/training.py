import tensorflow as tf

import os
from object_detection.utils import dataset_util

flags = tf.app.flags
flags.DEFINE_string('output_path', '', 'Path to output TFRecord')
FLAGS = flags.FLAGS

LABEL_DICT = {
    "Person": 1
}

class Training(object):
    def __init__(self, trainingDir):
       self.start(trainingDir)

    def create_tf_example(self, example):

        return False
        # (imageBlob, jsonBlob) = example
        # imageFilepath = "/tmp/" + imageBlob.name
        # jsonFilepath = "/tmp/" + imageBlob.name
        # imageBlob.download_to_filename(imageFilepath)
        # jsonBlob.downolad_to_filename(imageFilepath)
        #
        # # Bosch
        # height = 720  # Image height
        # width = 1280  # Image width
        #
        # filename = example['path']  # Filename of the image. Empty if image is not from file
        # filename = filename.encode()
        #
        # with tf.gfile.GFile(example['path'], 'rb') as fid:
        #     encoded_image = fid.read()
        #
        # image_format = 'png'.encode()
        #
        # xmins = []  # List of normalized left x coordinates in bounding box (1 per box)
        # xmaxs = []  # List of normalized right x coordinates in bounding box
        # # (1 per box)
        # ymins = []  # List of normalized top y coordinates in bounding box (1 per box)
        # ymaxs = []  # List of normalized bottom y coordinates in bounding box
        # # (1 per box)
        # classes_text = []  # List of string class name of bounding box (1 per box)
        # classes = []  # List of integer class id of bounding box (1 per box)
        #
        # for box in example['boxes']:
        #     # if box['occluded'] is False:
        #     # print("adding box")
        #     xmins.append(float(box['x_min'] / width))
        #     xmaxs.append(float(box['x_max'] / width))
        #     ymins.append(float(box['y_min'] / height))
        #     ymaxs.append(float(box['y_max'] / height))
        #     classes_text.append(box['label'].encode())
        #     classes.append(int(LABEL_DICT[box['label']]))
        #
        # tf_example = tf.train.Example(features=tf.train.Features(feature={
        #     'image/height': dataset_util.int64_feature(height),
        #     'image/width': dataset_util.int64_feature(width),
        #     'image/filename': dataset_util.bytes_feature(filename),
        #     'image/source_id': dataset_util.bytes_feature(filename),
        #     'image/encoded': dataset_util.bytes_feature(encoded_image),
        #     'image/format': dataset_util.bytes_feature(image_format),
        #     'image/object/bbox/xmin': dataset_util.float_list_feature(xmins),
        #     'image/object/bbox/xmax': dataset_util.float_list_feature(xmaxs),
        #     'image/object/bbox/ymin': dataset_util.float_list_feature(ymins),
        #     'image/object/bbox/ymax': dataset_util.float_list_feature(ymaxs),
        #     'image/object/class/text': dataset_util.bytes_list_feature(classes_text),
        #     'image/object/class/label': dataset_util.int64_list_feature(classes),
        # }))
        #
        # return tf_example


    def start(self, destDir):
        writer = tf.python_io.TFRecordWriter(FLAGS.output_path)
        # load images from google cloud bucket
        # and iterate through each image
        #images = firebase.getImagesForTraining()
        files = os.listdir(destDir)
        for file in files:
            print(file)



#     # examples = examples[:10]  # for testing
#     len_images = len(images)
#     print("Loaded ", len_images, "images")
#
#     for i in range(len_images):
#         examples[i]['path'] = os.path.abspath(os.path.join(os.path.dirname(INPUT_YAML), examples[i]['path']))
#
#     counter = 0
#     for (imageBlob, jsonBlob) in images:
#         tf_example = create_tf_example((imageBlob, jsonBlob))
#         writer.write(tf_example.SerializeToString())
#
#         if counter % 10 == 0:
#             print("Percent done", (counter / len_images) * 100)
#         counter += 1
#
#     writer.close()
#
#
# if __name__ == '__main__':
#     tf.app.run()