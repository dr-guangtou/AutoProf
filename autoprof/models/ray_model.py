from .galaxy_model_object import Galaxy_Model
from autoprof.utils.interpolate import cubic_spline_torch
import numpy as np
import torch
from autoprof.utils.conversions.coordinates import Axis_Ratio_Cartesian

class Ray_Galaxy(Galaxy_Model):

    model_type = " ".join(("ray", Galaxy_Model.model_type))
    parameter_specs = {
        "q(R)": {"units": "b/a", "limits": (0,1), "uncertainty": 0.04},
        "PA(R)": {"units": "rad", "limits": (0,np.pi), "cyclic": True, "uncertainty": 0.08},
    }

    def __init__(self, *args, **kwargs):
        if not hasattr(self, "profR"):
            self.profR = None
        super().__init__(*args, **kwargs)
        self.rays = int(kwargs.get("rays", 1))

    def _init_convert_input_units(self):
        super()._init_convert_input_units()
        
        if self["PA(R)"].value is not None:
            self["PA(R)"].set_value(self["PA(R)"].value * np.pi / 180, override_locked = True)

    def initialize(self):
        super().initialize()
        if not (self["PA(R)"].value is None or self["q(R)"].value is None):
            return

        if self["PA(R)"].value is None:
            self["PA(R)"].set_value(np.ones(len(self.profR))*self["PA"].value.detach().item(), override_locked = True)
            
        if self["q(R)"].value is None:
            self["q(R)"].set_value(np.ones(len(self.profR))*0.9, override_locked = True)
            
    def set_fit_window(self, window):
        super().set_fit_window(window)

        if self.profR is None:
            self.profR = [0,1]
            while self.profR[-1] < np.sqrt(np.sum((self.fit_window.shape/2)**2)):
                self.profR.append(self.profR[-1] + max(1,self.profR[-1]*0.2))
            self.profR.pop()
            self.profR = torch.tensor(self.profR)

    def brightness_model(self, R, T, image):
        # fixme
            
    def evaluate_model(self, image):
        X, Y = image.get_coordinate_meshgrid_torch(self["center"].value[0], self["center"].value[1])
        XX, YY = self.transform_coordinates(X, Y)
        
        return self.brightness_model(self.radius_metric(XX, YY), torch.atan2(YY, XX), image)