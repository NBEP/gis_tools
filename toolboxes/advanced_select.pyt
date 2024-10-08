# -*- coding: utf-8 -*-

import arcpy
import os


class Toolbox:
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Advanced Select"
        self.alias = "adv_select"
        self.description = """
                        This toolbox contains a series of advanced selection tools.

                        MIT License

                        Copyright (c) 2024 Mariel Sorlien, Narragansett Bay Estuary Program

                        Permission is hereby granted, free of charge, to any person obtaining a copy
                        of this software and associated documentation files (the "Software"), to deal
                        in the Software without restriction, including without limitation the rights
                        to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
                        copies of the Software, and to permit persons to whom the Software is
                        furnished to do so, subject to the following conditions:

                        The above copyright notice and this permission notice shall be included in all
                        copies or substantial portions of the Software.

                        THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
                        IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
                        FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
                        AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
                        LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
                        OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
                        SOFTWARE."""

        # List of tool classes associated with this toolbox
        self.tools = [selectInteriorLines, selectOverlap]

class selectInteriorLines(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Select Interior Lines"
        self.description = "Selects all interior lines in a polygon and saves them as a polyline."

    def getParameterInfo(self):
        """Define the tool parameters."""
        params = []

        # Input polygon parameter
        in_features = arcpy.Parameter(
            name="in_features",
            displayName="Input Polygon",
            datatype="DEFeatureClass",
            parameterType="Required", # Required | Optional | Derived
            direction = "Input") # Input | Output
        in_features.filter.list = ["POLYGON"]
        params.append(in_features)

        # Derived output features parameter
        out_features = arcpy.Parameter(
            name="out_features",
            displayName="Output Features",
            datatype="DEFeatureClass",
            parameterType="Required", # Required | Optional | Derived
            direction = "Output") # Input | Output
        out_features.parameterDependencies = [in_features.name]
        out_features.schema.clone = True
        params.append(out_features)

        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        in_features = parameters[0].valueAsText
        out_features = parameters[1].valueAsText

        out_path = os.path.dirname(out_features)
        out_name = os.path.basename(out_features)

        temp_polyline = arcpy.env.scratchFolder + "/temp_polyline.shp"
        temp_polygon = arcpy.env.scratchFolder + "/temp_polygon.shp"

        # Function is based on proposed solution by RyanKDalton at
        # https://gis.stackexchange.com/questions/15583/select-interior-lines-of-a-polygon-to-line-layer#15588
        # site accessed 2022-07-07

        arcpy.AddMessage("Converting polygon to lines")
        #PolygonToLine does not split lines at intersections and creates errors
        arcpy.FeatureToLine_management(
            in_features=in_features,
            out_feature_class=temp_polyline,
            attributes="NO_ATTRIBUTES")

        arcpy.AddMessage("Dissolving polygon")  # Necessary to select exterior lines
        arcpy.Dissolve_management(in_features, temp_polygon)

        arcpy.AddMessage("Selecting interior lines")
        # Find all exterior lines with "SHARE_A_LINE_SEGMENT_WITH", then INVERT to select interior lines
        polyline_select = arcpy.SelectLayerByLocation_management(
            in_layer=temp_polyline,
            overlap_type="SHARE_A_LINE_SEGMENT_WITH",
            select_features=temp_polygon,
            invert_spatial_relationship="INVERT")

        arcpy.AddMessage("Saving output")
        arcpy.FeatureClassToFeatureClass_conversion(
            in_features=polyline_select,
            out_path=out_path,
            out_name=out_name)

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return

class selectOverlap(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Select Overlap"
        self.description = "Selects all features that intersect selection feature, saves as new layer."

    def getParameterInfo(self):
        """Define the tool parameters."""
        params = []

        # Input feature parameter
        in_features = arcpy.Parameter(
            name="in_features",
            displayName="Input Features",
            datatype="DEFeatureClass",
            parameterType="Required", # Required | Optional | Derived
            direction = "Input") # Input | Output
        params.append(in_features)

        # Input select feature parameter
        select_features = arcpy.Parameter(
            name="select_features",
            displayName="Select Features",
            datatype="DEFeatureClass",
            parameterType="Required", # Required | Optional | Derived
            direction = "Input") # Input | Output
        params.append(select_features)

        # Derived output features parameter
        out_features = arcpy.Parameter(
            name="out_features",
            displayName="Output Features",
            datatype="DEFeatureClass",
            parameterType="Required", # Required | Optional | Derived
            direction = "Output") # Input | Output
        out_features.parameterDependencies = [in_features.name]
        out_features.schema.clone = True
        params.append(out_features)

        return params

    def isLicensed(self):
        """Set whether the tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter. This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        in_features = parameters[0].valueAsText
        select_features = parameters[1].valueAsText
        out_features = parameters[2].valueAsText

        polygon_overlap = arcpy.management.SelectLayerByLocation(
            in_layer=in_features,
            select_features=select_features)
        arcpy.management.CopyFeatures(
            in_features=polygon_overlap,
            out_feature_class=out_features)

        return

    def postExecute(self, parameters):
        """This method takes place after outputs are processed and
        added to the display."""
        return
