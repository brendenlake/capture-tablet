from psychopy import visual,event,core,colors,tools,monitors
import glob
import re
import csv
import numpy as np
import os
import copy
from PIL import Image

# ----
#
# Simple drawing app that asks participants to draw a series of images. 
#
# Acknowledgments:
#   Some aspects based on Gary Strangman's example:
#     https://groups.google.com/forum/?fromgroups=#!searchin/psychopy-users/tablet/psychopy-users/Bt1jh45SrQM/BoCLUo3dafIJ
#
# ----

# Parameters
lw = 8.0 # line width of the pen
imgs_in = 'imgs_printed' # images we want participant to copy
imgs_out = 'imgs_handwritten' # folder to store drawn images
stks_out = 'strokes_handwritten' # folder to store trajectory data
width = 500 # width of window in pixels
window_offset = 1050 # how many pixels to offset window from left of screen
key_continue = 'space' # key to press to continue
key_undo = 'backspace' # key to press to undo last stroke
pfill = 0.6 # proportion of canvas that longest dimension of target image should fill

# Create folders if needed
if not os.path.exists(imgs_out): os.makedirs(imgs_out)
if not os.path.exists(stks_out): os.makedirs(stks_out)

# Geometry to grab canvas frame from screen shot
height = width*2 # height of window
xborder = width/4
yborder = (height/2)/4
window_grab = (xborder, (height/2)+yborder, width-xborder, height-yborder)

def run():
    # collect drawing for each image in the selected directory
    username = get_username()
    fns = glob.glob(imgs_in+'/*.png')
    trial_total = len(fns)
    for trial_num,fn in enumerate(fns):
        do_trial(fn,username,trial_num+1,trial_total)

def get_username():
    # determine user name (s#) as increment of the last user name in output folder
    fns = glob.glob(imgs_out+'/*.png')
    if len(fns)==0:
        return 's1'
    myid = []
    for f in fns:
        m = re.match(imgs_out+'/s(\d+).*.png', f, re.M|re.I)
        g = m.groups()
        myid.append(g[0])
    myid = [int(i) for i in myid]
    myid = list(set(myid))
    max_id = max(myid)
    return 's' + str(max_id+1)
            
def get_strokes(D,center,xscale,yscale):
    # return drawing as a list of normalized trajectories
    #   center: center of current bounding box
    #   xscale: multiply by this to have range of bounding box be [-0.5,0.5]
    #   yscale: multiply by this to have range of bounding box be [-0.5,0.5] 
    strokes = []
    for s in D.strokes:
        stk = s.get_traj()
        for idx,_ in enumerate(stk):
            stk[idx][0] -= center[0]
            stk[idx][1] -= center[1]
            stk[idx][0] /= xscale
            stk[idx][1] /= yscale
        strokes.append(stk)
    return strokes

class Drawing:

    def __init__(self,w,canvas):
        self.w = w # window
        self.canvas = canvas # white drawing box element
        self.strokes = [] # set of strokes that make a drawing
        self.cache_image = [] # cache drawn canvas for quick rendering
        self.nrerender = 80 # only render this many time points on canvas from scratch before caching
        self.ncount = 0 # number of time points since we cached the canvas
        self.cache()

    def draw(self,from_scratch=False):
        # render drawing on canvas
        if from_scratch:
            self.canvas.draw() # essentially clears back buffer
            for stk in self.strokes:
                stk.draw()
        else:
            if self.cache_image:
                self.cache_image.draw()
            if self.strokes:
                self.strokes[-1].draw(self.nrerender)

    def cache(self):
        # render and store to cache for fast rendering later
        self.draw(from_scratch=True)
        self.cache_image = visual.BufferImageStim(self.w,buffer='back')
        self.ncount = 0        

    def new_stroke(self,pos,timestamp):
        # create a new stroke
        if self.strokes:
            self.cache()
        self.strokes.append(Stroke(self.w))
        self.append(pos,timestamp)
        self.ncount += 1

    def append(self,pos,timestamp):
        # add the next mouse step
        self.strokes[-1].append(pos,timestamp)
        self.ncount += 1
        if self.ncount > self.nrerender:
            self.cache()

    def undo(self):
        # remove last stroke
        if self.strokes:
            del self.strokes[-1]
        self.cache()

class Stroke:

    def __init__(self,w):
        self.w = w # window
        self.T = visual.ShapeStim(self.w,lineWidth=lw,lineColor='black',fillColor=None,closeShape=False) # trajectory
        self.isempty = True # if we have no strokes yet
        self.T.autoLog = False # 
        self.rounded_corners = [] # rounded corners for trajectory stored as sequence of circles
        self.time = [] # series of time stamps for each mouse capture
        
        # compute radius of rounded corner circles
        pixOverNorm = tools.monitorunittools.convertToPix(np.array([1,1]), pos = (0,0), units='norm', win=self.w)
        normOverPix = (1 / float(pixOverNorm[0]), 1 / float(pixOverNorm[1]))
        self.radius = ((lw/2.0)*normOverPix[0],(lw/2.0)*normOverPix[1]) # radius of pen dots

    def singleton(self):
        # return 'True' if we have just one mouse capture
        return len(self.T.vertices.shape) <= 1

    def get_traj(self):
        # get trajectory as a list of [x,y,t] points
        if self.singleton():
            vlist = [self.T.vertices.tolist()]
        else:
            vlist = self.T.vertices.tolist()
        for i in range(len(vlist)): # add time data
            vlist[i] = vlist[i] + [self.time[i]]
        return vlist
        
    def append(self,pos,timestamp):
        # add a new mouse capture
        if self.isempty:
            self.T.setVertices(pos)
            self.isempty = False
        elif self.singleton():
            self.T.setVertices([self.T.vertices.tolist()]+[pos])
        else:
            self.T.setVertices(self.T.vertices.tolist()+[pos])
        C = visual.Circle(self.w,radius=self.radius, pos=pos, fillColor='black',lineColor='black',lineWidth=0)
        C.autoLog = False
        self.rounded_corners.append(C)
        self.time.append(timestamp)

    def draw(self,only_recent=[]):
        # first draw rounded edges then draw straight line skeleton
        #   only_recent: render only the m most recent time points
        if only_recent:
            for C in self.rounded_corners[-only_recent:]:
                C.draw()
        else:
            for C in self.rounded_corners:
                C.draw()
        if not self.singleton():
            self.T.draw()

def do_trial(filename,username,trial_num,trial_total):
    # file to load
    # username : unique id 
    # trial_num : trial number
    # trial_total : total number of trials

    # parse the filename
    m = re.match(imgs_in+'/(.*).png', filename, re.M|re.I)
    g = m.groups()
    base = g[0]
    fout_img = imgs_out+'/'+username+'_'+base+'.png'
    fout_stk = stks_out+'/'+username+'_'+base+'.csv'

    # create a window, a mouse monitor and a clock    
    w = visual.Window([width,height],pos=[window_offset,0],winType='pyglet')
    m = event.Mouse(win=w)    
    tick = core.Clock()

    # initialize variables
    drawlist = []
    timelist = []
    mousedown = False
    tick.reset()

    # Load canvas
    cwidth = 1
    cheight = 0.5
    cpos = (0,-0.5)
    canvas = visual.Rect(w,pos=cpos,width=cwidth,height=cheight,fillColor='white')

    # Load display image
    IMG = Image.open(filename)
    currwidth = float(max(IMG.size[0],IMG.size[1]))
    background_width = width / 2.0 # base size of target image
    basewidth = background_width*pfill # proportion of base that target image fills
    wpercent = (basewidth/currwidth)
    wsize = int((float(IMG.size[0])*float(wpercent)))
    hsize = int((float(IMG.size[1])*float(wpercent)))
    IMG = IMG.resize((wsize,hsize), Image.ANTIALIAS)
    sz = (int(background_width),int(background_width))
    PADDING = Image.new('RGB', sz, 'white')
    PADDING.paste(IMG,((sz[0] - IMG.size[0]) / 2, (sz[1] - IMG.size[1]) / 2))
    im = visual.SimpleImageStim(w,PADDING,pos=(0,0.5))
    im.setAutoDraw(True)
    im.autoLog=False
    
    # For rescaling time series
    cverts = canvas.vertices # [top left, top right, bottom right, bottom left]
    v = [np.array(c)+np.array(cpos) for c in cverts]
    xscale = v[1][0]-v[0][0]
    yscale = v[1][1]-v[2][1]
    center = (v[0]+v[2])/2
    txt = "  Please draw this (" + str(trial_num)+ ' of ' +str(trial_total)+').\nPress <space> when done.\nPress <backspace> to undo.'
    t1 = visual.TextStim(w,text=txt,pos=(0,0),color='black',height=0.035)
    t1.setAutoDraw(True)
    t1.autoLog=False
    
    D = Drawing(w,canvas)

    while tick.getTime() < float('Inf'):

        D.draw()
        w.flip()

        # get mouse information
        pos = m.getPos().tolist()
        tt = int(tick.getTime()*1000) # time in milliseconds

        # record
        if not canvas.contains(pos):
            # if we move off the canvas
            mousedown = False
        elif m.getPressed()[0]==1:
            # if the mouse is down, determine if we started a new stroke
            if mousedown == False:                 
                D.new_stroke(pos,tt)
                mousedown = True
            else:
                D.append(pos,tt)
        elif m.getPressed()[0]==0:
            # if the mouse is up, reset and wait for new drawing phase
            mousedown = False

        # special key events
        if event.getKeys(keyList=key_continue) == [key_continue]:
            # if space is pressed, the drawing is done
            break
        if event.getKeys(keyList=key_undo) == [key_undo]:
            # if undo key is pressed, delete the last stroke             
            D.undo()
            mousedown = False
    
    # make image
    D.draw(from_scratch=True)
    IMG = w.getMovieFrame(buffer='back')    
    IMG = IMG.crop(window_grab)
    IMG.save(fout_img)

    # print time course to text file
    traj = get_strokes(D,center,xscale,yscale)
    with open(fout_stk,"wb") as f:
        writer = csv.writer(f)
        writer.writerows(traj)
    w.close()

if __name__ == "__main__":
    run()