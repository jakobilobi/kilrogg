import os
from skimage import io, transform
import torch
import torchvision
from torch.autograd import Variable
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms #, utils
# import torch.optim as optim

import numpy as np
from PIL import Image
import glob

import sys
sys.path.append(".") # Required to resolve "attempted relative import beyond top-level package"

from model import RescaleT
from model.data_loader import ToTensor
from model.data_loader import ToTensorLab
from model.data_loader import SalObjDataset

from model import U2NET # full size version 173.6 MB
from model import U2NETP # small version u2net 4.7 MB

def get_path_as_list(path):
    if (os.path.isdir(path)):
        return glob.glob(path + os.sep + '*')
    if (os.path.isfile(path)):
        return [path]

def resolve_input(path):
    file_list = []
    if (isinstance(path, list)):
        for item in path:
            file_list += get_path_as_list(item)
    else:
        file_list += get_path_as_list(path)
    return file_list

class ModelInterface:
    def __init__(self, placeholder=0):
        self.placeholder = placeholder
        self.infered_np_arrays = []
        self.saved_files = []

    def run_inference(self, input_path):
        # --------- 1. get image path and name ---------
        model_name='u2net'#u2netp

        img_name_list = resolve_input(input_path)

        prediction_dir = os.path.join(os.getcwd(), 'test_data', model_name + '_results' + os.sep)
        model_dir = os.path.join(os.getcwd(), 'saved_models', model_name, model_name + '.pth')

        # --------- 2. dataloader ---------
        #1. dataloader
        test_salobj_dataset = SalObjDataset(img_name_list = img_name_list,
                                            lbl_name_list = [],
                                            transform=transforms.Compose([RescaleT(320),
                                                                        ToTensorLab(flag=0)])
                                            )
        test_salobj_dataloader = DataLoader(test_salobj_dataset,
                                            batch_size=1,
                                            shuffle=False,
                                            num_workers=1)

        # --------- 3. model define ---------
        if(model_name=='u2net'):
            print("...load U2NET---173.6 MB")
            net = U2NET(3,1)
        elif(model_name=='u2netp'):
            print("...load U2NEP---4.7 MB")
            net = U2NETP(3,1)
        net.load_state_dict(torch.load(model_dir, map_location=torch.device('cpu')))
        if torch.cuda.is_available():
            net.cuda()
        net.eval()

        # --------- 4. inference for each image ---------
        saved_file_paths = []
        for i_test, data_test in enumerate(test_salobj_dataloader):
            print("inferencing:",img_name_list[i_test].split(os.sep)[-1])

            inputs_test = data_test['image']
            inputs_test = inputs_test.type(torch.FloatTensor)

            if torch.cuda.is_available():
                inputs_test = Variable(inputs_test.cuda())
            else:
                inputs_test = Variable(inputs_test)

            d1,d2,d3,d4,d5,d6,d7= net(inputs_test)

            # normalization
            pred = d1[:,0,:,:]
            pred = self.normPRED(pred)

            # save results to test_results folder
            if not os.path.exists(prediction_dir):
                os.makedirs(prediction_dir, exist_ok=True)

            predict = pred
            predict = predict.squeeze()
            predict_np = predict.cpu().data.numpy()
            self.infered_np_arrays.append(predict_np)

            filename = self.save_output(img_name_list[i_test], predict_np, prediction_dir)

            del d1,d2,d3,d4,d5,d6,d7
            saved_file_paths = saved_file_paths + [filename]

        self.saved_files = saved_file_paths

    def save_output(self, image_name, predict_np, d_dir):
        im = Image.fromarray(predict_np*255).convert('RGB')
        img_name = image_name.split(os.sep)[-1]
        image = io.imread(image_name)
        imo = im.resize((image.shape[1],image.shape[0]),resample=Image.BILINEAR)

        pb_np = np.array(imo)

        aaa = img_name.split(".")
        bbb = aaa[0:-1]
        imidx = bbb[0]
        for i in range(1,len(bbb)):
            imidx = imidx + "." + bbb[i]

        filename = d_dir + imidx + '.png'
        imo.save(filename)
        return filename

    def get_saved_files_realpath(self):
        return self.saved_files

    def get_saved_files_name(self):
        filenames = []
        for f in self.saved_files:
            filenames += [os.path.basename(f)]
        return filenames

    def get_infered_np_arrays(self):
        return self.infered_np_arrays

    # normalize the predicted SOD probability map
    def normPRED(self, d):
        ma = torch.max(d)
        mi = torch.min(d)

        dn = (d-mi)/(ma-mi)

        return dn
