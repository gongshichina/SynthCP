"""
Copyright (C) 2019 NVIDIA Corporation.  All rights reserved.
Licensed under the CC BY-NC-SA 4.0 license (https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode).
"""

import os
import os.path as osp
import sys
sys.path.append(osp.dirname(osp.dirname(osp.abspath(__file__))))
from collections import OrderedDict
from options.train_options import TrainOptions
import data
from util.iter_counter import IterationCounter
from util.visualizer import Visualizer
from trainers.pix2pix_trainer import Pix2PixTrainer
from PIL import Image
from util.util import tensor2im
import torch
import pdb

#torch.backends.cudnn.benchmark = False

# parse options
opt = TrainOptions().parse()

# print options to help debugging
print(' '.join(sys.argv))

# load the dataset
dataloader = data.create_dataloader(opt)

# create trainer for our model
trainer = Pix2PixTrainer(opt)
trainer.pix2pix_model.eval()

# create tool for counting iterations
iter_counter = IterationCounter(opt, len(dataloader))

# create tool for visualization
visualizer = Visualizer(opt)
epoch = 0
iter_counter.record_epoch_start(epoch)
for i, data_i in enumerate(dataloader, start=iter_counter.epoch_iter):
    iter_counter.record_one_iteration()

    # Training
    # train generator
    with torch.no_grad():
        if i % opt.D_steps_per_G == 0:
            trainer.run_generator_one_step(data_i, backward=False)

    # Save reconstructed image
    #img_rec_path = os.path.join(opt.eval_output_dir, data_i['path'][0].replace('leftImg8bit', opt.rec_save_suffix))
    img_rec_path = data_i['path'][0].replace('leftImg8bit', opt.rec_save_suffix)
    os.makedirs(os.path.dirname(img_rec_path), exist_ok=True)
    Image.fromarray(tensor2im(trainer.get_latest_generated()[0])).save(img_rec_path)

    #visuals = OrderedDict([('input_label', data_i['label']),
    #                       ('synthesized_image', trainer.get_latest_generated()),
    #                       ('real_image', data_i['image'])])
    #visualizer.display_current_results(visuals, epoch, iter_counter.total_steps_so_far)

#visualizer.dump_record_losses()
print('Evaluating was successfully finished.')
