from .basicobject import BasicObject
from ..reprc import dtype, fmt
from ..dlisutils import curves
from .valuetypes import scalar, vector, reverse
from .linkage import *
from .utils import *

import numpy as np
from collections import OrderedDict


class Channel(BasicObject):
    """
    A channel is a sequence of measured or computed samples that are indexed
    against some physical quantity e.g. depth or time. The standard supports
    multi-dimensional samples. Each sample can be a scalar or a n-dimensional
    array. In addition to giving access to the actual curve-data, the Channel
    object contains metadata about the curve.

    All Channels are a part of one, and only one, Frame. The parent Frame can
    be reached directly through :py:attr:`frame`.

    Refer to the :py:func:`curves` to see some examples on how to access the
    curve-data.

    Attributes
    ----------

    long_name : str or Longname
        Descriptive name of the channel.

    reprc : int
        Representation code

    units : str
        Physical units of each element in the channel's sample arrays

    properties : list(str)
        Property indicators that summarizes the characteristics of the
        channel and the processing that have produced it.

    dimension : list(int)
        Dimensions of the samples

    axis : list(Axis)
        Coordinate axes of the samples

    element_limit : list(int)
        The maximum size of the sample dimensions

    source
        The source of the channel. Returns the source object, if any

    frame : Frame
        Frame to which channel belongs to

    See also
    --------

    BasicObject : The basic object that Channel is derived from

    Notes
    -----

    The Channel object reflects the logical record type CHANNEL, defined in
    rp66. CHANNEL records are listed in Appendix A.2 - Logical Record Types and
    described in detail in Chapter 5.5.1 - Static and Frame Data, CHANNEL
    objects.
    """
    attributes = {
        'LONG-NAME'          : scalar,
        'REPRESENTATION-CODE': scalar,
        'UNITS'              : scalar,
        'PROPERTIES'         : vector,
        'DIMENSION'          : reverse,
        'AXIS'               : reverse,
        'ELEMENT-LIMIT'      : reverse,
        'SOURCE'             : scalar,
    }

    linkage = {
        'LONG-NAME' : obname('LONG-NAME'),
        'AXIS'      : obname('AXIS'),
        'SOURCE'    : objref
    }

    def __init__(self, obj = None, name = None, lf=None):
        super().__init__(obj, name = name, type = 'CHANNEL', lf=lf)
        # The numpy data type of the sample array
        self._frame        = None

    @property
    def frame(self):
        return lookup(self, obname('FRAME'), self._frame)

    @property
    def long_name(self):
        return self['LONG-NAME']

    @property
    def reprc(self):
        return self['REPRESENTATION-CODE']

    @property
    def units(self):
        return self['UNITS']

    @property
    def properties(self):
        return self['PROPERTIES']

    @property
    def dimension(self):
        return self['DIMENSION']

    @property
    def axis(self):
        return self['AXIS']

    @property
    def element_limit(self):
        return self['ELEMENT-LIMIT']

    @property
    def source(self):
        return self['SOURCE']

    @property
    def dtype(self):
        """dtype

        data-type of each sample in the channel's sample array. The dtype-label
        is *channel.name.id*.

        Returns
        -------

        dtype : np.dtype
        """
        if self.dimension == [1]:
            return np.dtype(dtype[self.reprc])
        else:
            return np.dtype((dtype[self.reprc], tuple(self.dimension)))

    def fmtstr(self):
        """Generate format-string for Channel

        The format-string is mainly intended for internal use.

        Returns
        -------

        fmtstr : str
        """
        if not self.dimension:
            msg = "channel.dimension is invalid for {} (was: {})"
            raise ValueError(msg.format(self, self.dimension))
        samples = np.prod(np.array(self.dimension))
        reprc = fmt[self.reprc]
        fmtstr = samples * reprc

        return fmtstr

    def curves(self):
        """
        Returns a numpy ndarray with the curves-values.

        Notes
        -----

        This method should only be used if there is only *one* channel of
        interest in a particular frame.

        Due to the memory-layout of dlis-files, reading a single channel from
        disk and reading the entire frame is almost equally fast. That means
        reading channels from the same frame one-by-one with this method is
        _way_ slower than reading the entire frame with :func:`Frame.curves()`
        and then indexing on the channels-of-interest.

        Examples
        --------

        Read the full curve

        >>> curve = channel.curves()
        >>> curve
        array([1.1, 2.2, 3.3, 4.4])

        The returned array supports common slicing operations

        >>> curve[::2]
        array([1.1, 3.3])

        Read the full curve from a multidimensional channel

        >>> curve = multichannel.curves()
        >>> curve
        array([[[  1,  2,  3],
                [  4,  5,  6]],
               [[  7,  8,  9],
                [ 10, 11,  12]]])

        This curve has two samples, that both are of size 2x3. From the 1st
        sample, read the element located in the 2nd row, 3rd column

        >>> curve[0][1][2]
        6

        See also
        --------

        Frame.curves() : Read all the curves in a Frame in one go

        Returns
        -------
        curves : np.ndarray
        """
        return np.copy(self.frame.curves()[self.name])

    def describe_attr(self, buf, width, indent, exclude):
        describe_description(buf, self.long_name, width, indent, exclude)

        d = OrderedDict()
        d['Physical unit of sample']   = self.units
        d['Sample dimensions']         = self.dimension
        d['Axis']                      = self.axis
        d['Maximum sample dimensions'] = self.element_limit
        d['Property indicators']       = self.properties
        d['Source']                    = self.source

        describe_dict(buf, d, width, indent, exclude)
