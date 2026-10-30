"""Finite-difference checks for multi-positive, weighted negatives and normalized heads."""
import sys,unittest
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from contrastive.numpy_models import *
class Gradients(unittest.TestCase):
 def test_projection_gradients(self):
  rng=np.random.default_rng(17);x=rng.normal(size=(3,4));t=rng.normal(size=(6,4));wl=rng.normal(size=(4,2));wt=rng.normal(size=(4,2));y=np.array([[1,1,0,0,0,0],[0,0,1,0,0,0],[0,0,0,1,1,0]],bool);mask=np.ones_like(y);mask[0,5]=False;weights=np.ones_like(y,float);weights[~y]=.4
  for bce in [False,True]:
   loss,gl,gt=projection_loss(x,t,wl,wt,y,mask,weights,bce)
   for param,g in [(wl,gl),(wt,gt)]:
    for i,j in [(0,0),(2,1)]:
     old=param[i,j];eps=1e-6;param[i,j]=old+eps;a=projection_loss(x,t,wl,wt,y,mask,weights,bce)[0];param[i,j]=old-eps;b=projection_loss(x,t,wl,wt,y,mask,weights,bce)[0];param[i,j]=old;self.assertAlmostEqual((a-b)/(2*eps),g[i,j],places=5)
 def test_positive_mask_protects_all_labels(self):
  y=np.array([[1,1,0]],bool)
  with self.assertRaises(AssertionError):contrastive_loss_gradient(np.zeros((1,3)),y,np.array([[1,0,1]],bool),np.ones((1,3)))
 def test_linear_gradient(self):
  rng=np.random.default_rng(3);x=rng.normal(size=(4,3));w=rng.normal(size=(3,2));b=np.zeros(2);y=np.array([[1,0],[0,1],[1,1],[0,0]],float);loss,g,gb=linear_loss(x,y,w,b,.001);old=w[1,0];eps=1e-6;w[1,0]=old+eps;a=linear_loss(x,y,w,b,.001)[0];w[1,0]=old-eps;z=linear_loss(x,y,w,b,.001)[0];w[1,0]=old;self.assertAlmostEqual((a-z)/2/eps,g[1,0],places=6)
if __name__=='__main__':unittest.main()
