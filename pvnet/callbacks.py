r"""
Early Stopping
^^^^^^^^^^^^^^
Monitor a metric and _____ when it stops improving.
"""
import logging
from typing import Any, Callable, Dict, Optional, Tuple
from lightning.pytorch.trainer.states import TrainerFn
from lightning.pytorch.callbacks import EarlyStopping, BaseFinetuning

class PhaseEarlyStopping(EarlyStopping):
    
    training_phase = None
                         
    def switch_phase(self, phase: str):
        if phase==self.training_phase:
            self.activate()
        else:
            self.deactivate()
    
    def deactivate(self):
        self.active = False
        
    def activate(self):
        self.active = True
    
    def _should_skip_check(self, trainer: "pl.Trainer") -> bool:

        return (
            (trainer.state.fn != TrainerFn.FITTING) 
            or (trainer.sanity_checking)
            or not self.active
        )
    
class PretrainEarlyStopping(EarlyStopping):
    training_phase = "pretrain"
    
class MainEarlyStopping(EarlyStopping):
    training_phase = "main"


class PretrainFreeze(BaseFinetuning):
    
    training_phase = "pretrain"
    
    def __init__(self):
        super().__init__()

    def freeze_before_training(self, pl_module):
        # freeze any module you want
        modules = []
        if pl_module.include_sat:
             modules += [pl_module.sat_encoder]
        if pl_module.include_nwp:
            modules += [pl_module.nwp_encoder]
        self.freeze(modules)

    def finetune_function(self, pl_module, current_epoch, optimizer):            
        if not self.active:
            modules = []
            if pl_module.include_sat:
                 modules += [pl_module.sat_encoder]
            if pl_module.include_nwp:
                modules += [pl_module.nwp_encoder]
            self.unfreeze_and_add_param_group(
                 modules=modules,
                 optimizer=optimizer,
                 train_bn=True,
            )
    
    def switch_phase(self, phase: str):
        if phase==self.training_phase:
            self.activate()
        else:
            self.deactivate()
    
    def deactivate(self):
        self.active = False
        
    def activate(self):
        self.active = True
