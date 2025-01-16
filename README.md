![License](https://img.shields.io/badge/license-CC0_1.0-blue.svg)
![Krita Version](https://img.shields.io/badge/krita-5.2.6-green.svg)
![Version](https://img.shields.io/badge/version-v0.1.3-orange.svg)

# Krita "Tile Grid" Plugin

**Tile Grid** lets you create a regular set of guides defining *"tiles"* (or *"cells"*) with customizable dimensions, aspect ratios, and spacing.
This tool is ideal for designing basic **tilesets**, **photoboards**, **storyboard or comic page layouts**, or even **single frames with user-defined margins**.

*Tested in Krita 5.2.6*

## Installation

1. Download the plugin: Click on the big green <kbd><> Code</kbd> button, then click on <kbd>Download ZIP</kbd> (or just click [here](https://github.com/madjyc/Krita_Tile_Grid_Plugin/archive/refs/heads/main.zip)).

2. Install the plugin in Krita (as a ZIP file, don't extract it yourself!): Start Krita, go to the menu `Tools` > `Scripts` > `Import Python Plugin from File...`, locate the plugin (ZIP file) and press <kbd>OK</kbd>. A popup will ask you if you want to enable the plugin. Click on <kbd>Yes</kbd>, then **restart Krita**.

You can now use the plugin by clicking on the menu `Tools` > `Scripts` > `Tile Grid`.

*If needed, you'll find more information on how to install Krita python plugins [here](https://docs.krita.org/en/user_manual/python_scripting/install_custom_python_plugin.html)*.

## How to use the plugin

Very simple:

- Specify the **`margins`** you want for the grid;
- Specify the **`spacing`** (*"gutters"*) between tiles;
- Specify the desired number of **`columns`** and **`rows`** of tiles;

Entering the above values automatically calculates the optimal tile format ratio (i.e. width/height). If you need a specific tile format ratio:

- Specify the **`format ratio`** for the tiles.

This tells the plugin to consider the spacing between tiles as a hint (i.e. **minimum** spacing). The actual spacing will be automatically calculated to preserve the specified format ratio.

You're done! The plugin will automatically calculate the size of the tiles based on the canvas size and create guides accordingly.

Oh and you can save your settings as a **`preset`** and restore them later.

Feel free to contact me on [Krita Artists](https://krita-artists.org/). There is a [thread dedicated to the Tile Grid plugin](https://krita-artists.org/t/tile-grid-a-plugin-for-creating-customizable-guide-layouts-for-storyboards-tilesets-and-more/) in the forum.

#### Hope you enjoy this plugin!
