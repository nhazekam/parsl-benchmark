def compute_mandelbrot(limit):
  xmin = 1
  ymin = 1
  xmax = 640
  ymax = 480
  width = 640
  height = 480
  iterations = 50

  for j in range(height):
    for i in range(width):
      x = xmin + i * (xmax-xmin)/width
      y = ymin + i * (ymax-ymin)/width
      z = x + y
      alpha = 1
      for _ in range(iterations):
        z = z - alpha * ((z ** 2 - 1) / (2*z))
  return 0

if __name__ == "__main__":
  import sys
  limit = 0
  if len(sys.argv) > 1:
    limit = int(sys.argv[0])
  compute_mandelbrot(limit)
