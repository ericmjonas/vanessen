import matplotlib
matplotlib.use('Agg')
from matplotlib import pylab
import matplotlib.patches as patches
import numpy as np


import lxml.etree

from lxml import objectify

fig = pylab.figure(figsize=(6, 8), frameon=False)
ax = fig.add_subplot(1, 1, 1)
ax.set_axis_off()



xmlstr = open('Primate Visual System.xml', 'r').read()

region_id_to_pos = {}
region_with_subregions = {}

tree = lxml.etree.fromstring(xmlstr)
for region in tree.xpath('/Neuroptikon/Network/Region'):
    
    abbrev = region.find("Abbreviation").text
    id =  int(region.attrib['id'])
    geometry =  tree.xpath("/Neuroptikon/DisplayWindow/Display/Visible[@objectId='{}']/Geometry".format(id))[0]
    x = float(geometry.find('Position').attrib['x'])
    y = float(geometry.find('Position').attrib['y'])

    region_id_to_pos[id] = (x, y)

    size_x = float(geometry.find('Size').attrib['x'])
    size_y = float(geometry.find('Size').attrib['y'])
    
    # are there subregions
    subregions = [] 
    for r in region.findall('Region'):
        sub_id = int(r.attrib['id'])
        sub_abbrev = r.find('Abbreviation').text

        subregions.append((sub_id, sub_abbrev))
    xc = x # - size_x/2
    yc = y # - size_y/2
    if len(subregions) == 0:
        ax.text(xc, yc, abbrev, fontsize=7, 
                va='center', ha='center', 
                zorder=2)
    if len(subregions) > 0:
        spacing = (size_x / len(subregions))
        subregion_text_centers = np.arange(len(subregions))* spacing
        subregion_text_centers -= size_x/2.0
        subregion_text_centers += xc + spacing/2.0
        for (sub_id, sub_abbrev), sub_x in zip(subregions, subregion_text_centers):
            print "plotting", id, sub_id, sub_abbrev, sub_x

            ax.text(sub_x, yc, sub_abbrev, fontsize=6, 
                    va='center', ha='center', 
                    zorder=2)
            
            region_id_to_pos[sub_id] = sub_x, yc        

    ax.add_patch(
        patches.Rectangle(
            (xc - size_x/2, yc - size_y/2), 
            size_x,          # width
            size_y,          # height
            facecolor='w', 
            edgecolor='k', 
            zorder=1, 
        )
    )


    
# pathways

for pathway in tree.xpath('/Neuroptikon/Network/Pathway'):
    
    region1Id = int(pathway.attrib['region1Id'])
    region2Id = int(pathway.attrib['region2Id'])
    
    ## skip if they are sub-regions -- worry about that later
    if (region1Id not in region_id_to_pos ) or (region2Id not in region_id_to_pos):
        continue
    region1_xy = region_id_to_pos[region1Id]

    region2_xy = region_id_to_pos[region2Id]
    
    # try adding those locs onto the ends

    id =  pathway.attrib['id']
    visible =  tree.xpath("/Neuroptikon/DisplayWindow/Display/Visible[@objectId='{}']".format(id))[0]
    geometry =  visible.find('Geometry')
    x = geometry.find('Position').attrib['x']
    y = geometry.find('Position').attrib['y']
    #pylab.scatter([x], [y], c='k', s=50)

    path =  visible.find('Path')
    path_points = [region1_xy]
    for a in path:
        path_points.append([float(a.attrib['x']), float(a.attrib['y'])])
    path_points.append(region2_xy)
    path_points = np.array(path_points)
    
    ax.plot(path_points[:, 0], path_points[:, 1], zorder=-1) # , c='k')



ax.set_xlim(-0.4, 0.4)
ax.set_ylim(-0.77, 0.05)
fig.tight_layout()
fig.savefig("primate.pdf")
fig.savefig("primate.png")

