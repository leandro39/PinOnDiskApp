import timeit
import time

#mysetup = 'import time'
mycode = '''
t1 = time.time()
timestamp = time.strftime('%H:%M:%S', time.gmtime(time.time()-t1))
'''


print(timeit.timeit(mycode))
