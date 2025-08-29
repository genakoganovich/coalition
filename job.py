# Simulate a job ending in error
import time, sys

for i in range(1000) :
	print("P:"+str(i/1000.0))
	sys.stdout.flush()
	time.sleep (0.01)

sys.exit (0)
