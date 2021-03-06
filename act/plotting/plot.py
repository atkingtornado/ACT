"""
act.plotting.TimeSeriesDisplay
==============================

Class for creating timeseries plots from ACT datasets.

.. autosummary::
    :toctree: generated/

    TimeSeriesDisplay

"""
# Import third party libraries
import matplotlib.pyplot as plt
import datetime as dt
import astral
import numpy as np

# Import Local Libs
from . import common
from ..utils import datetime_utils as dt_utils
from ..utils import data_utils


class TimeSeriesDisplay(object):
    """
    A class for handing the display of timeseries of ARM Datasets. The class stores
    the dataset to be plotted.

    Attributes
    ----------
    fields: dict
        The dictionary containing the fields inside the ARM dataset. Each field
        has a key that links to an xarray DataArray object.
    ds: str
        The name of the datastream.
    file_dates: list
        The dates of each file being display
    fig: matplotlib figure handle
        The matplotlib figure handle to display the plots on. Initializing the
        class with this set to None will create a new figure handle. See the
        matplotlib documentation on what keyword arguments are
        available.
    axes: list
        The list of axes handles to each subplot.
    plot_vars: list
        The list of variables being plotted.
    cbs: list
        The list of colorbar handles.

    Parameters
    ----------
    arm_obj: ACT Dataset
        The ACT Dataset to display in the object
    subplot_shape: 1 or 2D tuple
        A tuple representing the number of (rows, columns) for the subplots
        in the display. If this is None, the figure and axes will not
        be initialized.
    **kwargs:
        Keyword arguments passed to plt.subplots.


    Examples
    --------

    To create a TimeSeriesDisplay with 3 rows, simply do:

    .. code-block:: python

        ds = act.read_netcdf(the_file)
        disp = act.plotting.TimeSeriesDisplay(
           ds, subplot_shape=(3,), figsize=(15,5))

    The TimeSeriesDisplay constructor takes in the same keyword arguments as
    plt.subplots. For more information on the plt.subplots keyword arguments,
    see the `matplotlib documentation
    <https://matplotlib.org/api/_as_gen/matplotlib.pyplot.subplots.html>`_.
    If no subplot_shape is provided, then no figure or axis will be created
    until add_subplots or plots is called.

    """

    def __init__(self, arm_obj, subplot_shape=None, **kwargs):
        self._arm = arm_obj
        self.fields = arm_obj.variables
        self.ds = str(arm_obj.act.datastream)
        if self.ds is None:
            self.ds = str(arm_obj._arm.act._obj.act.datastream)
        self.file_dates = arm_obj.act.file_dates
        self.fig = None
        self.axes = None
        self.plot_vars = []
        self.cbs = []
        if subplot_shape is not None:
            self.add_subplots(subplot_shape, **kwargs)

    def add_subplots(self, subplot_shape=(1, ), **kwargs):
        """
        Adds subplots to the display object. The current
        figure in the object will be deleted and overwritten.

        Parameters
        ----------
        subplot_shape: 1 or 2D tuple, list, or array
            The structure of the subplots in (rows, cols).
        **kwargs: keyword arguments
            Any other keyword arguments that will be passed
            into matplotlib.pyplot.subplots. See the matplotlib
            documentation for further details on what keyword
            arguments are available.
        """

        if self.fig is not None:
            del self.fig

        if len(subplot_shape) == 2:
            fig, ax = plt.subplots(
                subplot_shape[0], subplot_shape[1], **kwargs)
        elif len(subplot_shape) == 1:
            fig, ax = plt.subplots(
                subplot_shape[0], 1, **kwargs)
            if(subplot_shape[0] == 1):
                ax = np.array([ax])
        else:
            raise ValueError(("subplot_shape must be a 1 or 2 dimensional tuple" +
                              "list, or array!"))

        self.fig = fig
        self.axes = ax

    def day_night_background(self, subplot_index=(0, )):
        """
        Colorcodes the background according to sunrise/sunset

        Parameters
        ----------
        subplot_index: 1 or 2D tuple, list, or array
            The index to the subplot to place the day and night background in.

        """
        # Get File Dates
        file_dates = self._arm.act.file_dates
        if len(file_dates) == 0:
            sdate = dt_utils.numpy_to_arm_date(self._arm.time.values[0])
            edate = dt_utils.numpy_to_arm_date(self._arm.time.values[-1])
            file_dates = [sdate, edate]

        all_dates = dt_utils.dates_between(file_dates[0], file_dates[-1])

        if self.axes is None:
            raise RuntimeError("day_night_background requires the plot to be displayed.")

        ax = self.axes[subplot_index]

        # initialize the plot to a gray background for total darkness
        rect = ax.patch
        rect.set_facecolor('0.85')

        # Initiate Astral Instance
        a = astral.Astral()
        if self._arm.lat.data.size > 1:
            lat = self._arm.lat.data[0]
            lon = self._arm.lon.data[0]
        else:
            lat = float(self._arm.lat.data)
            lon = float(self._arm.lon.data)

        for f in all_dates:
            sun = a.sun_utc(f, lat, lon)
            # add yellow background for specified time period
            ax.axvspan(sun['sunrise'], sun['sunset'], facecolor='#FFFFCC')

            # add local solar noon line
            ax.axvline(x=sun['noon'], linestyle='--', color='y')

    def set_xrng(self, xrng, subplot_index=(0, )):
        """
        Sets the x range of the plot.

        Parameters
        ----------
        xrng: 2 number array
            The x limits of the plot.
        subplot_index: 1 or 2D tuple, list, or array
            The index of the subplot to set the x range of.

        """
        if self.axes is None:
            raise RuntimeError("set_xrng requires the plot to be displayed.")

        if not hasattr(self, 'xrng') and len(self.axes.shape) == 2:
            self.xrng = np.zeros((self.axes.shape[0], self.axes.shape[1], 2), dtype='datetime64[D]')
        elif not hasattr(self, 'xrng') and len(self.axes.shape) == 1:
            self.xrng = np.zeros((self.axes.shape[0], 2), dtype='datetime64[D]')

        self.axes[subplot_index].set_xlim(xrng)
        self.xrng[subplot_index, :] = np.array(xrng, dtype='datetime64[D]')

    def set_yrng(self, yrng, subplot_index=(0, )):
        """
        Sets the y range of the plot.

        Parameters
        ----------
        yrng: 2 number array
            The y limits of the plot.
        subplot_index: 1 or 2D tuple, list, or array
            The index of the subplot to set the x range of.

        """
        if self.axes is None:
            raise RuntimeError("set_yrng requires the plot to be displayed.")

        if not hasattr(self, 'yrng') and len(self.axes.shape) == 2:
            self.yrng = np.zeros((self.axes.shape[0], self.axes.shape[1], 2))
        elif not hasattr(self, 'yrng') and len(self.axes.shape) == 1:
            self.yrng = np.zeros((self.axes.shape[0], 2))

        self.axes[subplot_index].set_ylim(yrng)
        self.yrng[subplot_index, :] = yrng

    def add_colorbar(self, mappable, title=None, subplot_index=(0, )):
        """
        Adds a colorbar to the plot

        Parameters
        ----------
        mappable: matplotlib mappable
            The mappable to base the colorbar on.
        title: str
            The title of the colorbar. Set to None to have no title.
        subplot_index: 1 or 2D tuple, list, or array
            The index of the subplot to set the x range of.

        Returns
        -------
        cbar: matplotlib colorbar handle
            The handle to the matplotlib colorbar.
        """
        if self.axes is None:
            raise RuntimeError("add_colorbar requires the plot to be displayed.")

        fig = self.fig
        ax = self.axes[subplot_index]

        # Give the colorbar it's own axis so the 2D plots line up with 1D
        box = ax.get_position()
        pad, width = 0.01, 0.01
        cax = fig.add_axes([box.xmax + pad, box.ymin, width, box.height])
        cbar = plt.colorbar(mappable, cax=cax)
        cbar.ax.set_ylabel(title, rotation=270, fontsize=8, labelpad=3)
        cbar.ax.tick_params(labelsize=6)
        self.cbs.append(cbar)

        return cbar

    def plot(self, field, subplot_index=(0, ),
             line_color='k', cmap=None, cbmin=None, cbmax=None, set_title=None,
             add_nan=False, **kwargs):
        """
        Makes a timeseries plot. If subplots have not been added yet, an axis will
        be created assuming that there is only going to be one plot.

        Parameters
        ----------
        mappable: matplotlib mappable
            The mappable to base the colorbar on.
        title: str
            The title of the colorbar. Set to None to have no title.
        subplot_index: 1 or 2D tuple, list, or array
            The index of the subplot to set the x range of.
        cmap: matplotlib colormap
            The colormap to use/
        line_color: str
            The color of the line.
        cbmin: float
            The minimum for the colorbar.
        cbmax: float
            The maximum for the colorbar.
        set_title: str
            The title for the plot.
        add_nan: bool
            Set to True to fill in data gaps with NaNs.
        kwargs: dict
            The keyword arguments for plt.plot
        """

        # Get data and dimensions
        data = self._arm[field]
        dim = list(self._arm[field].dims)
        xdata = self._arm[dim[0]]
        ytitle = ''.join(['(', data.attrs['units'], ')'])
        if len(dim) > 1:
            ydata = self._arm[dim[1]]
            units = ytitle
            ytitle = ''.join(['(', ydata.attrs['units'], ')'])
        else:
            ydata = None

        # Get the current plotting axis, add day/night background and plot data
        if self.fig is None:
            self.fig = plt.figure()

        if self.axes is None:
            self.axes = np.array([plt.axes()])
            self.fig.add_axes(self.axes[0])

        ax = self.axes[subplot_index]

        if ydata is None:
            self.day_night_background(subplot_index)
            ax.plot(xdata, data, '.', color=line_color)
        else:
            # Add in nans to ensure the data are not streaking
            if add_nan is True:
                xdata, data = data_utils.add_in_nan(xdata, data)
            mesh = ax.pcolormesh(xdata, ydata, data.transpose(),
                                 cmap=cmap, vmax=cbmax,
                                 vmin=cbmin, edgecolors='face')

        # Set Title
        if set_title is None:
            set_title = ' '.join([self.ds, field, 'on',
                                 dt_utils.numpy_to_arm_date(self._arm.time.values[0])])

        ax.set_title(set_title)

        # Set YTitle
        ax.set_ylabel(ytitle)

        # Set X Limit - We want the same time axes for all subplots
        if not hasattr(self, 'time_rng'):
            self.time_rng = [xdata.min().values, xdata.max().values]

        self.set_xrng(self.time_rng, subplot_index)

        # Set Y Limit
        if hasattr(self, 'yrng'):
            # Make sure that the yrng is not just the default
            if not self.yrng[subplot_index] == np.zeros(2):
                self.set_yrng(self.yrng[subplot_index], subplot_index)
            else:
                yrng = [ydata.min().values, ydata.max().values]
                self.set_yrng(yrng, subplot_index)

        # Set X Format
        if len(subplot_index) == 1:
            days = (self.xrng[subplot_index, 1] - self.xrng[subplot_index, 0]) / np.timedelta64(1, 'D')
        else:
            days = (self.xrng[subplot_index[0], subplot_index[1], 1] -
                    self.xrng[subplot_index[0], subplot_index[1], 0]) / np.timedelta64(1, 'D')

        myFmt = common.get_date_format(days)
        ax.xaxis.set_major_formatter(myFmt)

        if ydata is not None:
            self.add_colorbar(mesh, title=units, subplot_index=subplot_index)
