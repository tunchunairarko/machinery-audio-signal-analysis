import pyqtgraph as pg
import pyqtgraph.exporters
import numpy as np

images = np.random.random((3,128,128))

imagewindow = pg.image()

for i in xrange(images.shape[0]):
    img = pg.ImageItem(images[i])
    imagewindow.clear()
    imagewindow.addItem(img)
    exporter = pg.exporters.ImageExporter(imagewindow.view)
    exporter.export('image_'+str(i)+'.png')