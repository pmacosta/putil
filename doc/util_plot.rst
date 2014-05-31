util_plot module
================



This is a library that can be used to create high-quality, presentation-ready X-Y graphs quickly and easily.

The properties of the graph (figure in Matplotlib parlance) are defined in an an object of the :py:class:`util_plot.Figure()` class.

Each figure can have one or more panels, whose properties are defined by object(s) of the :py:class:`util_plot.Panel()` class. Panels are arranged vertically in the figure and share the same independent axis. The independent axis of the figure is the union of the independent axis of all the panels, and is shown in the bottom-most panel.

Each panel can have one or more data series, whose properties are defined by objects of the :py:class:`util_plot.Series()` class. The series can be associated with either the primary or secondary dependent axis of the panel. The primary and secondary dependent axis of the panel are the union of the primary and secondary dependent axis of the series associated with each axis. The primary axis is shown on the left of the panel and the secondary axis is shown on the right of the panel.

The data for a series is defined by a source. Two data sources are provided: the :py:class:`util_plot.BasicSource()` class provides basic data validation and minimum/maximum independent variable range bounding. The :py:class:`util_plot.CsvSource()` class builds upon the functionality of the  :py:class:`util_plot.BasicSource()` class and offers a simple way of accessing data from a comma-separated (CSV) file. Other data sources can be programmed (and may optionally inherit from the :py:class:`util_plot.BasicSource()` class) and used as long as the source objects have two attributes, *indep_var* and *dep_var*, that contain an increasing real Numpy vector and a real Numpy vector respectively. 

Example
-------

.. literalinclude:: ./examples/example_util_plot.py
    :language: python
    :linenos:
    :tab-width: 3
    :lines: 5-76

|

.. csv-table:: data.csv file
   :file: ./examples/data.csv
   :header-rows: 1

|

.. image:: ./examples/util_plot_example.png

Application programming interface (API)
---------------------------------------

.. automodule:: util_plot
    :members:
    :undoc-members:
    :show-inheritance:
