from .sky_model_object import Sky_Model


class PlaneSky(Sky_Model):

    name = "plane sky"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
