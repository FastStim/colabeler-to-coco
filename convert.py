# Script for convert single JSON to COCO dataset format
# Format json for end-convert format
# {
#    "info"         : info
#    "images"       : [image],
#    "annotations"  : [annotation],
#    "licenses"     : [license]
# }
#
# info {
#   "year"          : int,
#   "version"       : str,
#   "description"   : str,
#   "contributor"   : str,
#   "url"           : str,
#   "data_created"  : datetime
# }
#
# images {
#   "id"            : int,
#   "width"         : int,
#   "height"        : int,
#   "file_name"     : str,
#   "license"       : int,
#   "flickr_url"    : str,
#   "coco_url"      : str,
#   "data_captured  : datetime
# }
#
# license {
#   "id"            : int,
#   "name"          : str,
#   "url"           : str
# }
#
# Object detection format
# annotation {
#   "id"            : int,
#   "image_id"      : int,
#   "category_id"   : int,
#   "segmentation"  : RLE or [polygon],
#   "area"          : float,
#   "bbox"          : [x, y, width, height]
#   "iscrowd"       : 0 or 1
# }
#
# categories [{
#   "id"            : int,
#   "name"          : str,
#   "supercategory" : str,
# }]

import argparse
from os import listdir
from os.path import isfile, join
import json
import datetime


def save_json(coco_json, output_json, debug):
    with open(output_json, 'w') as outfile:
        json.dump(coco_json, outfile)

    print(' \033[33m[OK]\033[0m save json file')


def add_json_images(input_json, all_count, debug):
    i = 0
    j = 0
    count = 0
    pos = 0
    images = []
    annotations = []

    for js in input_json:
        pos += 1
        if not js['outputs']:
            print('\033[31m [%04d/%04d]\033[0m %s \033[31mwrong\033[0m' % (pos, all_count, js['path'].rsplit('\\', 1)[1]))
            continue

        print('\033[34m [%04d/%04d]\033[0m %s \033[34mcorrect\033[0m' % (pos, all_count, js['path'].rsplit('\\', 1)[1]))

        count += 1
        i += 1

        # Filename may be need change to after
        image = {
            'id': i,
            'width': js['size']['width'],
            'height': js['size']['height'],
            'file_name': js['path'],
            'license': 1,
            # 'flickr_url': '',
            # 'coco_url': '',
            'data_captured': datetime.datetime.now().strftime("%Y-%m-%d")
        }
        images.append(image)

        for out in js['outputs']['object']:
            j += 1

            cat_id = 0
            if out['name'] == 'smoke_forest_white':
                cat_id = 1
            if out['name'] == ' smoke_forest_dark':
                cat_id = 2
            if out['name'] == 'smoke_sky_white':
                cat_id = 3
            if out['name'] == 'smoke_sky_dark':
                cat_id = 4

            box = [out['bndbox']['xmin'] - 1, out['bndbox']['ymin'] - 1,
                   out['bndbox']['xmax'] - out['bndbox']['xmin'] - 1,
                   out['bndbox']['ymax'] - out['bndbox']['ymin'] - 1]

            annotation = {
                'id': j,
                'image_id': i,
                'category_id': cat_id,
                'segmentation': [
                    [box[0], box[1], box[0], (box[1] + box[3]), (box[0] + box[2]), (box[1] + box[3]), (box[0] + box[2]),
                     box[1]]],
                'area': float(box[2] * box[3]),
                'bbox': box,
                'iscrowd': 0
            }
            annotations.append(annotation)
            if debug:
                print(' annotation: %s' % annotation)

        if debug:
            print(' image: %s' % image)

    print('\033[33m count correct images:\033[0m %s' % count)

    return images, annotations


def create_json(debug):
    # First, create COCO dataset using the variables declared here,
    # after created method for change it to an external file
    data = {}
    info = {
        'year': datetime.datetime.now().year,
        'version': '0.02',
        'description': 'Small smoke dataset',
        'contributor': 'FastStim',
        'url': 'faststim.com',
        'data_created': datetime.datetime.now().strftime("%Y-%m-%d")
    }

    lic = {
        'id': 1,
        'name': 'non-free',
        'url': 'faststim.com'
    }

    cat = [{
        'id': 1,
        'name': 'smoke_forest_white',
        'supercategory': 'smoke',
    }, {
        'id': 2,
        'name': 'smoke_forest_dark',
        'supercategory': 'smoke'
    }, {
        'id': 3,
        'name': 'smoke_sky_white',
        'supercategory': 'smoke'
    }, {
        'id': 4,
        'name': 'smoke_sky_dark',
        'supercategory': 'smoke'
    }]

    data['info'] = info
    data['licenses'] = [lic]
    data['categories'] = cat

    if debug:
        print(' data: %s' % data)

    return data


def parse_json(files, debug):
    data = []
    for file in files:
        with open(file) as f:
            data.append(json.load(f))

    if debug:
        print(' data: %s' % data)
        print('\033[35m end function: parse_json\033[0m')

    return data


def main(input_dir, output, debug):
    print('\033[1m\033[35m start program\033[0m')
    if debug:
        print(' input_dir = "%s"' % input_dir)

    coco_json = create_json(debug)

    # Required to add a check that would take only json
    json_files = [input_dir + '/' + f for f in listdir(input_dir) if isfile(join(input_dir, f))]

    all_count = len(json_files)
    print('\033[33m boxx all find files:\033[0m %s' % all_count)

    if debug:
        print(' files %s' % json_files)

    input_json = parse_json(json_files, debug)
    coco_json['images'], coco_json['annotations'] = add_json_images(input_json, all_count, debug)

    save_json(coco_json, output, debug)

    print('\033[1m\033[35m end program\033[0m')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Convert JSON for COCO dataset format')
    parser.add_argument('-d', '--debug', help='Start to debug mode', action="store_true")
    parser.add_argument('--input_dir', required=True, dest='input_dir', type=str, default=None,
                        help='Input directory single json file')
    parser.add_argument('--output', required=True, dest='output', type=str, default=None,
                        help='Output file for save json COCO dataset')
    args = parser.parse_args()

    main(args.input_dir, args.output, args.debug)
