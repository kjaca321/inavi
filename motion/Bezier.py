import numpy as np

class Bezier:
  def __init__(self, control, target):
    # assign control and target points from parameters
    self.control = control
    self.target = target

  def get(self, t):
    # make sure input parameter is valid
    if t < 0 or t > 1:
      raise Exception("t not in [0,1]")
    
    # assign control/target point to new variables
    x1, y1 = self.control[0], self.control[1]
    x2, y2 = self.target[0], self.target[1]

    # calculate (x,y) position at input parameter from quadratic Bezier equation
    xt = 2*(1-t)*t*x1 + t*t*x2
    yt = 2*(1-t)*t*y1 + t*t*y2

    return (xt, yt)

  def array(self):
    # initialize lists to store partial sums of distance along the curve, and uniform resulting points
    lengths, spline = [], []

    # initialize cumulative distance, density to match motion profile density
    total_dist, density = 0, 0.0102
    
    # for every input on [0,1]
    t = density
    while t <= 1:
      # retrieve previous and current points at input t
      prev = self.get(t - density)
      curr = self.get(t)

      # calculate distance between the previous and current points
      d = np.sqrt((prev[0]-curr[0]) ** 2 + (prev[1]-curr[1]) ** 2)

      #append partial sum of distance to lengths list
      lengths.append(total_dist)

      #increment total distance and input parameter
      total_dist += d
      t += density
    
    # calculate total number of points on the curve as the reciprocal of point density
    num_pts = int(1/density)

    # for each input in [0,1]
    u, mapped_t = 0, 0
    while u <= 1:
      # calculate current length from input parameter and total distance
      targ_len = u * lengths[num_pts - 1]

      # binary search to find the index corresponding to the target length
      low, high, idx = 0, num_pts, 0
      while low <= high:
        idx = ((high + low) // 2)
        if lengths[idx] < targ_len:
          low = idx + 1
        elif lengths[idx] > targ_len:
          high = idx - 1
        else:
           break
        
      # adjust index if needed  
      if lengths[idx] > targ_len:
        idx -= 1
      
      # create mapped t value from the result of the binary search
      prev_len = lengths[idx]
      if prev_len == targ_len:
        mapped_t = idx / num_pts
      else:
        mapped_t = (idx + (targ_len - prev_len) / (lengths[idx+1] - prev_len)) / num_pts
      
      # add point corresponding to mapped t value to final list, increment input parameter
      spline.append(self.get(mapped_t))
      u += density
    
    # add last point on the curve
    spline.append(self.target)
    return spline
