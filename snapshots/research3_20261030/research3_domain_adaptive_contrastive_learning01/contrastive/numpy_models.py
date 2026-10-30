"""Small trainable heads with analytic gradients, independent of GTE backbone."""
import numpy as np
def normalize(x:np.ndarray)->tuple[np.ndarray,np.ndarray]:
 norm=np.maximum(np.linalg.norm(x,axis=1,keepdims=True),1e-8);return x/norm,norm
def logsumexp(x:np.ndarray)->np.ndarray:
 m=np.max(x,axis=1,keepdims=True);return m+np.log(np.exp(x-m).sum(axis=1,keepdims=True))
def sigmoid(x:np.ndarray)->np.ndarray:return np.exp(-np.logaddexp(0,-x))
def contrastive_loss_gradient(scores:np.ndarray,positives:np.ndarray,mask:np.ndarray,weights:np.ndarray)->tuple[float,np.ndarray]:
 assert (mask[positives]>0).all() and (weights[positives]==1).all() and np.all(positives.sum(1)>0)
 adjusted=np.where(mask,scores+np.log(np.maximum(weights,1e-30)),-1e9);lse=logsumexp(adjusted);p=positives/positives.sum(1,keepdims=True)
 loss=float(np.mean(lse[:,0]-(scores*p).sum(1)));g=(np.exp(adjusted-lse)-p)/len(scores);return loss,g

def balanced_projection_loss(scores:np.ndarray,positives:np.ndarray)->tuple[float,np.ndarray]:
 p=positives/positives.sum(1,keepdims=True);negative=~positives;n=negative/negative.sum(1,keepdims=True)
 loss=float(np.mean(.5*(p*np.logaddexp(0,-scores)+n*np.logaddexp(0,scores)).sum(1)));g=.5*(sigmoid(scores)*(p+n)-p)/len(scores);return loss,g

def linear_loss(x:np.ndarray,y:np.ndarray,w:np.ndarray,b:np.ndarray,l2:float)->tuple[float,np.ndarray,np.ndarray]:
 z=x@w+b;count=y.sum(0);pw=(len(y)-count)/np.maximum(count,1);loss=float(np.mean(pw*y*np.logaddexp(0,-z)+(1-y)*np.logaddexp(0,z))+.5*l2*np.square(w).sum());g=(sigmoid(z)*(pw*y+1-y)-pw*y)/z.size;return loss,x.T@g+l2*w,g.sum(0)

def projection_loss(x:np.ndarray,t:np.ndarray,wl:np.ndarray,wt:np.ndarray,positives:np.ndarray,mask:np.ndarray,weights:np.ndarray,bce:bool=False,tau:float=.1,l2:float=.001)->tuple[float,np.ndarray,np.ndarray]:
 zl,nl=normalize(x@wl);zt,nt=normalize(t@wt);scores=zl@zt.T/tau
 loss,g=balanced_projection_loss(scores,positives) if bce else contrastive_loss_gradient(scores,positives,mask,weights)
 gl=g@zt/tau;gt=g.T@zl/tau;ul=(gl-zl*(gl*zl).sum(1,keepdims=True))/nl;ut=(gt-zt*(gt*zt).sum(1,keepdims=True))/nt
 return loss+.5*l2*float(np.square(wl).sum()+np.square(wt).sum()),x.T@ul+l2*wl,t.T@ut+l2*wt

def project_scores(x:np.ndarray,t:np.ndarray,wl:np.ndarray,wt:np.ndarray)->np.ndarray:
 return normalize(x@wl)[0]@normalize(t@wt)[0].T/.1

class Adam:
 def __init__(self,params:list[np.ndarray],lr:float):
  self.lr=lr;self.step_number=0;self.m=[np.zeros_like(p) for p in params];self.v=[np.zeros_like(p) for p in params]
 def step(self,params:list[np.ndarray],grads:list[np.ndarray])->None:
  self.step_number+=1
  for i,(p,g) in enumerate(zip(params,grads)):
   assert np.isfinite(g).all()
   self.m[i]=.9*self.m[i]+.1*g;self.v[i]=.999*self.v[i]+.001*g*g;p-=self.lr*(self.m[i]/(1-.9**self.step_number))/(np.sqrt(self.v[i]/(1-.999**self.step_number))+1e-8)
   assert np.isfinite(p).all()
