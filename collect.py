from psychopy import visual,event,core,colors
import glob
import re
import csv
import numpy as np

# Parameters
imgs_in = 'imgs_printed' # images we want participant to copy
imgs_out = 'imgs_handwritten' # folder to store drawn images
stks_out = 'strokes_handwritten' # folder to store trajectory data
width = 500 # width of window
height = width*2
key_continue = 'space' # key to press to continue
key_undo = 'backspace' # key to press to undo last stroke
lw = 4.0 # line width

# Geometry to grab canvas frame from screen shot
xborder = width/4
yborder = (height/2)/4
window_grab = (xborder, (height/2)+yborder, width-xborder, height-yborder)

def run():
    # collect drawing of each image in directory
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

def draw_strokes(drawlist):
    # render strokes to screen
    for stroke in drawlist:
        if len(stroke.vertices.shape)>1: # if we have more than one vertex
            stroke.draw()

def get_strokes(drawlist,center,xscale,yscale):
    # return stroke as list of trajectories
    #   center: center of current bounding box
    #   xscale: multiply by this to have range of bounding box be 1
    #   yscale: multiply by this to have range of bounding box be 1
    # 
    #   Normalizes such that canvas coordinates are [-0.5,0.5] in both dimensions
    strokes = []
    for item in drawlist:
        if len(item.vertices.shape)==1:
            stk = [item.vertices.tolist()]
        else:
            stk = item.vertices.tolist()

        for idx,_ in enumerate(stk):
            stk[idx][0] -= center[0]
            stk[idx][1] -= center[1]
            stk[idx][0] /= xscale
            stk[idx][1] /= yscale

        strokes.append(stk)
    return strokes

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
    w = visual.Window([width,height],winType='pyglet')
    m = event.Mouse(win=w)    
    tick = core.Clock()

    # initialize variables
    drawlist = []
    timelist = []
    mousedown = False
    tick.reset()

    # Load display image
    im = visual.SimpleImageStim(w,filename,pos=(0,0.5))
    im.setAutoDraw(True)
    im.autoLog=False

    # Load canvas
    cwidth = 1
    cheight = 0.5
    cpos = (0,-0.5)
    canvas = visual.Rect(w,pos=cpos,width=cwidth,height=cheight,fillColor='white')
    
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
    
    while tick.getTime() < float('Inf'):
        
         canvas.draw()
         draw_strokes(drawlist)
         w.flip()

         pos = m.getPos().tolist()
         tt = int(tick.getTime()*1000) # time in milliseconds
         if not canvas.contains(pos):
            # if we move off the canvas
             mousedown = False
         elif m.getPressed()[0]==1:
             # if the mouse is down, determine if JUST pressed, or still pressed
             if mousedown == False:
                 # start a new drawing phase (and change colors)
                 mousedown = True
                 drawlist.append(visual.ShapeStim(w,lineWidth=lw,lineColor='black',fillColor=None,closeShape=False))
                 drawlist[-1].setVertices(pos)
                 timelist.append([tt])
             else:
                 # continue last drawing phase
                 if len(drawlist[-1].vertices.shape)==1:
                     # only one vertex thus far (vertices is 1D)
                     drawlist[-1].setVertices([drawlist[-1].vertices.tolist()]+[pos])
                 else:
                     # more than one vertex (vertices is 2D)
                     drawlist[-1].setVertices(drawlist[-1].vertices.tolist()+[pos])
                 timelist[-1].append(tt)
         elif m.getPressed()[0]==0:
             # if the mouse is up, reset and wait for new drawing phase
             mousedown = False
         if event.getKeys(keyList=key_continue):
             # if space is pressed, the object is done
             break
         if event.getKeys(keyList=key_undo):
             # if undo key is pressed, delete the last stroke
             mousedown = False
             del drawlist[-1]
             del timelist[-1]
    
    # make image         
    canvas.draw()
    draw_strokes(drawlist)
    IMG = w.getMovieFrame(buffer='back')    
    IMG = IMG.crop(window_grab)
    IMG.save(fout_img)
    
    #w.saveMovieFrames(fout_img)

    # print time course to text file
    strokes = get_strokes(drawlist,center,xscale,yscale)
    for i,stk in enumerate(strokes):
        for j,pt in enumerate(stk):
            pt.append(timelist[i][j]) # add timestamp
    with open(fout_stk,"wb") as f:
        writer = csv.writer(f)
        writer.writerows(strokes)

    w.close()

if __name__ == "__main__":
    run()