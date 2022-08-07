from flow import Process
from autoprof.utils.visuals import autocmap
from astropy.visualization import SqrtStretch, LogStretch, HistEqStretch
from astropy.visualization.mpl_normalize import ImageNormalize
from autoprof.models import Galaxy_Model
import matplotlib.pyplot as plt
import os
import numpy as np

class Plot_Model(Process):
    """
    Plots the current model image.
    """

    def action(self, state):
        autocmap.set_under("k", alpha=0)
        plt.figure(figsize = (7, 7*state.data.model_image.shape[1]/state.data.model_image.shape[0]), facecolor = 'k')
        plt.contourf(np.log10(state.data.model_image.data), levels = 20, cmap = "Greens_r")
        plt.gca().set_facecolor("k")
        # plt.imshow(
        #     state.data.model_image.data,
        #     origin="lower",
        #     cmap=autocmap,
        #     norm=ImageNormalize(stretch=LogStretch(), clip=False),
        # )
        plt.axis("off")
        plt.margins(0,0)
        plt.tight_layout()
        plt.savefig(
            os.path.join(
                state.options.plot_path,
                f"{self.name}_{state.options.name}_{state.models.iteration:04d}.pdf",
            ),
            # dpi=state.options["ap_plotdpi", 600],
            bbox_inches = 'tight',
            pad_inches = 0
        )
        plt.close()

        residual = (state.data.target - state.data.model_image).data
        plt.figure(figsize = (7, 7*state.data.model_image.shape[1]/state.data.model_image.shape[0]))
        plt.imshow(
            residual,
            origin="lower",
            norm=ImageNormalize(stretch=HistEqStretch(residual), clip = False),
        )
        plt.axis("off")
        plt.margins(0,0)
        plt.tight_layout()
        plt.savefig(
            os.path.join(
                state.options.plot_path,
                f"{self.name}_Residual_{state.options.name}_{state.models.iteration:04d}.jpg",
            ),
            dpi=state.options["ap_plotdpi", 300],
            bbox_inches = 'tight',
            pad_inches = 0
        )
        plt.close()

        
        return state


class Plot_Loss_History(Process):
    """
    Plot the loss history for all the models to identify outliers.
    """

    def action(self, state):

        for model in state.models:
            if len(model.history) == 0:
                continue
            plt.plot(list(reversed(range(len(model.history.loss_history)))), np.log10(np.array(model.history.loss_history) / model.history.loss_history[-1]), label = f"{model.name}")
        plt.legend()
        plt.ylim([None, min(0.5, plt.gca().get_ylim()[1])])
        plt.savefig(
            os.path.join(
                state.options.plot_path,
                f"{self.name}_{state.options.name}.jpg",
            ),
            dpi=state.options["ap_plotdpi", 300],
        )
        plt.close()
        
        return state

class Plot_Galaxy_Profiles(Process):

    def action(self, state):
        for model in state.models:
            if not isinstance(model, Galaxy_Model):
                continue
            R = np.linspace(0, max(model._base_window.shape)/2, 1000)
            I = model.radial_model(R)
            plt.plot(R, np.log10(I))
            plt.xlabel("Semi-major axis [arcsec]")
            plt.ylabel("log$_{10}$(flux/arcsec$^2$)")
            plt.savefig(
                os.path.join(
                    state.options.plot_path,
                    f"{self.name}_{state.options.name}_{model.name}.jpg",
                ),
                dpi=state.options["ap_plotdpi", 300],
            )
            plt.close()
