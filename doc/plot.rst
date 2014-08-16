plot module
===========



This is a library that can be used to create high-quality, presentation-ready X-Y graphs quickly and easily.

The properties of the graph (figure in Matplotlib parlance) are defined in an object of the :py:class:`putil.plot.Figure()` class.

Each figure can have one or more panels, whose properties are defined by objects of the :py:class:`putil.plot.Panel()` class. Panels are arranged vertically in the figure and share the same independent axis. The limits of the independent axis of the figure result from the union of the independent data points of all the panels, and is shown by default in the bottom-most panel (it can be configured to be in any panel or panels).

Each panel can have one or more data series, whose properties are defined by objects of the :py:class:`putil.plot.Series()` class. A series can be associated with either the primary or secondary dependent axis of the panel. The limits of the primary and secondary dependent axis of the panel result from the union of the primary and secondary dependent data points of all the series associated with each axis. The primary axis is shown on the left of the panel and the secondary axis is shown on the right of the panel.

The data for a series is defined by a source. Two data sources are provided: the :py:class:`putil.plot.BasicSource()` class provides basic data validation and minimum/maximum independent variable range bounding. The :py:class:`putil.plot.CsvSource()` class builds upon the functionality of the  :py:class:`putil.plot.BasicSource()` class and offers a simple way of accessing data from a comma-separated (CSV) file. Other data sources can be programmed (and may optionally inherit from the :py:class:`putil.plot.BasicSource()` class) and used as long as the source objects have two attributes, *indep_var* and *dep_var*, that contain an increasing real Numpy vector and a real Numpy vector respectively. 

.. figure:: ./support/Class_hierarchy_example.png
   :scale: 100%

   Diagram of the class hierarchy in the putil.plot module

Example
-------

.. literalinclude:: ./support/example_plot.py
    :language: python
    :linenos:
    :tab-width: 3
    :lines: 5-92

|

.. csv-table:: data.csv file
   :file: ./support/data.csv
   :header-rows: 1

|

.. figure:: ./support/example_plot.png
   :scale: 100%

   example_plot.png 

|

Application programming interface (API)
---------------------------------------

.. automodule:: putil.plot
    :members:
    :undoc-members:
    :show-inheritance:
