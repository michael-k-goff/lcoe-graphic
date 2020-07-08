# Box and Whisker plot portraying cost of electricity

The purpose of this project is to redesign the levelized cost of electricity (LCOE) plot for [Urban Cruise Ship](http://urbancruiseship.org/). It can be seen in context in our overview of [energy production](http://urbancruiseship.org/solution/energy/production).

The levelized cost of electricity is the long-term price that a power plant needs to receive for electricity to be profitable. The measure of LCOE depends on the choice of discount rate, how a power market handles ancillary services, how environmental externalities are priced, and a variety of other factors. Additional factors that affect a plant's economic performance include climate conditions--particularly for renewable power--cost of labor and materials, a specific plant's design specifications, construction management, and more. Therefore, LCOE is a highly heterogeneous metric. We have collected a wide range of LCOE estimates for common types of power to show both the prevailing cost of a particularly type of power and how heterogeneous costs can be.

## Project Structure

The following files are included.

* `lcoe.py`: the python script that builds the image file.
* `lcoe.csv`: a CSV file with our collection of LCOE estimates. Not all estimates are used in this particular project. See the comments in lcoe.py for details on how this file is used and processed.
* `lcoe.svg`: a scalable vector graphics (SVG) file that is the output of our script.
* `logo.png`: the Urban Cruise Ship logo, which is included on all our graphical output.
* `README.md`: this file.

## Design Considerations

See the documentation in `lcoe.py` for details on project implementation. Here we discuss some general design considerations that are part of the project.

###### Choice of Image Format

SVG is a widely supported image format that has the virtue of being scale-free. Aside from the Urban Cruise Ship logo, which is a raster image, the image is a vector-based graphical format that will not become blurry or pixellated when zoomed in upon. In the long run I would like to convert all of Urban Cruise Ship's graphics to vector formats, but this LCOE plot is the only one as of this writing (July 7, 2020).

###### Grayscale

Our primary client's design philosophy is that color can be distracting and a crutch for poorly organized information, and with very limited exceptions, Urban Cruise Ship avoids the use of color. This is also done for ease of printing.

###### Element Layout

One challenge I faced in designing this image is knowing how to lay out different elements, such as the key image, annotations to the key, the caption, the logo, attribution information in the bottom right corner, and the title. My strategy was to adjust the position and sizes elements until they "looked right". There may be subtle misalignments that I fail to see. It would be nice to have a more systematic method of aligning elements, both to insure design consistency and quality and to allow a more automated image generation process.

###### Display of All LCOE Estimates

The image shows every LCOE estimate that is in the dataset and relevant to what is being portrayed, a nonstandard design decision for a box and whisker plot. This was done at the request of the client. While it does perhaps make the graph feel more cluttered than optimal, it is meant to show a quantity of LCOE estimates in a way that is obscured by only showing outliers.